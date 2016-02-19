import datetime

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


CABIN_CHOICES = (
    ("COACH", "COACH"),
    ("PREMIUM_COACH", "PREMIUM_COACH"),
    ("BUSINESS", "BUSINESS"),
    ("FIRST", "FIRST"))


class TripSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trip_searches')
    round_trip = models.BooleanField(default=True)
    passenger = JSONField()
    origin = models.CharField(max_length=20, blank=False)
    destination = models.CharField(max_length=20, blank=False)
    date = models.CharField(max_length=10, blank=False)
    cabin = models.CharField(max_length=13, choices=CABIN_CHOICES, blank=False)
    departure_time = models.CharField(max_length=5, blank=False)
    carrier = models.CharField(max_length=2, blank=False)
    price = models.CharField(max_length=12, blank=False)
    trip_option = JSONField()
    expiration = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "TripSearch"
        verbose_name_plural = "TripSearches"
        ordering = ['-timestamp']

    def __unicode__(self):
        return '{0} -> {1}: {2}'.format(self.origin, self.destination, self.date)


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trips')
    trip_search = models.OneToOneField(TripSearch, blank=False, related_name='trip')
    current_price = models.CharField(max_length=12, blank=False)
    cheapest_price = models.CharField(max_length=12, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ['-timestamp']

    def __unicode__(self):
        return '{0} {2}'.format(self.user.full_name, self.timestamp)

    
