import unweaver


class RoutingContext:
    def __init__(self, G, profiles):
        self.G = G
        self.profiles = profiles


class NetworkContainer:
    def __init__(
        self,
        pedestrian_graph,
        street_graph,
        pedestrian_profiles,
        street_profiles,
    ):
        self.pedestrian = RoutingContext(pedestrian_graph, pedestrian_profiles)
        self.street = RoutingContext(pedestrian_graph, pedestrian_profiles)

    @staticmethod
    def from_directories(pedestrian_directory, street_directory):
        def from_directory(directory):
            G = unweaver.graph.get_graph(directory)
            G = G.to_in_memory()
            profiles = unweaver.parsers.parse_profiles(directory)
            return G, profiles

        G_ped, profiles_ped = from_directory(pedestrian_directory)
        G_street, profiles_street = from_directory(street_directory)

        return NetworkContainer(G_ped, G_street, profiles_ped, profiles_street)
