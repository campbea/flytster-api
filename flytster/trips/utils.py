import datetime

from .models import TripPrice, Flight


class InvalidTripOption(Exception):
    pass


def create_flights_from_trip_data(trip):
    '''
    Create a Flights from a Google QPX tripOption
    '''

    try:
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
                    passengers = trip.data['pricing'][0]['passengers']['adultCount']
                )

        price = float(trip.data['pricing'][0]['saleFareTotal'][3:])
        tax = float(trip.data['pricing'][0]['saleTaxTotal'][3:])
        total = float(trip.data['pricing'][0]['saleTotal'][3:])
        TripPrice.objects.create(trip=trip, price=price, tax=tax, total=total)

    except Exception as e:
        trip.delete()
        raise InvalidTripOption(e)
