import json
from django.contrib.auth.models import AnonymousUser

from .. import pipeline
from ..auth import _authenticator
from ..exceptions import Unauthorized


class FetchLink(pipeline.BaseLink):
    def process(self, data):
        if self.params['type'] == pipeline.QUERY:
            return self.params['schema'].fetch_query(**self.get_args(data))
        if self.params['type'] == pipeline.ADD:
            return self.params['schema'].fetch_add(**self.get_args(data))
        if self.params['type'] == pipeline.CHANGE:
            return self.params['schema'].fetch_change(**self.get_args(data))
        if self.params['type'] == pipeline.DELETE:
            return self.params['schema'].fetch_delete(**self.get_args(data))


class ObjectPermissionLink(pipeline.BaseLink):

    def process(self, data):
        permissions = getattr(self.params['schema'], 'permissions', [])
        if hasattr(data, '__iter__'):
            return list(filter(
                lambda x: all(map(lambda y: getattr(y, y.object_permission_check)(**self.get_args(data)), permissions)),
                data))

        return data if all(
            map(lambda y: getattr(y, y.object_permission_check)(**self.get_args(data)), permissions)) else None


class RequestPermissionLink(pipeline.BaseLink):

    def process(self, data):
        permissions = getattr(self.params['schema'], 'permissions', [])

        authorized = all(
            map(lambda y: getattr(y, y.request_permission_check)(**self.get_args(data)), permissions)
        )

        if not authorized:
            raise Unauthorized()
        return data


class AuthLink(pipeline.BaseLink):

    def process(self, data):
        args = {name: value[1] for name, value in
                {**self.context.headers._store, **json.loads(self.context.body)}.items()
                if name in _authenticator.all_args}
        user = None
        for authenticator in _authenticator.authenticators:
            user = authenticator.authenticate(**args)
            if user and user.is_authenticated:
                break
        if not user:
            user = AnonymousUser()
        self.params['user'] = user
        return data


class ExecuteLink(pipeline.BaseLink):

    def process(self, data):
        if self.params['type'] == pipeline.QUERY:
            return self.params['schema'].execute_query(**self.get_args(data))
        if self.params['type'] == pipeline.ADD:
            return self.params['schema'].execute_add(**self.get_args(data))
        if self.params['type'] == pipeline.CHANGE:
            return self.params['schema'].execute_change(**self.get_args(data))
        if self.params['type'] == pipeline.DELETE:
            return self.params['schema'].execute_delete(**self.get_args(data))
