import re
import time

from django.db.models import Min

from rest_framework import serializers

from .models import Trip, TripStatus


class TripStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = TripStatus
        fields = ('is_selected', 'is_passenger_ready', 'is_available',
            'is_purchased', 'is_booked', 'is_expired', 'updated')


class TripPostSerializer(serializers.Serializer):
    trip_option = serializers.JSONField()

    def validate_trip_option(self, value):
        if not value['kind'] == 'qpxexpress#tripOption':
            raise serializers.ValidationError('Data must be a QPX Trip Option')
        if not 'id' in value:
            raise serializers.ValidationError('Data must have an id.')
        if not 'slice' in value:
            raise serializers.ValidationError('Data must have a slice field.')
        if not 'pricing' in value:
            raise serializers.ValidationError('Data must have a pricing field')
        return value


class TripSerializer(serializers.ModelSerializer):
    status = TripStatusSerializer()
    cheapest_price = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ('id', 'user', 'cheapest_price', 'status', 'data', 'timestamp')

    def get_cheapest_price(self, obj):
        if obj.prices.first():
            d = obj.prices.aggregate(cheapest_price=Min('total'))
            return d['cheapest_price']
