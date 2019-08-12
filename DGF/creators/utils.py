import graphene


def get_values(schema):
    return {
        name: field.filter
        if not field.is_list else graphene.List(graphene.Int)
        for name, field in schema._fields.items()
        if not field.is_required
    }


def get_filters(schema):
    return {f'_{name}': field.filter
            for name, field in schema._fields.items() if
            not field.is_list}


def get_resolvers(schema):
    return schema._resolvers
