import graphene

from .. import pipeline
from .utils import get_filters


def mutate(root, info, **data):
    schema = info.parent_type.graphene_type._schemas[f'{info.field_name[6:]}Schema']
    return pipeline.trigger(info.context, schema, data, pipeline.DELETE)


def create(schema, name):
    filters = get_filters(schema)
    arguments = type('Arguments', (), filters)
    return type(f'{name}Delete', (graphene.Mutation,), {
        'Output': graphene.List(graphene.Int),
        'Arguments': arguments,
        'mutate': mutate,
        '_schema': schema
    })
