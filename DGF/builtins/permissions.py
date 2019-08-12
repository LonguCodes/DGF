from .. import BasePermission
from .. import QUERY


class ReadOnlyPermission(BasePermission):

    @staticmethod
    def has_object_permission(params, **kwargs):
        return params['type'] == QUERY

    @staticmethod
    def has_request_permission(params, **kwargs):
        return params['type'] == QUERY
