import graphene

from .creators import (
    add as add_creator,
    change as change_creator,
    delete as delete_creator
)
from .pipeline import DELETE, ADD, CHANGE, QUERY
from .resolvers import (
    query as query_resolver,
    add as add_resolver,
    change as change_resolver,
    delete as delete_resolver,
)
from .fields import Field
from .registry import get_registry
from .utils import get_converted_model_fields
from .utiltypes import SubclassWithMeta


def get_fields(schema, model, field_names):
    schema_fields = {value.name: value for value in schema.__dict__.values() if
                     type(value) is Field}
    model_fields = get_converted_model_fields(model)

    fields = {**model_fields, **schema_fields}
    return {name: value for name, value in fields.items() if not field_names or name in field_names}


class Schema(SubclassWithMeta):
    permissions = []
    allowed_requests = [QUERY, ADD, CHANGE, DELETE]

    @classmethod
    def fetch_query(cls, **kwargs):
        return query_resolver.default_resolve(**kwargs)

    @classmethod
    def execute_query(cls, **kwargs):
        return query_resolver.default_execute(**kwargs)

    @classmethod
    def fetch_add(cls, **kwargs):
        return add_resolver.default_resolve(**kwargs)

    @classmethod
    def execute_add(cls, **kwargs):
        return add_resolver.default_execute(**kwargs)

    @classmethod
    def fetch_change(cls, **kwargs):
        return change_resolver.default_resolve(**kwargs)

    @classmethod
    def execute_change(cls, **kwargs):
        return change_resolver.default_execute(**kwargs)

    @classmethod
    def fetch_delete(cls, **kwargs):
        return delete_resolver.default_resolve(**kwargs)

    @classmethod
    def execute_delete(cls, **kwargs):
        return delete_resolver.default_execute(**kwargs)

    @classmethod
    def __init_subclass_with_meta__(cls, model, fields=None, **options):
        setattr(cls, 'mutations', {})

        registry = get_registry()

        schema_fields = {}
        graphene_fields = {}
        filters = {}
        resolvers = {}

        for name, field in get_fields(cls, model, fields).items():
            graphene_fields[name] = field.field
            filters[name] = field.filter

            if field.resolver:
                resolvers[f'resolve_{name}'] = field.resolver

            schema_fields[name] = field

        setattr(cls, '_graphene_fields', graphene_fields)
        setattr(cls, '_filters', filters)
        setattr(cls, '_resolvers', resolvers)
        setattr(cls, '_fields', schema_fields)

        create_query(model.__name__, cls)
        create_mutations(model.__name__, cls)
        registry.register_schema(cls)


def create_query(name, schema):
    if QUERY not in schema.allowed_requests:
        return
    base = (graphene.ObjectType,)
    props = {**schema._graphene_fields, **schema._resolvers, '_schema': schema}
    query = type(f'{name}Query', base, props)
    setattr(schema, 'Query', query)


def create_mutations(name, schema):
    if ADD in schema.allowed_requests:
        schema.mutations['add'] = add_creator.create(schema, name)
    if CHANGE in schema.allowed_requests:
        schema.mutations['change'] = change_creator.create(schema, name)
    if DELETE in schema.allowed_requests:
        schema.mutations['delete'] = delete_creator.create(schema, name)
