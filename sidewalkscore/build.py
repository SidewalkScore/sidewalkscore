from unweaver.build import build_graph as unweaver_build_graph
from unweaver.parsers import parse_profiles

from .exceptions import (
    MisconfiguredStreetProfileError,
    MissingStreetProfileError,
)


def build_graph(path, changes_sign=None, counter=None):
    if changes_sign is None:
        changes_sign = []

    has_street_profile = False
    profiles = parse_profiles(path)
    for profile in profiles:
        if profile["id"] == "street":
            if "precalculate" not in profile or not profile["precalculate"]:
                raise MisconfiguredStreetProfileError(
                    "Street profile must have precalculated: true"
                )
            has_street_profile = True
            break
    if not has_street_profile:
        raise MissingStreetProfileError("Missing profile with id 'street'")

    G = unweaver_build_graph(path, changes_sign=changes_sign, counter=counter)

    return G
