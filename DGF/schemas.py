import graphene
from graphene.utils.str_converters import to_camel_case
from .creators.query import resolve
from .creators.utils import get_filters


def add_schemas(type, schemas):
    schemas = {schema.__name__: schema for schema in schemas}
    setattr(type, '_schemas', schemas)
    return type


def create_query(schemas):
    fields = {}
    resolvers = {}

    for schema in schemas:
        query = getattr(schema, 'Query', None)

        if query:
            filters = get_filters(schema)

            name = to_camel_case(query.__name__)

            fields[name] = graphene.List(query, **filters)

            resolvers[f'resolve_{name}'] = resolve

    query_type = type('Query', (graphene.ObjectType,), {**fields, **resolvers})
    return add_schemas(query_type, schemas)


def create_mutation(schemas):
    base = (graphene.ObjectType,)

    mutations = {to_camel_case(mutation.__name__): mutation.Field() for schema in schemas for mutation in
                 schema.mutations.values()}
    mutation_type = type('Mutation', base, mutations)
    return add_schemas(mutation_type, schemas)
