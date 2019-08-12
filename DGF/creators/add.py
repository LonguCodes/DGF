from graphene import Mutation

from .. import pipeline
from .utils import get_values


def mutate(root, info, **data):
    schema = info.return_type.graphene_type._schema
    return pipeline.trigger(info.context, schema, data, pipeline.ADD)


def create(schema, name):
    values = get_values(schema)

    arguments = type('Arguments', (), values)

    return type(f'{name}Add', (Mutation,), {
        'Output': schema.Query,
        'Arguments': arguments,
        'mutate': mutate,
        '_schema': schema
    })
