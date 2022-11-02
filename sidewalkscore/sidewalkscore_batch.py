import shapely  # type: ignore

from .sidewalkscore import sidewalkscore
from .network_container import NetworkContainer

# TODO: put in top-level __init__, as it has global effects?
if shapely.speedups.available:
    shapely.speedups.enable()


def sidewalkscore_batch(
    pedestrian_db_directory, street_db_directory, driver="GPKG", counter=None
):
    # TODO: use multiprocessing - speed up by nx, where n = cores
    networks = NetworkContainer.from_directories(
        pedestrian_db_directory, street_db_directory
    )

    # geom_key_st = networks.street.G.network.edges.geom_column

    # features = []
    # Update streets graph with sidewalkscores
    # TODO: this is where to parallelize
    sidewalkscores_ebunch = []
    for i, (u, v, street) in enumerate(networks.street.G.edges(data=True)):
        sidewalkscores = sidewalkscore(networks, street)
        sidewalkscores_ebunch.append((u, v, sidewalkscores))

    networks.street.G.update(sidewalkscores_ebunch)
