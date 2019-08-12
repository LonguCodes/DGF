import graphene

from .schemas import create_query, create_mutation


class Combiner:
    def __init__(self):
        self._schemas = []

    def register(self, schema):
        self._schemas.append(schema)

    def combine(self, other):
        self._schemas += other._schemas

    def to_schema(self):
        query = create_query(self._schemas)
        mutation = create_mutation(self._schemas)
        return graphene.Schema(query, mutation, auto_camelcase=False)
