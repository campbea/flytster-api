import datetime
import json
import requests

from django.conf import settings

from .models import TripSearch


class InvalidTripOption(Exception):
    pass


def create_trip_search_from_qpx_trip_option(user, data):
    '''
    Create a TripSearch instance from a Google QPX tripOption
    '''
    try:
        departure_date = data['slice'][0]['segment'][0]['leg'][0]['departureTime'][0:10]

        trip_search = TripSearch.objects.create(
            user = user,
            round_trip = False if len(data['slice']) == 1 else True,
            passenger = data['pricing'][0]['passengers'],
            origin = data['slice'][0]['segment'][0]['leg'][0]['origin'],
            destination = data['slice'][0]['segment'][-1]['leg'][-1]['destination'],
            date = departure_date,
            cabin = data['slice'][0]['segment'][0]['cabin'],
            departure_time = data['slice'][0]['segment'][0]['leg'][0]['departureTime'][11:16],
            carrier = data['slice'][0]['segment'][0]['flight']['carrier'],
            price = data['saleTotal'],
            trip_option = data,
            expiration = datetime.datetime.strptime(departure_date, '%Y-%m-%d')
        )
    except Exception as e:
        raise InvalidTripOption('Detail: {}'.format(e))

    return trip_search
