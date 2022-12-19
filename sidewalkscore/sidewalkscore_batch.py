import os
import shapely  # type: ignore

from unweaver.graphs import DiGraphGPKG

from .sidewalkscore import sidewalkscore
from .network_container import NetworkContainer

from sidewalkscore.constants import STREETS

# TODO: put in top-level __init__, as it has global effects?
if shapely.speedups.available:
    shapely.speedups.enable()


def sidewalkscore_batch(project_directory, driver="GPKG", counter=None):
    sidewalkscores_ebunch = []
    G = DiGraphGPKG(path=os.path.join(project_directory, "graph.gpkg"))
    for i, (u, v, d) in enumerate(G.iter_edges()):
        if d.get("highway", None) in STREETS:
            sidewalkscores = sidewalkscore(networks, d)
            sidewalkscores_ebunch.append((u, v, sidewalkscores))

    networks.street.G.update(sidewalkscores_ebunch)
