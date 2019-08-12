from django.db import models
from django.utils.encoding import force_text
from functools import singledispatch
from graphene import (
    ID,
    Boolean,
    Dynamic,
    Enum,
    Field,
    Float,
    Int,
    List,
    NonNull,
    String,
    UUID,
    DateTime,
    Date,
    Time,
)
from graphene.utils.str_converters import to_camel_case, to_const
from graphql import assert_valid_name

from .creators.utils import get_filters


def convert_choice_name(name):
    name = to_const(force_text(name))
    try:
        assert_valid_name(name)
    except AssertionError:
        name = "A_%s" % name
    return name


def convert(field, registry=None):
    if registry:
        converted = registry.get_converted_by_field(field)
        if converted:
            return converted
    choices = getattr(field, "choices", None)
    if choices:
        converted = convert_with_choices(field, choices)
    else:
        converted = convert_without_choices(field, registry)
    if registry is not None:
        registry.register_field(converted, field)
    return converted


def convert_with_choices(field, choices):
    meta = field.model._meta
    name = to_camel_case("{}_{}".format(meta.object_name, field.name))

    choices = [(convert_choice_name(value), str(name)) for value, name in choices]

    enum = Enum(name, choices)
    return enum(required=not field.null)


@singledispatch
def convert_without_choices(field, registry=None):
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" % (field, field.__class__)
    )


@convert_without_choices.register(models.CharField)
@convert_without_choices.register(models.TextField)
@convert_without_choices.register(models.EmailField)
@convert_without_choices.register(models.SlugField)
@convert_without_choices.register(models.URLField)
@convert_without_choices.register(models.GenericIPAddressField)
@convert_without_choices.register(models.FileField)
@convert_without_choices.register(models.FilePathField)
def convert_field_to_string(field, registry=None):
    return String(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.AutoField)
def convert_field_to_id(field, registry=None):
    return ID(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.UUIDField)
def convert_field_to_uuid(field, registry=None):
    return UUID(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.PositiveIntegerField)
@convert_without_choices.register(models.PositiveSmallIntegerField)
@convert_without_choices.register(models.SmallIntegerField)
@convert_without_choices.register(models.BigIntegerField)
@convert_without_choices.register(models.IntegerField)
def convert_field_to_int(field, registry=None):
    return Int(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.BooleanField)
def convert_field_to_boolean(field, registry=None):
    return NonNull(Boolean, description=field.help_text)


@convert_without_choices.register(models.NullBooleanField)
def convert_field_to_nullboolean(field, registry=None):
    return Boolean(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.DecimalField)
@convert_without_choices.register(models.FloatField)
@convert_without_choices.register(models.DurationField)
def convert_field_to_float(field, registry=None):
    return Float(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.DateTimeField)
def convert_datetime_to_string(field, registry=None):
    return DateTime(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.DateField)
def convert_date_to_string(field, registry=None):
    return Date(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.TimeField)
def convert_time_to_string(field, registry=None):
    return Time(description=field.help_text, required=not field.null)


@convert_without_choices.register(models.OneToOneRel)
def convert_onetoone_field_to_djangomodel(field, registry=None):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_query_by_model(model)
        if not _type:
            return

        # We do this for a bug in Django 1.8, where null attr
        # is not available in the OneToOneRel instance
        null = getattr(field, "null", True)
        return Field(_type, required=not null)

    return Dynamic(dynamic_type)


@convert_without_choices.register(models.ManyToManyField)
@convert_without_choices.register(models.ManyToManyRel)
@convert_without_choices.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(field, registry=None):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_query_by_model(model)
        if not _type:
            return
        return List(_type, **get_filters(_type._schema))

    return Dynamic(dynamic_type)


@convert_without_choices.register(models.OneToOneField)
@convert_without_choices.register(models.ForeignKey)
def convert_field_to_djangomodel(field, registry=None):
    model = field.related_model

    def dynamic_type():
        _type = registry.get_query_by_model(model)
        if not _type:
            return

        return Field(_type, description=field.help_text, required=not field.null)

    return Dynamic(dynamic_type)
