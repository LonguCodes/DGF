from django.apps import AppConfig
from .pipeline import create
from .auth._authenticator import collect_authenticators


class DGFConfig(AppConfig):
    name = 'DGF'

    def ready(self):
        create()
        collect_authenticators()
