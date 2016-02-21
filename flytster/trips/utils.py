import datetime

from .models import TripPrice, Flight

class InvalidTripOption(Exception):
    pass


def create_flights_from_trip_option_data(trip):
    '''
    Create a Flights from a Google QPX tripOption
    '''

    try:
        passenger_dict = trip.data['pricing'][0]['passengers']
        passengers = 0
        for key, value in passenger_dict.items():
            if isinstance(value, int):
                passengers += value

        for c, slice_item in enumerate(trip.data['slice']):
            for segment_item in trip.data['slice'][c]['segment']:
                Flight.objects.create(
                    trip=trip,
                    carrier = segment_item['flight']['carrier'],
                    number = segment_item['flight']['number'],
                    cabin = segment_item['cabin'],
                    booking_code = segment_item['bookingCode'],
                    married = segment_item['marriedSegmentGroup'],
                    aircraft = segment_item['leg'][0]['aircraft'],
                    arrival_time = segment_item['leg'][0]['arrivalTime'],
                    departure_time = segment_item['leg'][0]['departureTime'],
                    origin = segment_item['leg'][0]['origin'],
                    destination = segment_item['leg'][0]['destination'],
                    passengers = passengers
                )

        price = float(trip.data['saleTotal'][3:])
        TripPrice.objects.create(trip=trip, price=price)

    except Exception as e:
        trip.delete()
        raise InvalidTripOption(e)
