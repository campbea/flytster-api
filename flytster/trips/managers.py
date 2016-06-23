from django.db import models, transaction
from django.utils.timezone import now, timedelta

from utils.converters import utc_string_to_datetime

class InvalidTripOption(Exception):
    pass


class TripManager(models.Manager):

    @transaction.atomic
    def create_trip(self, user, data):
        from .models import TripStatus, TripExpectedPassengers, TripPrice, Trip, Flight, Leg

        try:
            trip = Trip.objects.create(
                user=user,
                status=TripStatus.objects.create(),
                data=data)

            data['pricing_data']['last_ticket_time'] = utc_string_to_datetime(data['pricing_data']['last_ticket_time'])
            trip_price = TripPrice.objects.create(trip=trip, **data['pricing_data'])

            trip_exp_pass = TripExpectedPassengers.objects.create(
                                    trip_price=trip_price, **data['passenger_data'])

            # Loop through each slice object (one for one-way, two for round-trip)
            for slice_item in data['trip_data']['slice']:
                # Loop through each segment (multiple segments mean connecting flights)
                for segment_item in slice_item['segment']:
                    legs = segment_item.pop('leg')
                    flight = Flight.objects.create(trip=trip, **segment_item)
                    # Loop through each leg (smallest unit of travel - flight takeoff to landing)
                    for leg_item in legs:
                        leg_item['arrival_time'] = utc_string_to_datetime(leg_item['arrival_time'])
                        leg_item['departure_time'] = utc_string_to_datetime(leg_item['departure_time'])
                        Leg.objects.create(flight=flight, **leg_item)

        except Exception as e:
            raise InvalidTripOption(e)

        return trip
