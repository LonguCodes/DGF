_registry = None


class Registry:
    def __init__(self):
        self._schemas = {}
        self._converted = {}

    def get_schema_by_model(self, model):
        if model in self._schemas:
            return self._schemas[model]
        return None

    def register_schema(self, schema):
        self._schemas[schema.Meta.model] = schema

    def get_converted_by_field(self, field):
        if field in self._converted:
            return self._converted[field]
        return None

    def register_field(self, converted, field):
        self._converted[field] = converted

    def get_query_by_model(self, model):
        if model in self._schemas:
            return self._schemas[model].Query
        return None


def get_registry():
    global _registry
    if not _registry:
        _registry = Registry()
    return _registry
