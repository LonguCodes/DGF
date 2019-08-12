from django.conf import settings
from ..defaults import AUTHENTICATORS
from ..utils import get_module

authenticators = []
all_args = []


def collect_authenticators():
    global authenticators, all_args
    authenticators = list(map(get_module, getattr(settings, 'GRAHENE_ADDONS_AUTHENTICATORS', AUTHENTICATORS)))
    for authenticator in authenticators:
        authenticator.args = list(map(str.lower, authenticator.args))
    all_args = [arg for authenticator in authenticators for arg in authenticator.args]
