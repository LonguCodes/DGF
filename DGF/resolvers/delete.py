# TODO: Try to return full data about the object
from .utils import get_filters, delete_models


def default_resolve(schema, model, data, **kwargs):
    filters = get_filters(schema, data)
    models = model.objects.filter(**filters)

    return models


def default_execute(data, **kwargs):
    ids = [model.id for model in data]
    delete_models(data)
    return ids
