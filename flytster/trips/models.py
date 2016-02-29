import datetime

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


CABIN_CHOICES = (
    ("COACH", "COACH"),
    ("PREMIUM_COACH", "PREMIUM_COACH"),
    ("BUSINESS", "BUSINESS"),
    ("FIRST", "FIRST"))


class TripStatus(models.Model):
    is_selected = models.BooleanField(default=True)
    is_passenger_ready = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    is_booked = models.BooleanField(default=False)
    is_ticketed = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class TripPrice(models.Model):
    trip = models.ForeignKey("Trip", related_name='prices')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    tax = models.DecimalField(max_digits=6, decimal_places=2)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "TripPrice"
        verbose_name_plural = "TripPrices"
        ordering = ['-timestamp']

    def __unicode__(self):
        return '{0}'.format(self.price)


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trips')
    status = models.OneToOneField(TripStatus)
    data = JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ['-timestamp']

    def __unicode__(self):
        return '{0} {2}'.format(self.user.full_name, self.timestamp)


class Flight(models.Model):
    trip = models.ForeignKey(Trip, null=True, related_name='flights')
    carrier = models.CharField(max_length=2)
    number = models.CharField(max_length=10)
    cabin = models.CharField(max_length=13, choices=CABIN_CHOICES)
    booking_code = models.CharField(max_length=1)
    married = models.CharField(max_length=1)
    aircraft = models.CharField(max_length=10)
    arrival_time = models.CharField(max_length=22)
    departure_time = models.CharField(max_length=22)
    origin = models.CharField(max_length=3)
    destination = models.CharField(max_length=3)
    passengers = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ['-timestamp']

    def __unicode__(self):
        return '{0} {2}'.format(self.carrier, self.number)


# class TripSearch(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trip_searches')
#     round_trip = models.BooleanField(default=True)
#     passenger = JSONField()
#     origin = models.CharField(max_length=3)
#     destination = models.CharField(max_length=3)
#     date = models.CharField(max_length=10)
#     cabin = models.CharField(max_length=13, choices=CABIN_CHOICES)
#     arrival_time = models.CharField(max_length=5)
#     departure_time = models.CharField(max_length=5)
#     carrier = models.CharField(max_length=2)
#     price = models.CharField(max_length=12)
#     trip_option = JSONField()
#     expiration = models.DateTimeField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         verbose_name = "TripSearch"
#         verbose_name_plural = "TripSearches"
#         ordering = ['-timestamp']
#
#     def __unicode__(self):
#         return '{0} -> {1}: {2}'.format(self.origin, self.destination, self.date)
