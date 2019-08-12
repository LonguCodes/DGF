from graphql import GraphQLError


class SchemaException(Exception):
    def __init__(self, schema, message):
        super(SchemaException, self).__init__(f'Incorrect schema {type(schema) if schema else ""} : {message}')


class PipelineException(GraphQLError):
    pass


class Unauthorized(PipelineException):
    def __init__(self):
        super(Unauthorized, self).__init__('You don\'t have permission to make this request')
