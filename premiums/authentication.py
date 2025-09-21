from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from rest_framework import exceptions
import jwt
from django.contrib.auth.models import AnonymousUser


class ExternalJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        user = AnonymousUser()
        user.id = payload.get('user_id')
        user.username = payload.get('username', '')
        return (user, token)
