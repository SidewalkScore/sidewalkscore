from dataclasses import dataclass
import json
from typing import Literal, List, Optional, Set, Tuple

import networkx as nx
from shapely.geometry import LineString, Point, shape
from unweaver.graphs import DiGraphGPKG
from unweaver.geojson import LineString as GeoJSONLineString

from sidewalkscore.constants import STREETS

NodeID = str
EdgeID = Tuple[str, str]


@dataclass
class AssociatedStreet:
    street_id: EdgeID
    left_sidewalk_id: Optional[EdgeID]
    right_sidewalk_id: Optional[EdgeID]


class MidpointSegmentError(Exception):
    pass


class NoNearbyStreetError(Exception):
    pass


def _cross(x1, y1, x2, y2):
    return x1 * -y2 + y1 * x2


def line_side_of_line(
    reference_line: LineString, target_line: LineString
) -> Literal["left", "right"]:
    # Get line segment that's in the middle of the reference line
    # TODO: use a more reliable way to calculate this
    # TODO: make use of 'layer' filtering, rule out intersecting lines.
    reference_line_geom = shape(reference_line)
    target_line_geom = shape(target_line)

    midpoint = reference_line_geom.interpolate(distance=0.5, normalized=True)
    reference_segment = None
    traveled = 0.0
    for pt1, pt2 in zip(
        reference_line_geom.coords, reference_line_geom.coords[1:]
    ):
        segment = LineString([pt1, pt2])
        traveled += segment.length
        if traveled > (reference_line_geom.length / 2):
            reference_segment = segment
            break
    if reference_segment is None:
        # Failed to identify the segment
        raise MidpointSegmentError()
    # Get closest point on target line to the midpoint of the reference line
    # segment
    target_distance_along = target_line_geom.project(
        reference_segment.interpolate(distance=0.5, normalized=True)
    )
    target_point = target_line_geom.interpolate(target_distance_along)
    # Use standard left/right calculation of line segment to point
    x1 = reference_segment.coords[1][0] - reference_segment.coords[0][0]
    y1 = reference_segment.coords[1][1] - reference_segment.coords[0][1]
    # FIXME: verify that midpoint is a Point
    x2 = target_point.x - midpoint.x
    y2 = target_point.y - midpoint.y
    if _cross(x1, y1, x2, y2) > 0:
        return "right"
    else:
        # NOTE: parallel vector (i.e. the nearest is 'straight ahead') would be
        # the '0' value and we assign it to 'left'. Perhaps we should be more
        # picky.
        return "left"


def associate_street(
    lon: float,
    lat: float,
    G: DiGraphGPKG,
    street_search_dist: float = 30,
    sidewalk_search_dist: float = 30,
) -> AssociatedStreet:
    """Locate a left/right sidewalk for points on a street, if applicable.
    Search radius distances are in meters."""
    # Identify street within street search distance
    nearby_edges = G.network.edges.dwithin_edges(
        lon, lat, street_search_dist, sort=True
    )
    nearby_streets = (
        d for _, __, d in nearby_edges if d.get("_street", False)
    )
    try:
        street = next(iter(nearby_streets))
    except StopIteration:
        raise NoNearbyStreetError()

    # Select projected point: closest point on street to the lon/lat
    # FIXME: projections should be done in cartesian space, i.e. projected, but
    # this is implemented in lon/lat
    street_geom = shape(street["geom"])
    distance_along = street_geom.project(Point(lon, lat))
    st_point = street_geom.interpolate(distance_along)

    # Identify all sidewalks within sidewalk search distance, sort by distance
    edges_near_street = G.network.edges.dwithin_edges(
        st_point.x, st_point.y, sidewalk_search_dist, sort=True
    )
    nearby_sidewalks = (
        d
        for _, __, d in edges_near_street
        if d.get("highway", None) == "footway"
        and d.get("footway", None) == "sidewalk"
    )

    # Iterate over each sidewalk, categorize as 'left' or 'right. When a
    # 'left' sidewalk is found, stop searching for left sidewalks. When a right
    # sidewalk is found, start searching for right sidewalks
    sw_left = None
    sw_right = None
    for sidewalk in nearby_sidewalks:
        if sw_left is not None and sw_right is not None:
            break
        side = line_side_of_line(street["geom"], sidewalk["geom"])
        if sw_left is None and side == "left":
            sw_left = (sidewalk["_u_id"], sidewalk["_v_id"])
        if sw_right is None and side == "right":
            sw_right = (sidewalk["_u_id"], sidewalk["_v_id"])

    # Return result
    return AssociatedStreet(
        street_id=(str(street["_u_id"]), str(street["_v_id"])),
        left_sidewalk_id=sw_left,
        right_sidewalk_id=sw_right,
    )


def _get_a_start_node(
    G: DiGraphGPKG, component: Set[NodeID]
) -> Optional[NodeID]:
    # A "start" node here is one on the fringe: it's only connected to 1 other
    # node. The graph is directed, so that means there should be either 0 or 1
    # predecessor nodes. 0 predecessors = the component is an isolated node. 1
    # predecessor = there are multiple nodes and this one is on the fringe.
    for node in component:
        try:
            pred = G.predecessors(node)
            n_pred = sum(1 for _ in pred)
            if n_pred < 2:
                # If
                return node
        except StopIteration:
            pass
    return None


