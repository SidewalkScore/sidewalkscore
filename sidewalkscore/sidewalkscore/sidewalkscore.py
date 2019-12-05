from collections import OrderedDict
import copy
import json
import os
import sys

import fiona
import fiona.crs
import networkx as nx
import shapely
from shapely.geometry import shape

import unweaver

if shapely.speedups.available:
    shapely.speedups.enable()


def sidewalkscore(networks, street_edge, street_cost_function):
    # conn = networks["pedestrian"]["G"].sqlitegraph.conn
    # indices = list(conn.execute("SELECT * FROM sqlite_master WHERE type = 'index'"))
    # for index in indices:
    #     print(index)
    # Get the midpoint
    # FIXME: json.loads required for entwiner graph, but not networkx?
    if type(street_edge) == "dict":
        json_geometry_st = json.loads(street_edge["_geometry"])
    else:
        json_geometry_st = street_edge["_geometry"]
    geometry_st = shape(json_geometry_st)
    midpoint = geometry_st.interpolate(0.5, normalized=True)
    # Get the associated sidewalks, if applicable
    sidewalk_ids = []
    # FIXME: Why would sw_left exist but not pkey_left?
    if "sw_left" in street_edge and street_edge["pkey_left"] is not None:
        sidewalk_ids.append(street_edge["pkey_left"])
    if "sw_right" in street_edge and street_edge["pkey_right"] is not None:
        sidewalk_ids.append(street_edge["pkey_right"])

    if not sidewalk_ids:
        return {profile["name"]: 0 for profile in networks["pedestrian"]["profiles"]}

    street_candidates = unweaver.network_queries.dwithin.candidates_dwithin(
      networks["street"]["G"], midpoint.x, midpoint.y, 4, is_destination=False, dwithin=5e-4
    )

    street_candidate = unweaver.algorithms.shortest_path._choose_candidate(street_candidates, street_cost_function)
    if street_candidate is None:
        # FIXME: handle this better
        raise Exception("No street candidate!?")

    to_retrieve = set([int(sw_id) for sw_id in sidewalk_ids])
    sidewalks = []
    near_edges = unweaver.network_queries.dwithin.edges_dwithin(networks["pedestrian"]["G"], midpoint.x, midpoint.y, distance=5e-4, sort=True)
    near = list(near_edges)
    for edge in near:
        # FIXME: hard-coded, prevents use of other datasets
        if edge["_layer"] == "sidewalks":
            if edge["pkey"] in to_retrieve:
                sidewalks.append(edge)
                to_retrieve.remove(edge["pkey"])

    # Find reachable paths for all
    sw_distances = {profile["name"]: [] for profile in networks["pedestrian"]["profiles"]}
    sw_candidates_list = []
    for sidewalk in sidewalks:
        sw_geometry = sidewalk["_geometry"]
        sw_midpoint = sw_geometry.interpolate(sw_geometry.project(midpoint))
        sw_candidates = list(unweaver.network_queries.dwithin.candidates_dwithin(networks["pedestrian"]["G"], sw_midpoint.x, sw_midpoint.y, 1, is_destination=False, dwithin=5e-4))
        sw_candidates_list.append(sw_candidates)

    for profile in networks["pedestrian"]["profiles"]:
        name = profile["name"]
        # TODO: calculate dynamic weights if static is not available
        if "static" in profile:
            cost_function = lambda u, v, d: d.get(f"_weight_{name}", None)
        else:
            cost_function = profile["cost_function"]()
        # name, cost_function in cost_functions.items():
        # FIXME: do this in UTM space or otherwise use geography-compatible
        # spatial functions like projection and interpolation.
        distances = []
        for sw_candidates in sw_candidates_list:
            sw_candidate = unweaver.algorithms.shortest_path._choose_candidate(copy.deepcopy(sw_candidates), cost_function)
            if sw_candidate is None:
                # No valid candidate could be identified - falls outside cost fun
                sw_distances[name].append(0)
            else:
                sw_nodes, sw_edges = unweaver.algorithms.reachable.reachable(networks["pedestrian"]["G"], sw_candidate, cost_function, max_cost=400)
                sw_distance = 0
                seen_edges = set([])
                for edge in sw_edges:
                    # TODO: embed ID in all edges? pkey is unique to seattle
                    if "pkey" in edge:
                        if edge["pkey"] not in seen_edges:
                            sw_distance += edge["length"]
                            seen_edges.add(edge["pkey"])
                # sw_distance = sum([edge["length"] for edge in sw_edges])
                sw_distances[name].append(sw_distance)

    sw_total_distances = {name: sum(distances) for name, distances in sw_distances.items()}

    st_nodes, st_edges = unweaver.algorithms.reachable.reachable(networks["street"]["G"], street_candidate, street_cost_function, max_cost=400)
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
    return final_scores

def sidewalkscore_batch(pedestrian_db_directory, street_db_directory, out_file, counter=None):
    # TODO: use multiprocessing - speed up by nx, where n = cores
    networks = {}
    for network_type, directory in zip(["pedestrian", "street"], [pedestrian_db_directory, street_db_directory]):
        G = unweaver.graph.get_graph(directory)

        G.sqlitegraph = G.sqlitegraph.to_in_memory()
        sqlitegraph = G.sqlitegraph
        G = nx.DiGraph(G)
        G.sqlitegraph = sqlitegraph

        profiles = unweaver.parsers.parse_profiles(directory)
        networks[network_type] = {
            "G": G,
            "profiles": profiles,
        }

    # FIXME: standardize expectation over profile combinations. Is it all-by-all
    # comparisons between ped and street? Need a strategy for aligning pedestrian
    # profiles with street profiles. For now, assumes only a single street profile
    street_profile = networks["street"]["profiles"][0]
    # TODO: use precalculated weights
    street_cost_function = street_profile["cost_function"]()

    features = []
    for i, (u, v, street) in enumerate(networks["street"]["G"].edges(data=True)):
    # for i, (u, v, street) in enumerate(networks["street"]["G"].iter_edges()):
        sidewalkscores = sidewalkscore(networks, street, street_cost_function)
        # json_geometry_st = json.loads(street["_geometry"])
        json_geometry_st = street["_geometry"]
        features.append({
            "type": "Feature",
            "geometry": json_geometry_st,
            "properties": {f"sidewalkscore_{name}": score for name, score in sidewalkscores.items()}
        })
        # TODO: add click-independent interface for counter?
        if counter:
            counter.update(1)
        # if i > 200:
        #     raise Exception()

    # TODO: incrementally build sidewalkscore GPKG in temp file, copy over on completion.
    schema = {
        "geometry": "LineString",
        "properties": OrderedDict([
            (f"sidewalkscore_{name}", "float") for name in sorted(sidewalkscores.keys())
        ]),
    }

    crs = fiona.crs.from_epsg(4326)

    with fiona.open(out_file, "w", driver="GPKG", crs=crs, schema=schema) as c:
        for feature in features:
            c.write(feature)
