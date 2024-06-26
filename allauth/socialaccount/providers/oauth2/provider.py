import warnings
from urllib.parse import parse_qsl

from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider

from .utils import generate_code_challenge


class OAuth2Provider(Provider):
    pkce_enabled_default = False
    oauth2_adapter_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.oauth2_adapter_class is None:
            warnings.warn("provider.oauth2_adapter_class property missing")

    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def get_callback_url(self):
        return reverse(self.id + "_callback")

    def get_pkce_params(self):
        settings = self.get_settings()
        if settings.get("OAUTH_PKCE_ENABLED", self.pkce_enabled_default):
            pkce_code_params = generate_code_challenge()
            return pkce_code_params
        return {}

    def get_auth_params(self, request, action):
        settings = self.get_settings()
        ret = dict(settings.get("AUTH_PARAMS", {}))
        dynamic_auth_params = request.GET.get("auth_params", None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))
        return ret

    def get_scope(self, request):
        settings = self.get_settings()
        scope = list(settings.get("SCOPE", self.get_default_scope()))
        dynamic_scope = request.GET.get("scope", None)
        if dynamic_scope:
            scope.extend(dynamic_scope.split(","))
        return scope

    def get_default_scope(self):
        return []
