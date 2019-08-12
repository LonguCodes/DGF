from django.contrib.auth import authenticate

from ..auth.authenticator import BaseAuthenticator


class BackendAuthenticator(BaseAuthenticator):

    @classmethod
    def authenticate(cls, **kwargs):
        credentials = {name.lower(): value[1] for name, value in kwargs.items() if name in cls.args}
        return authenticate(**credentials)


class BearerAuthenticator(BaseAuthenticator):
    args = ['Authorization']

    @classmethod
    def authenticate_token(cls, token):
        return None

    @classmethod
    def authenticate(cls, authorization=None, **kwargs):
        if authorization is None:
            return None
        if not authorization.startswith('Bearer '):
            return None
        token = authorization[7:]
        return cls.authenticate_token(token=token)


class ModelAuthenticator(BackendAuthenticator):
    args = ['username', 'password']
