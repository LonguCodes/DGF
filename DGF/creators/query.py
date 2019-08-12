from .. import pipeline


def resolve(parent, info, **data):
    schema = info.return_type.of_type.graphene_type._schema

    return pipeline.trigger(info.context, schema, data, pipeline.QUERY)
