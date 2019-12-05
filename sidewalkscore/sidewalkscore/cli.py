"""sidewalkscore CLI."""
import os

import click

import entwiner
from unweaver.build import build_graph
from unweaver.parsers import parse_profiles
from unweaver.server import run_app
from unweaver.weight import precalculate_weights
from sidewalkscore.sidewalkscore import sidewalkscore_batch
# from sidewalkscore.build import build_graphs


@click.group()
def sidewalkscore():
    pass


@sidewalkscore.command()
@click.argument("directory", type=click.Path("r"))
@click.option("--changes-sign", multiple=True)
def build(directory, changes_sign):
    # TODO: carbon-copied from unweaver. Could just allow a pass-through to unweaver
    # cli?
    # TODO: catch errors in starting server
    # TODO: spawn process?
    # TODO: separate arguments for street vs. pedestrian networks? 'changes-sign'
    # applies to both right now.
    pedestrian_directory = os.path.join(directory, "pedestrian")
    street_directory = os.path.join(directory, "street")

    click.echo("Building street network...")
    build_graph(street_directory, changes_sign=changes_sign)

    click.echo("Building pedestrian network...")
    build_graph(pedestrian_directory, changes_sign=changes_sign)

    click.echo("Done.")


@sidewalkscore.command()
@click.argument("directory", type=click.Path("r"))
def weight(directory):
    # TODO: carbon-copied from unweaver. Could just allow a pass-through to unweaver
    # cli?
    pedestrian_directory = os.path.join(directory, "pedestrian")
    street_directory = os.path.join(directory, "street")

    # TODO: catch errors in starting server
    # TODO: spawn process?
    click.echo("Calculating static street network weights...")
    # precalculate_weights(street_directory)

    click.echo("Calculating static pedestrian network weights...")

    profiles = parse_profiles(pedestrian_directory)
    G = entwiner.DiGraphDB(path=os.path.join(pedestrian_directory, "graph.db"))

    # TODO: speedup with .size() in entwiner
    n_profiles = len([p for p in profiles if p["precalculate"]])
    n_weights = G.size() * n_profiles

    # TODO: pass progressbar to precalculate_weights function or find equivalent
    # alternative
    with click.progressbar(length=n_weights, label="Computing pedestrian network weights") as bar:
        for profile in profiles:
            if profile["precalculate"]:
                cost_function = profile["cost_function"]()
                weight_column = "_weight_{}".format(profile["name"])
                batch = []
                for u, v, d in G.iter_edges():
                    # Update 100 at a time
                    weight = cost_function(u, v, d)
                    if len(batch) == 1000:
                        G.update_edges(batch)
                        batch = []
                    batch.append((u, v, {weight_column: weight}))
                    bar.update(1)
                # Update any remaining edges in batch
                if batch:
                    G.update_edges(batch)

    click.echo("Done.")


@sidewalkscore.command()
@click.argument("directory", type=click.Path("r"))
def score(directory):
    pedestrian_directory = os.path.join(directory, "pedestrian")
    street_directory = os.path.join(directory, "street")
    output_path = os.path.join(directory, "sidewalkscore.gpkg")

    G = entwiner.DiGraphDB(path=os.path.join(street_directory, "graph.db"))
    n = G.size()
    click.echo("Converting to in-memory graph databases...")
    with click.progressbar(length=n, label="Computing SidewalkScores") as bar:
        sidewalkscore_batch(pedestrian_directory, street_directory, output_path, counter=bar)
    click.echo("Done.")


@sidewalkscore.command()
@click.argument("directory", type=click.Path("r"))
@click.option("--host", "-h", default="localhost")
@click.option("--port", "-p", default=8000)
@click.option("--debug", is_flag=True)
def run(directory, host, port, debug=False):
    click.echo("Starting server in {}...".format(directory))
    # TODO: catch errors in starting server
    # TODO: spawn process?
    run_app(directory, host=host, port=port, debug=debug)