"""sidewalkscore CLI."""
import os
import sqlite3

import click
import fiona  # type: ignore

from unweaver.build import get_layers_paths
from unweaver.graphs import DiGraphGPKG
from unweaver.parsers import parse_profiles
from unweaver.server import run_app
from sidewalkscore.associate import (
    associate_streets,
    embed_intersection_graph_streets,
)
from sidewalkscore.build import build_graph
from sidewalkscore.sidewalkscore_batch import sidewalkscore_batch

# Size of batch inserts
BATCH_SIZE = 1000


@click.group()
def sidewalkscore():
    pass


@sidewalkscore.command()
@click.argument("project_directory", type=click.Path(True))
@click.option("--changes-sign", multiple=True)
def build(project_directory, changes_sign):
    click.echo("Building network...")
    click.echo("Estimating feature count...")
    n = 0
    for path in get_layers_paths(project_directory):
        with fiona.open(path) as c:
            n += len(c)
    with click.progressbar(length=n, label="Importing edges") as bar:
        build_graph(project_directory, changes_sign=changes_sign, counter=bar)

    click.echo("Done.")


@sidewalkscore.command()
@click.argument("project_directory", type=click.Path(True))
def weight(project_directory):
    click.echo("Calculating static network weights...")

    profiles = parse_profiles(project_directory)
    precalculated_profiles = [p for p in profiles if p["precalculate"]]
    n_profiles = len(precalculated_profiles)

    G = DiGraphGPKG(path=os.path.join(project_directory, "graph.gpkg"))
    n_weights = G.size() * n_profiles

    # TODO: pass progressbar to precalculate_weights function or find
    # equivalent alternative
    with click.progressbar(
        length=n_weights, label="Computing network weights"
    ) as bar:
        for profile in profiles:
            if profile["precalculate"]:
                cost_function = profile["cost_function"](G)
                weight_column = "_weight_{}".format(profile["id"])
                try:
                    with G.network.gpkg.connect() as conn:
                        conn.execute(
                            f"""ALTER TABLE edges
                                 ADD COLUMN {weight_column} float"""
                        )
                except sqlite3.OperationalError:
                    pass
                batch = []
                for u, v, d in G.iter_edges():
                    weight = cost_function(u, v, d)
                    if len(batch) == BATCH_SIZE:
                        G.update_edges(batch)
                        batch = []
                    batch.append((u, v, {weight_column: weight}))
                    bar.update(1)
                # Update any remaining edges in batch
                if batch:
                    G.update_edges(batch)

    click.echo("Done.")


@sidewalkscore.command()
@click.argument("project_directory", type=click.Path(True))
def associate(project_directory):
    G = DiGraphGPKG(path=os.path.join(project_directory, "graph.gpkg"))
    click.echo("Extracting intersection-to-intersection streets...")
    n_paths = embed_intersection_graph_streets(G)
    with click.progressbar(
        length=n_paths, label="Associating streets and sidewalks..."
    ) as bar:
        associate_streets(G, counter=bar)
    click.echo("Done.")


@sidewalkscore.command()
@click.argument("project_directory", type=click.Path(True))
@click.option("--output_driver", "-od", default="GPKG")
def score(project_directory, output_driver):
    G = DiGraphGPKG(path=os.path.join(project_directory, "graph.gpkg"))
    n = G.size()
    with click.progressbar(length=n, label="Computing SidewalkScores") as bar:
        sidewalkscore_batch(
            project_directory, driver=output_driver, counter=bar
        )
    click.echo("Done.")


@sidewalkscore.command()
@click.argument("directory", type=click.Path(True))
@click.option("--host", "-h", default="localhost")
@click.option("--port", "-p", default=8000)
@click.option("--debug", is_flag=True)
def serve(directory, host, port, debug=False):
    click.echo("Starting server in {}...".format(directory))
    # TODO: catch errors in starting server
    # TODO: spawn process?
    run_app(directory, host=host, port=port, debug=debug)
