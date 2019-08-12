class BasePermission:
    object_permission_check = 'has_object_permission'
    request_permission_check = 'has_request_permission'

    @staticmethod
    def has_object_permission(**kwargs):
        return True

    @staticmethod
    def has_request_permission(**kwargs):
        return True
