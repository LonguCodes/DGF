from DGF.resolvers.utils import get_filters


def default_resolve(schema, model, data, **kwargs):
    filters = get_filters(schema, data)
    return model.objects.filter(**filters)


def default_execute(data, **kwargs):
    return data
