import re

from rest_framework import serializers, status

from trips.models import Trip

from .models import Passenger, GENDER_CHOICES


# Validators
def valid_phone(value):
    if re.match(r'^\d{10}$', value):
        return
    raise serializers.ValidationError('Phone numbers must be 10 digits.')


# Serializers
class CreatePassengerSerializer(serializers.Serializer):

    trip_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip.objects.all(), source='trip', write_only=True)
    first_name = serializers.CharField(max_length=20)
    middle_name = serializers.CharField(max_length=20, default='', allow_blank=True)
    last_name = serializers.CharField(max_length=20)
    phone = serializers.CharField(max_length=10, validators=[valid_phone])
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    birthdate = serializers.DateField()


class PassengerSerializer(serializers.ModelSerializer):

    trip = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Passenger
        fields = (
            'id', 'user', 'trip', 'first_name', 'middle_name', 'last_name', 'phone',
            'gender', 'birthdate', 'timestamp')
        read_only_fields = ('timestamp')
