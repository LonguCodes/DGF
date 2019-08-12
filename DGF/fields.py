import graphene

from .converter import convert
from .exceptions import SchemaException
from .registry import get_registry

from django.db import models


def get_filter(field):
    field_type = type(field)
    if field_type is graphene.NonNull:
        return field._of_type(required=False)
    elif field_type is graphene.Dynamic:
        return graphene.List(graphene.Int, required=False)
    return field_type(required=False)


def is_django_relation(field):
    field_type = type(field)

    return (field_type is models.ManyToManyField
            or field_type is models.ManyToManyRel
            or field_type is models.ManyToOneRel)


def list_resolver(parent, info, **kwargs):
    return getattr(parent, info.field_name).filter(**kwargs)


class Field:
    def __init__(self, name, field=None, django_field=None):

        self.name = name
        if not field:
            if django_field:
                registry = get_registry()
                self.field = convert(django_field, registry)

            else:
                raise SchemaException(None, 'Neither django_field nor field supplied')
        else:
            self.field = field

        self.is_required = getattr(django_field, 'primary_key', False) or issubclass(type(self.field), graphene.NonNull)

        self.is_relation = is_django_relation(django_field)

        self.is_list = self.is_relation or issubclass(type(field), graphene.List)

        self.filter = get_filter(self.field)
        self.resolver = list_resolver if self.is_list else None
