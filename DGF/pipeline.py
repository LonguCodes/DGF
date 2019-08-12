from django.conf import settings

from . import defaults
from .utils import get_module

pipeline = None


class BaseLink:

    def get_args(self, data):
        return {
            'schema': self.params['schema'],
            'model': self.params['model'],
            'data': data,
            'params': self.params,
            'raw_data': self.params['raw_data']
        }

    def __init__(self, inner=None):
        self._inner = inner
        if inner:
            self._base = inner._base
        else:
            self._base = self
        self._context = None
        self._params = None

    def init_trigger(self, context, params):
        self._base._context = context
        self._base._params = params

    @property
    def context(self):
        if self._base:
            return self._base._context
        return self._context

    @property
    def params(self):
        if self._base:
            return self._base._params
        return self._params

    def process(self, data):
        return data

    def set_up(self):
        pass

    def activate(self, data):
        if self._inner:
            data = self._inner.activate(data)
        return self.process(data)


def create():
    pipeline_modules = getattr(settings, 'DGF_PIPELINE', defaults.PIPELINES)
    global pipeline
    pipeline = BaseLink()

    for block_address in pipeline_modules:
        pipeblock = get_module(block_address)
        pipeline = pipeblock(pipeline)
        pipeline.set_up()


def trigger(context, schema, data, type):
    model = schema.Meta.model
    params = {
        'schema': schema,
        'model': model,
        'type': type,
        'raw_data': data
    }
    pipeline.init_trigger(context=context, params=params)
    return pipeline.activate(data)


QUERY = 1
ADD = 2
CHANGE = 3
DELETE = 4
