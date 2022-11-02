import os

from unweaver.build import build_graph


def build_graphs(path, changes_sign=None):
    if changes_sign is None:
        changes_sign = []

    ped_path = os.path.join(path, "pedestrian")
    street_path = os.path.join(path, "street")

    G_ped = build_graph(ped_path, changes_sign=changes_sign)
    G_st = build_graph(street_path, changes_sign=changes_sign)

    return G_ped, G_st
