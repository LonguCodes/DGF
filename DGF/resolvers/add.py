from .utils import get_values, get_relations, set_relations


def default_resolve(schema, data,**kwargs):
    fields = get_values(schema, data)
    relations = get_relations(schema, data)
    model = schema.Meta.model.objects.create(**fields)
    set_relations(model, relations)
    model.save()
    return model


def default_execute(data,**kwargs):
    return data
