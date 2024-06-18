from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')
        if api_key == f"Bearer {settings.API_KEY}":
            return (None, None)
        raise AuthenticationFailed('Invalid API Key')
