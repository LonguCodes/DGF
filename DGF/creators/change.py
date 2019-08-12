from graphene import List, Mutation

from .utils import get_values, get_filters, get_resolvers
from .. import pipeline


def mutate(root, info, **data):
    schema = info.return_type.of_type.graphene_type._schema
    return pipeline.trigger(info.context, schema, data, pipeline.CHANGE)


def create(schema, name):
    values = get_values(schema)
    filters = get_filters(schema)

    arguments = type('Arguments', (), {**values, **filters})
    resolvers = get_resolvers(schema)
    return type(f'{name}Change', (Mutation,), {
        'Output': List(schema.Query),
        **resolvers,
        'Arguments': arguments,
        'mutate': mutate,
        '_schema': schema
    })
