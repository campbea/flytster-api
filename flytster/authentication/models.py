from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


def generate_token():
    return uuid4().hex


class AuthToken(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='auth_tokens')
    token = models.CharField(max_length=36, default=generate_token)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AuthToken'
        verbose_name_plural = 'AuthTokens'

    def __str__(self):
        return self.user.email

    @property
    def is_expired(self):
        delta = timedelta(
            days=settings.TOKEN_EXP_IN_DAYS
            ) if self.user.email_verified else timedelta(hours=24)
        if timezone.now() - self.timestamp < delta:
            return False
        self.delete()
        return True


class TokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        if not token:
            return None

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = AuthToken.objects.select_related('user').get(token=key)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed()

        if token.is_expired:
            raise AuthenticationFailed()

        return (token.user, token.token)