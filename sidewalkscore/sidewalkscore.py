from collections import OrderedDict
import copy
import json

import fiona
import fiona.crs
import shapely
from shapely.geometry import shape

import unweaver

# TODO: put in top-level __init__, as it has global effects?
if shapely.speedups.available:
    shapely.speedups.enable()


# FIXME: this function is never used? Remove it if so
def street_to_starts(networks, street_edge, interpolate=0.5):
    G_street = networks["street"]["G"]
    G_ped = networks["pedestrian"]["G"]
    street_cost_function = networks["street"]["cost_function"]()

    # Get the associated sidewalks, if applicable
    sidewalk_ids = []

    # FIXME: Why would sw_left exist but not pkey_left?
    if "sw_left" in street_edge and street_edge["pkey_left"] is not None:
        sidewalk_ids.append(street_edge["pkey_left"])
    if "sw_right" in street_edge and street_edge["pkey_right"] is not None:
        sidewalk_ids.append(street_edge["pkey_right"])

    if not sidewalk_ids:
        return None

    # FIXME: json.loads required for entwiner graph, but not networkx?
    if type(street_edge) == "dict":
        json_geometry_st = json.loads(street_edge["_geometry"])
    else:
        json_geometry_st = street_edge["_geometry"]
    geometry_st = shape(json_geometry_st)
    # TODO: ensure interpolation happens geodetically - currently introduces
    # errors as it's done in wgs84
    point_along = geometry_st.interpolate(interpolate, normalized=True)

    street_candidates = unweaver.graph.waypoint_candidates(
        G_street,
        point_along.x,
        point_along.y,
        4,
        is_destination=False,
        dwithin=5e-4,
    )

    street_candidate = unweaver.algorithms.shortest_path._choose_candidate(
        street_candidates, street_cost_function
    )
    if street_candidate is None:
        return None

    to_retrieve = set([int(sw_id) for sw_id in sidewalk_ids])

    # FIXME: formalize strategy (or strategies) for associating sidewalks with
    # streets.
    sidewalk_candidates = []
    near_edges = G_ped.edges_dwithin(
        point_along.x, point_along.y, distance=5e-4, sort=True
    )
    near = list(near_edges)
    for edge in near:
        # FIXME: hard-coded, prevents use of other datasets
        if edge["_layer"] == "sidewalks":
            if edge["pkey"] in to_retrieve:
                sidewalk_candidates.append(edge)
                to_retrieve.remove(edge["pkey"])

    return {
        "street": street_candidate,
        "sidewalks": sidewalk_candidates,
    }


def sidewalkscore(networks, street_edge, interpolate=0.5):
    # FIXME: standardize expectation over profile combinations. Is it
    # all-by-all comparisons between ped and street? Need a strategy for
    # aligning pedestrian profiles with street profiles. For now, assumes only
    # a single street profile
    G_ped = networks["pedestrian"]["G"]
    street_profile = networks["street"]["profiles"][0]
    # TODO: use precalculated weights
    street_cost_function = street_profile["cost_function"]()

    # Get the midpoint
    geometry_st = shape(street_edge["_geometry"])
    # TODO: ensure interpolation happens geodetically - currently introduces
    # errors as it's done in wgs84
    midpoint = geometry_st.interpolate(interpolate, normalized=True)
    # Get the associated sidewalks, if applicable
    sidewalk_ids = []
    # FIXME: Why would sw_left exist but not pkey_left?
    if "sw_left" in street_edge and street_edge["pkey_left"] is not None:
        sidewalk_ids.append(street_edge["pkey_left"])
    if "sw_right" in street_edge and street_edge["pkey_right"] is not None:
        sidewalk_ids.append(street_edge["pkey_right"])

    if not sidewalk_ids:
        return {
            profile["id"]: 0 for profile in networks["pedestrian"]["profiles"]
        }

    street_candidates = unweaver.graph.waypoint_candidates(
        networks["street"]["G"],
        midpoint.x,
        midpoint.y,
        4,
        is_destination=False,
        dwithin=5e-4,
    )

    street_candidate = unweaver.algorithms.shortest_path._choose_candidate(
        street_candidates, street_cost_function
    )
    if street_candidate is None:
        # FIXME: handle this better
        raise Exception("No street candidate!?")

    to_retrieve = set([int(sw_id) for sw_id in sidewalk_ids])
    sidewalks = []
    near_edges = G_ped.edges_dwithin(
        midpoint.x, midpoint.y, distance=5e-4, sort=True
    )
    near = list(near_edges)
    for u, v, d in near:
        # FIXME: hard-coded, prevents use of other datasets
        if d["_layer"] == "sidewalks":
            if d["pkey"] in to_retrieve:
                sidewalks.append(d)
                to_retrieve.remove(d["pkey"])

    # Find reachable paths for all
    sw_distances = {
        profile["id"]: [] for profile in networks["pedestrian"]["profiles"]
    }
    sw_candidates_list = []
    for sidewalk in sidewalks:
        sw_geometry = shape(sidewalk["_geometry"])
        sw_midpoint = sw_geometry.interpolate(sw_geometry.project(midpoint))
        sw_candidates = list(
            unweaver.graph.waypoint_candidates(
                networks["pedestrian"]["G"],
                sw_midpoint.x,
                sw_midpoint.y,
                1,
                is_destination=False,
                dwithin=5e-4,
            )
        )
        sw_candidates_list.append(sw_candidates)

    for profile in networks["pedestrian"]["profiles"]:
        profile_id = profile["id"]
        # TODO: calculate dynamic weights if static is not available
        if "static" in profile:

            def cost_function(u, v, d):
                return d.get("_weight_{profile_id}", None)

        else:
            cost_function = profile["cost_function"]()
        # name, cost_function in cost_functions.items():
        # FIXME: do this in UTM space or otherwise use geography-compatible
        # spatial functions like projection and interpolation.
        for sw_candidates in sw_candidates_list:
            sw_candidate = unweaver.algorithms.shortest_path._choose_candidate(
                copy.deepcopy(sw_candidates), cost_function
            )
            if sw_candidate is None:
                # No valid candidate could be identified - falls outside cost
                # fun
                sw_distances[profile_id].append(0)
            else:
                G_aug = unweaver.augmented.prepare_augmented(
                    networks["pedestrian"]["G"], sw_candidate
                )
                sw_nodes, sw_edges = unweaver.algorithms.reachable.reachable(
                    G_aug, sw_candidate, cost_function, max_cost=400
                )
                sw_distance = 0
                seen_edges = set([])
                for edge in sw_edges:
                    # TODO: embed ID in all edges? pkey is unique to seattle
                    if "pkey" in edge:
                        if edge["pkey"] not in seen_edges:
                            sw_distance += edge["length"]
                            seen_edges.add(edge["pkey"])
                # sw_distance = sum([edge["length"] for edge in sw_edges])
                sw_distances[profile_id].append(sw_distance)

    sw_total_distances = {
        name: sum(distances) for name, distances in sw_distances.items()
    }

    G_aug = unweaver.augmented.prepare_augmented(
        networks["street"]["G"], street_candidate
    )
    st_nodes, st_edges = unweaver.algorithms.reachable.reachable(
        G_aug, street_candidate, street_cost_function, max_cost=400
    )
    st_total_distance = sum([edge["length"] for edge in st_edges])

    final_scores = {}
    for name, total_distance in sw_total_distances.items():
        # Calculate sidewalkscore
        if not st_total_distance:
            # FIXME: consider whether this is a valid conclusion
            final_scores[name] = 0
        else:
            # SidewalkScore is normalized by 2 to account for the fact that we
            # asked for distances on up to 2 sidewalks.
            final_scores[name] = total_distance / 2 / st_total_distance

    # TODO: save and return walksheds as well

    return final_scores


