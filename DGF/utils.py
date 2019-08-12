import importlib
from django.db import models

from .fields import Field


def get_reverse_fields(model, local_field_names):
    for name, attr in model.__dict__.items():
        # Don't duplicate any local fields
        if name in local_field_names:
            continue

        # "rel" for FK and M2M relations and "related" for O2O Relations
        related = getattr(attr, "rel", None) or getattr(attr, "related", None)
        if isinstance(related, models.ManyToOneRel):
            yield (name, related)
        elif isinstance(related, models.ManyToManyRel) and not related.symmetrical:
            yield (name, related)


def get_model_fields(model):
    local_fields = [
        (field.name, field)
        for field in sorted(
            list(model._meta.fields) + list(model._meta.local_many_to_many)
        )
    ]

    # Make sure we don't duplicate local fields with "reverse" version
    local_field_names = [field[0] for field in local_fields]
    reverse_fields = get_reverse_fields(model, local_field_names)

    all_fields = local_fields + list(reverse_fields)

    return all_fields


def get_converted_model_fields(model):
    django_fields = get_model_fields(model)
    fields = {
        name: Field(name, django_field=field) for name, field in django_fields
    }
    return fields


def get_module(path):
    split = path.split('.')
    module_name = '.'.join(split[:-1])
    class_name = split[-1]
    return importlib.import_module(module_name).__dict__[class_name]
