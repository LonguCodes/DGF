from .utils import get_filters, get_values, get_relations, set_values, set_relations


def default_resolve(schema, model, data, **kwargs):
    filters = get_filters(schema, data)
    return model.objects.filter(**filters)


def default_execute(schema, data, raw_data, **kwargs):
    values = get_values(schema, raw_data)
    relations = get_relations(schema, raw_data)

    for model in data:
        set_values(model, values)
        set_relations(model, relations)
        model.save()
    return data
