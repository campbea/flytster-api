from django.conf import settings
from django.db import models

from trips.models import Trip


GENDER_CHOICES = (
    ("M", "male"),
    ("m", "male"),
    ("F", "female"),
    ("f", "female"))


class Passenger(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='passengers')
    trip = models.ForeignKey(Trip, related_name='passengers')
    first_name = models.CharField(max_length=20, null=False)
    middle_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthdate = models.DateField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = u'Passenger'
        verbose_name_plural = u'Passengers'
        ordering = ['-timestamp']
        unique_together = ('trip', 'first_name', 'last_name', 'birthdate')

    def get_full_name(self):
        if self.middle_name:
            return self.first_name + ' ' + middle_name + ' ' + self.last_name
        else:
            return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name

    def str(self):
        return get_full_name()
