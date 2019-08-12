def default_resolve(model, data, **kwargs):
    return model.objects.filter(**data)


def default_execute(data, **kwargs):
    return data
