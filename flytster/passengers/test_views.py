import pytest
pytestmark = pytest.mark.django_db

import json
from copy import deepcopy
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import timezone
from rest_framework import status

from users.models import FlytsterUser
from trips.models import Trip, TripStatus


PASSENGER_DATA_ONE = {
    "trip_id": "this will be replaced with actual trip pk",
    "first_name": "Drew",
    "last_name": "Brees",
    "gender": "M",
    "birthdate": "1979-01-15"
}

PASSENGER_DATA_TWO = {
    "trip_id": "this will be replaced with actual trip pk",
    "first_name": "Matt",
    "last_name": "Ryan",
    "gender": "M",
    "birthdate": "1985-05-17"
}


class PassengerSetupFixture:
    def __init__(self):
        self.client = Client()

        self.user = FlytsterUser.objects.create_user(
            first_name='Fly',
            last_name='High',
            email='flyhigh@gmail.com',
            password='Password1'
        )

        self.user.verify_email_token(self.user.email_token.token)
        self.auth = {'HTTP_AUTHORIZATION': self.user.auth_tokens.latest('timestamp').token}

        self.trip = Trip.objects.create(
            user=self.user,
            data={"fake": "data"},
            status = TripStatus.objects.create()
        )


        self.url_list_create = reverse('list_create_passenger')
        self.url_get_update = lambda t: reverse('get_update_passenger', args=[t])


@pytest.fixture(scope="function")
def setup():
    return PassengerSetupFixture()


# Test Create Passenger
def test_create_passenger(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['user'] == setup.user.id
    assert response.data['trip'] == setup.trip.id
    assert response.data['first_name'] == data['first_name']
    assert response.data['last_name'] == data['last_name']

def test_create_passenger_bad_birthdate(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    data['birthdate'] = "1111/11/11"

    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'birthdate' in response.data

def test_create_passenger_bad_gender(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    data['gender'] = "guy"

    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'gender' in response.data

def test_create_passenger_dup_same_trip(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id

    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['user'] == setup.user.id
    assert response.data['trip'] == setup.trip.id

    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_409_CONFLICT

def test_create_passenger_no_auth(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id

    response = setup.client.post(setup.url_list_create, data=data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_passenger_expired_auth(setup):
    token = setup.user.auth_tokens.latest('timestamp')
    token.timestamp = timezone.now() - timedelta(days=14)
    token.save()

    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id

    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test Passenger List
def test_list_passengers(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    data = deepcopy(PASSENGER_DATA_TWO)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    response = setup.client.get(setup.url_list_create, **setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    assert len(response.data['results']) == 2

    assert 'id' in response.data['results'][0]
    assert 'id' in response.data['results'][1]

def test_list_distinct_passengers(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    new_trip = Trip.objects.create(
        user=setup.user,
        data={"fake": "data"},
        status = TripStatus.objects.create()
    )
    data['trip_id'] = new_trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    response = setup.client.get(setup.url_list_create, **setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    assert 'id' in response.data['results'][0]

def test_list_passengers_no_auth(setup):
    response = setup.client.get(setup.url_list_create)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_list_passengers_expired_auth(setup):
    token = setup.user.auth_tokens.latest('timestamp')
    token.timestamp = timezone.now() - timedelta(days=14)
    token.save()

    response = setup.client.get(setup.url_list_create, **setup.auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test Get Passenger
def test_get_passenger(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    response = setup.client.get(setup.url_get_update(passenger_id), **setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['trip'] == setup.trip.id
    assert response.data['user'] == setup.user.id
    assert response.data['first_name'] == data['first_name']
    assert response.data['last_name'] == data['last_name']

def test_get_passenger_not_exists(setup):
    response = setup.client.get(setup.url_get_update(99999), **setup.auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_passenger_no_auth(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    response = setup.client.get(setup.url_get_update(passenger_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_passenger_expired_auth(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    token = setup.user.auth_tokens.latest('timestamp')
    token.timestamp = timezone.now() - timedelta(days=14)
    token.save()

    response = setup.client.get(setup.url_get_update(passenger_id), **setup.auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test Passenger Update
def test_update_passenger(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    data = deepcopy(PASSENGER_DATA_TWO)
    data['trip_id'] = setup.trip.id
    response = setup.client.patch(setup.url_get_update(passenger_id), data=json.dumps(data),
                            content_type='application/json', **setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['trip'] == setup.trip.id
    assert response.data['user'] == setup.user.id
    assert response.data['first_name'] == data['first_name']
    assert response.data['last_name'] == data['last_name']

def test_update_passenger_bad_birthdate_format(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    data = {"birthdate": "1111/11/11"}
    response = setup.client.patch(setup.url_get_update(passenger_id), data=json.dumps(data),
                            content_type='application/json', **setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'birthdate' in response.data

def test_update_passenger_dup_ppassenger(setup):
    data_one = deepcopy(PASSENGER_DATA_ONE)
    data_one['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data_one, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    data_two = deepcopy(PASSENGER_DATA_TWO)
    data_two['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data_two, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    data = {
        "first_name": data_one['first_name'],
        "last_name": data_one['last_name'],
        "birthdate": data_one['birthdate']
    }
    response = setup.client.patch(setup.url_get_update(passenger_id), data=json.dumps(data),
                            content_type='application/json', **setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_update_passenger_no_auth(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    data = {'first_name': 'not happening'}
    response = setup.client.patch(setup.url_get_update(passenger_id), data=json.dumps(data),
                            content_type='application/json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_passenger_expired_auth(setup):
    data = deepcopy(PASSENGER_DATA_ONE)
    data['trip_id'] = setup.trip.id
    response = setup.client.post(setup.url_list_create, data=data, format='json', **setup.auth)
    assert response.status_code == status.HTTP_201_CREATED

    passenger_id = response.data['id']

    token = setup.user.auth_tokens.latest('timestamp')
    token.timestamp = timezone.now() - timedelta(days=14)
    token.save()

    response = setup.client.patch(setup.url_get_update(passenger_id), data=json.dumps(data),
                            content_type='application/json', **setup.auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN
