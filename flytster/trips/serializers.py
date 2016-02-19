import re
import time

from rest_framework import serializers, status

from .models import TripSearch


class TripSearchPostSerializer(serializers.Serializer):
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


class TripSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = TripSearch
