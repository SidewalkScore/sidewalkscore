from collections import OrderedDict

import fiona
import fiona.crs
import shapely

import unweaver

from .sidewalkscore import sidewalkscore

# TODO: put in top-level __init__, as it has global effects?
if shapely.speedups.available:
    shapely.speedups.enable()


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
