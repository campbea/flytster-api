import datetime

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from .managers import TripManager


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

    def __str__(self):
        for field_name in ['is_selected', 'is_passenger_ready', 'is_available',
                        'is_purchased', 'is_booked', 'is_ticketed', 'is_expired']:
            value = getattr(self, field_name, None)
            if value:
                save_field = field_name
                save_value = value
            else:
                return '{0}: {1}'.format(save_field, save_value)


class TripExpectedPassengers(models.Model):
    trip_price = models.OneToOneField('TripPrice', related_name='expected_passengers')
    adult_count = models.IntegerField(default=0)
    child_count = models.IntegerField(default=0)
    infant_in_lap_count = models.IntegerField(default=0)
    infant_in_seat_count = models.IntegerField(default=0)
    senior_count = models.IntegerField(default=0)


class TripPrice(models.Model):
    trip = models.OneToOneField("Trip", related_name='price')
    base = models.DecimalField(max_digits=6, decimal_places=2)
    tax = models.DecimalField(max_digits=6, decimal_places=2)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    ptc = models.CharField(max_length=10, default='')
    refundable = models.BooleanField(default=False)
    last_ticket_time = models.DateTimeField()
    fare_calculation = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "TripPrice"
        verbose_name_plural = "TripPrices"
        ordering = ['-timestamp']

    def __str__(self):
        return '{0}'.format(self.total)


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trips')
    status = models.OneToOneField(TripStatus)
    data = JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = TripManager()

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ['-timestamp']

    def __str__(self):
        return '{0} {1}'.format(self.user.full_name, self.timestamp)


class Flight(models.Model):
    trip = models.ForeignKey(Trip, null=True, related_name='flights')
    carrier = models.CharField(max_length=2)
    number = models.CharField(max_length=10)
    duration = models.IntegerField()
    cabin = models.CharField(max_length=13, choices=CABIN_CHOICES)
    booking_code = models.CharField(max_length=1)
    married_group = models.CharField(max_length=1)
    connection_duration = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ['-timestamp']

    def __str__(self):
        return '{0} {1}'.format(self.carrier, self.number)


class Leg(models.Model):
    flight = models.ForeignKey(Flight, related_name='legs')
    aircraft = models.CharField(max_length=10)
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()
    origin = models.CharField(max_length=3)
    destination = models.CharField(max_length=3)
    duration = models.IntegerField()
    on_time_performance = models.IntegerField(null=True, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    meal = models.CharField(max_length=120, default='')
    secure = models.BooleanField(default=True)
    connection_duration = models.IntegerField(null=True, blank=True)
    change_plane = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Leg"
        verbose_name_plural = "Legs"
        ordering = ['-timestamp']

    def __str__(self):
        return '{0} >>> {2}'.format(self.origin, self.destination)
