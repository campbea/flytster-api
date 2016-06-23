import re
from datetime import datetime

from django.db.models import Min

from rest_framework import serializers

from .models import TripStatus, TripExpectedPassengers, TripPrice, Trip, Flight, Leg


class TripPostSerializer(serializers.Serializer):
    passenger_data = serializers.JSONField()
    pricing_data = serializers.JSONField()
    trip_data = serializers.JSONField()


class TripStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = TripStatus
        fields = ('is_selected', 'is_passenger_ready', 'is_available',
            'is_purchased', 'is_booked', 'is_expired', 'updated')


class TripExpectedPassengersSerializer(serializers.ModelSerializer):

    class Meta:
        model = TripExpectedPassengers
        fields = ('adult_count', 'child_count', 'infant_in_lap_count',
            'infant_in_seat_count', 'senior_count')


class TripPriceSerializer(serializers.ModelSerializer):
    expected_passengers = TripExpectedPassengersSerializer()

    class Meta:
        model = TripPrice
        fields = ('base', 'tax', 'total', 'ptc', 'refundable',
            'last_ticket_time', 'fare_calculation', 'expected_passengers')


class LegSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leg


class FlightSerializer(serializers.ModelSerializer):
    legs = LegSerializer(many=True)

    class Meta:
        model = Flight


class TripSerializer(serializers.ModelSerializer):
    status = TripStatusSerializer()
    price = TripPriceSerializer()
    flights = FlightSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('id', 'user', 'price', 'flights', 'status', 'timestamp')
