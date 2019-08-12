def get_relations(schema, data):
    return {name: value for name, value in data.items() if
            not name.startswith('_') and schema._fields[name].is_list}


def set_relations(model, relations):
    for name, value in relations.items():
        getattr(model, name).set(value)


def get_values(schema, data):
    return {name: value for name, value in data.items() if
            not name.startswith('_') and not schema._fields[name].is_list}


def set_values(model, values):
    for name, value in values.items():
        setattr(model, name, value)


def get_filters(schema, data):
    return {name[1:]: value for name, value in data.items() if
            name.startswith('_') and not schema._fields[name[1:]].is_list}


def delete_models(models):
    for model in models:
        model.delete()
