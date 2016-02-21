from django.conf import settings
from django.db import models


def set_expiration():
    return now() + timedelta(years=1)


class Credit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='credits')
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    used = models.BooleanField(default=False)
    expiration = models.DateTimeField(default=set_expiration)
    timestamp = models.DateTimeField(auto_now_add=True)
