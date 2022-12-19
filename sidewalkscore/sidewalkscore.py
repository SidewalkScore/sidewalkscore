import copy

import shapely  # type: ignore
from shapely.geometry import shape  # type: ignore

import unweaver

# TODO: put in top-level __init__, as it has global effects?
if shapely.speedups.available:
    shapely.speedups.enable()


def sidewalkscore(G, street_edge, interpolate=0.5):
    # FIXME: standardize expectation over profile combinations. Is it
    # all-by-all comparisons between ped and street? Need a strategy for
    # aligning pedestrian profiles with street profiles. For now, assumes only
    # a single street profile
    geom_key = G.network.edges.geom_column

    # Get the midpoint
    # FIXME: we're calculating more than 1 midpoint per ontological "street",
    # as streets are broken up in OpenSidewalks to connect them to pedestrian
    # edges. We should revisit this part of the function and replace it with
    # a new streets-only graph interpretation.
    geometry_st = shape(street_edge[geom_key])
    # TODO: ensure interpolation happens geodetically - currently introduces
    # errors as it's done in wgs84
    midpoint = geometry_st.interpolate(interpolate, normalized=True)

    street_candidates = unweaver.graph.waypoint_candidates(
        networks.street.G,
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
        profile["id"]: [] for profile in networks.pedestrian.profiles
    }
    sw_candidates_list = []
    for sidewalk in sidewalks:
        sw_geometry = shape(sidewalk[geom_key_ped])
        sw_midpoint = sw_geometry.interpolate(sw_geometry.project(midpoint))
        sw_candidates = list(
            unweaver.graph.waypoint_candidates(
                networks.pedestrian.G,
                sw_midpoint.x,
                sw_midpoint.y,
                1,
                is_destination=False,
                dwithin=5e-4,
            )
        )
        sw_candidates_list.append(sw_candidates)

    for profile in networks.pedestrian.profiles:
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
                    networks.pedestrian.G, sw_candidate
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
        networks.street.G, street_candidate
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