def sidewalkscore_batch(
    pedestrian_db_directory,
    street_db_directory,
    out_file,
    driver="GPKG",
    counter=None,
):
    # TODO: use multiprocessing - speed up by nx, where n = cores
    networks = {}
    for network_type, directory in zip(
        ["pedestrian", "street"],
        [pedestrian_db_directory, street_db_directory],
    ):
        G = unweaver.graph.get_graph(directory)

        G = G.to_in_memory()

        # G.sqlitegraph = G.sqlitegraph.to_in_memory()
        # sqlitegraph = G.sqlitegraph
        # G = nx.DiGraph(G)
        # G.sqlitegraph = sqlitegraph

        profiles = unweaver.parsers.parse_profiles(directory)
        networks[network_type] = {
            "G": G,
            "profiles": profiles,
        }

    features = []
    for i, (u, v, street) in enumerate(
        networks["street"]["G"].edges(data=True)
    ):
        sidewalkscores = sidewalkscore(networks, street)

        properties = {
            k: v for k, v in street.items() if not k.startswith("_weight")
        }
        json_geometry_st = properties.pop("_geometry")

        for name, score in sidewalkscores.items():
            properties[f"sidewalkscore_{name}"] = score

        features.append(
            {
                "type": "Feature",
                "geometry": json_geometry_st,
                "properties": properties,
            }
        )

        # TODO: add click-independent interface for counter?
        if counter:
            counter.update(1)
        # if i > 200:
        #     raise Exception()

    # TODO: incrementally build sidewalkscore GPKG in temp file, copy over on
    #       completion.
    # TODO: write to network database(!)

    street_db = networks["street"]["G"].sqlitegraph
    col_query = list(street_db.execute("PRAGMA table_info('edges')"))
    properties_schema = OrderedDict()
    for row in col_query:
        if row["name"] in ("_u", "_v"):
            # These get stripped from feature properties
            continue
        if row["type"].upper() == "INTEGER":
            properties_schema[row["name"]] = "int"
        elif row["type"].upper() == "REAL":
            properties_schema[row["name"]] = "float"
        elif row["type"].upper() == "TEXT":
            properties_schema[row["name"]] = "str"

    for name in sorted(sidewalkscores.keys()):
        properties_schema[f"sidewalkscore_{name}"] = "float"

    schema = {
        "geometry": "LineString",
        "properties": properties_schema,
    }

    crs = fiona.crs.from_epsg(4326)

    with fiona.open(out_file, "w", driver=driver, crs=crs, schema=schema) as c:
        i = 0
        batch = []
        for feature in features:
            if i < 1000:
                batch.append(feature)
                i += 1
            else:
                c.writerecords(batch)
                i = 0
        c.writerecords(batch)


def sidewalkscore_geometry():
    pass


def sidewalkscore_from_lonlat(lon, lat, networks, dwithin=5e-4):
    G_street = networks["street"]["G"]
    candidates = unweaver.graph.waypoint_candidates(
        G_street, lon, lat, 1, is_destination=False, dwithin=dwithin
    )

    if candidates is None:
        return None

    candidate = next(candidates)

    score = sidewalkscore(networks, candidate)

    return score
