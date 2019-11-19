from allocloud.openapt.errors import CircularDependencyException

class Graph():
    def __init__(self):
        self.edges = EdgeCollection()

    def add_dependency(self, source, dependency):
        self.edges.append(source, dependency)

    def resolve(self, entities):
        # Resolving the dependency tree is done with Kahn's algorithm

        edges = self.edges.copy()
        sorted_entities = []

        # First we get a list with each entity which is not a dependency of another entity
        # These are "root" entities
        root_entities = list(filter(lambda entity: edges.has_dependency(entity) is None, entities))

        # For each root entity we find its dependencies and we add them self as a root dependency
        while root_entities:
            entity = root_entities.pop()
            sorted_entities.append(entity)
            for source, dependency in edges.copy():
                if source != entity:
                    continue

                edges.remove(source, dependency)
                if not edges.has_dependency(dependency):
                    root_entities.append(dependency)

        # If we still have edges in the graph, they are circular dependencies
        if not edges.empty():
            raise CircularDependencyException() # TODO print a list of circular dependencies

        # We partially sort the result by entity priority, BUT we keep the order per type of entity.
        sorted_entities.sort(key=lambda entity: entity.priority)

        # Finally we reverse the array since to execute command from bottom to top
        sorted_entities.reverse()

        return sorted_entities

    def parents_of(self, entities):
        edges = self.edges.copy()
        sorted_entities = []

        source_entities = entities.copy()

        while source_entities:
            entity = source_entities.pop()
            sorted_entities.append(entity)
            for source, dependency in edges.copy():
                if source != entity:
                    continue
                source_entities.append(dependency)

        # We partially sort the result by entity priority, BUT we keep the order per type of entity.
        sorted_entities.sort(key=lambda entity: entity.priority)

        # Finally we reverse the array since to execute command from bottom to top
        sorted_entities.reverse()

        return sorted_entities


class EdgeCollection():
    def __init__(self, edges=None):
        self.edges = edges if edges else []

    def __iter__(self):
        return self.edges.__iter__()

    def __next__(self):
        return self.edges.__next__()

    def empty(self):
        return len(self.edges) <= 0

    def append(self, source, dependency):
        self.edges.append((source, dependency))

    def remove(self, source, dependency):
        self.edges.remove((source, dependency))

    def has_dependency(self, entity):
        try:
            next((source, dependency) for source, dependency in self.edges if dependency == entity)
            return True
        except StopIteration:
            return None

    def copy(self):
        return EdgeCollection(self.edges.copy())