def embed_intersection_graph_streets(G: DiGraphGPKG) -> int:
    """Extract intersection-to-intersection street graph, storing metadata on
    which edge IDs were merged from the input graph."""
    # Create street graph! This is a graph that contains only edges that have
    # certain metadata properties, namely certain values for the "highway" key.
    # G_street = nx.DiGraph()
    # G_street.add_edges_from()
    # for _, __, d in G.iter_edges()

    # Identify 2-degree street nodes
    # NOTE: this might not scale for very large numbers of nodes
    degree2_street_nodes: List[NodeID] = []
    for node in G.nodes():
        # Ignore nodes that aren't degree-2. Note that graph is directed, so
        # this means nodes with two incoming edges and two outgoing edges.
        predecessors = list(G.predecessors(node))
        successors = list(G.successors(node))
        if len(predecessors) != 2 or len(successors) != 2:
            continue

        # Only pay attention to nodes flanked by streets
        node_in = predecessors[0]
        node_out = successors[0]
        edge_in = G[node_in][node]
        if edge_in.get("highway", None) not in STREETS:
            continue
        edge_out = G[node_out][node]
        if edge_out.get("highway", None) not in STREETS:
            continue

        # Append node! It's degree-2 and flanked by streets
        degree2_street_nodes.append(node)

    # Create a view over the graph using those nodes and collect connected
    # components - each set of connected nodes are what need to be merged
    # together - represent a path that can't back up on itself
    # Create merge plan based on successive nodes
    G_in_mem = nx.DiGraph()
    G_in_mem.add_nodes_from(G.nodes(data=True))
    G_in_mem.add_edges_from(G.iter_edges())
    G_sub = G_in_mem.subgraph(degree2_street_nodes)
    paths = []
    for components in nx.weakly_connected_components(G_sub):
        # NOTE: some of these algorithms would be easier to conceptualize
        # and understand with an undirected graph.
        # Get a candidate 'start' node: a node on the fringe of the component.
        start_node = _get_a_start_node(G_sub, components)
        if start_node is None:
            # FIXME: totally wrong behavior - not a ValueError, not handled
            # properly
            raise ValueError("Couldn't find start node!")

        # Build a path that doesn't double back on itself, stop when reaching
        # the fringe.
        node = start_node
        seen = {node}
        path = [node]
        while True:
            next_nodes = list(G_sub.successors(node))
            n_nodes = len(next_nodes)
            if n_nodes == 0:
                # If there are no successor nodes, the component only had 1
                # node in it. This is the whole path - exit.
                break
            else:
                # Rule out nodes already-visited
                unseen = [n for n in next_nodes if n not in seen]
                n_unseen = len(unseen)
                if n_unseen == 0:
                    # Reached the fringe!
                    break
                elif n_unseen == 1:
                    # Reached a mid-node. Add and move on
                    next_node = next_nodes[0]
                    seen.add(next_node)
                    path.append(next_node)
                else:
                    # This shouldn't happen - raise an error.
                    raise ValueError("Invalid path node.")

        # The path is currently all degree-2 nodes. Flank it with the
        # neighboring nodes so that the path is truly the entire set of nodes
        # to use to represent the street!
        # TODO: catch StopIteration
        path = [next(G_in_mem.predecessors(path[0])), *path]
        path.append(next(G_in_mem.successors(path[-1])))

        # Append path! And don't forget the reverse path as well (street going
        # in the other direction).
        paths.append(path)
        paths.append(path[::-1])

    # Create intersection-to-intersection streets from merge plan. Include the
    # edges used to create it as an array of (u,v) tuples stored as JSON.
    for path in paths:
        u = path[0]
        v = path[-1]
        geom = GeoJSONLineString(
            coordinates=[G.nodes[n]["geom"]["coordinates"] for n in path]
        )
        # Store an array of the edge identifiers as JSON (so that it nicely
        # serializes to the db - TODO: make unweaver do this automatically for
        # otherwise non-serializable data?)
        edges = json.dumps(list(zip(path, path[1:])))
        # TODO: remove need for 'mapping' here: use Shapely geometries for
        # (de)serialization?
        d = {"geom": geom, "_street": 1, "_edges": edges}
        # TODO: improve Unweaver error messages. When insertion column type is
        # wrong, the message back is very unhelpful. It doesn't list the
        # column name, the column type, or the type of the input!
        G.add_edges_from(((u, v, d),))

    # FIXME: the spatial index gets out of date, but shouldn't! This hack to
    # drop and re-create it should be replaced by an upstream fix to Unweaver.
    G.network.edges.drop_rtree()
    G.network.edges.add_rtree()

    return len(paths)


def associate_streets(G: DiGraphGPKG, counter=None) -> None:
    """Precalculate and embed sidewalk associations for street graph midpoints.

    Note that the input graph needs to have street-to-street edges embedded,
    i.e. embed_intersection_graph_streets needs to be run on it first.
    """
    # Iterate over every intersection-to-intersection street segment, find the
    # midpoint, and calculate the 'associate_street' value to get left/right
    # sidewalks.
    for _, __, d in G.iter_edges():
        if not d.get("_street", False):
            continue
        geometry = shape(d["geom"])
        midpoint = geometry.interpolate(distance=0.5, normalized=True)
        # TODO: type check on midpoint being a Point

        associated_street = associate_street(midpoint.x, midpoint.y, G)
        # Assign left/right sidewalks to each street that is, itself,
        # associated with this intersection-to-intersection street
        try:
            edges: List[EdgeID] = json.loads(d["_edges"])
        except ValueError:
            # TODO: do more than continue?
            continue
        for u, v in edges:
            d2 = G[u][v]
            d2["sw_left"] = json.dumps(associated_street.left_sidewalk_id)
            d2["sw_right"] = json.dumps(associated_street.right_sidewalk_id)
        if counter is not None:
            counter.update(2)
