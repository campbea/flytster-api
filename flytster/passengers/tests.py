from copy import deepcopy
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from trips.models import Trip, TripStatus
from users.models import FlytsterUser


PASSENGER_DATA_ONE = {
    "trip_id": "this will be replaced with actual trip pk",
    "first_name": "Drew",
    "last_name": "Brees",
    "phone": "0987654321",
    "gender": "M",
    "birthdate": "1979-01-15"
}

PASSENGER_DATA_TWO = {
    "trip_id": "this will be replaced with actual trip pk",
    "first_name": "Matt",
    "last_name": "Ryan",
    "phone": "1234567890",
    "gender": "M",
    "birthdate": "1985-05-17"
}


class PassengerTestMixin(object):

    def setUp(self):
        user = FlytsterUser.objects.create_user(
            first_name='Fly',
            last_name='High',
            email='flyhigh@gmail.com',
            password='Password1'
        )

        assert(user)
        user.verify_email_token(user.email_token.token)

        self.user = user
        self.auth = {'HTTP_AUTHORIZATION': user.auth_tokens.latest('timestamp').token}

        trip = Trip.objects.create(
            user=user,
            data={"fake": "data"},
            status = TripStatus.objects.create()
        )

        assert(trip)
        self.trip = trip

        self.url_list_create = reverse('list_create_passenger')
        self.url_get_update = lambda t: reverse('get_update_passenger', args=[t])


class CreatePassengerTest(PassengerTestMixin, APITestCase):

    def test_create_passenger(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['trip'], self.trip.id)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])

    def test_create_passenger_bad_phone_format(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        data['phone'] = "111-111-1111"

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_create_passenger_bad_phone_num(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        data['phone'] = "11111"

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_create_passenger_bad_birthdate(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        data['birthdate'] = "1111/11/11"

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('birthdate', response.data)

    def test_create_passenger_bad_gender(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        data['gender'] = "guy"

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gender', response.data)

    def test_create_passenger_dup_same_trip(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['trip'], self.trip.id)

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_passenger_no_auth(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id

        response = self.client.post(self.url_list_create, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_passenger_expired_auth(self):
        token = self.user.auth_tokens.latest('timestamp')
        token.timestamp = timezone.now() - timedelta(days=14)
        token.save()

        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id

        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ListPassengerTest(PassengerTestMixin, APITestCase):

    def test_list_passengers(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = deepcopy(PASSENGER_DATA_TWO)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url_list_create, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

        self.assertIn('id', response.data['results'][0])
        self.assertIn('id', response.data['results'][1])

    def test_list_distinct_passengers(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_trip = Trip.objects.create(
            user=self.user,
            data={"fake": "data"},
            status = TripStatus.objects.create()
        )
        data['trip_id'] = new_trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url_list_create, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('id', response.data['results'][0])

    def test_list_passengers_no_auth(self):
        response = self.client.get(self.url_list_create)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_passengers_expired_auth(self):
        token = self.user.auth_tokens.latest('timestamp')
        token.timestamp = timezone.now() - timedelta(days=14)
        token.save()

        response = self.client.get(self.url_list_create, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class GetPassengerTest(PassengerTestMixin, APITestCase):

    def test_get_passenger(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        response = self.client.get(self.url_get_update(passenger_id), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['trip'], self.trip.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])

    def test_get_passenger_not_exists(self):
        response = self.client.get(self.url_get_update(99999), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_passenger_no_auth(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        response = self.client.get(self.url_get_update(passenger_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_passenger_expired_auth(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        token = self.user.auth_tokens.latest('timestamp')
        token.timestamp = timezone.now() - timedelta(days=14)
        token.save()

        response = self.client.get(self.url_get_update(passenger_id), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UpdatePassengerTest(PassengerTestMixin, APITestCase):

    def test_update_passenger(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        data = deepcopy(PASSENGER_DATA_TWO)
        data['trip_id'] = self.trip.id
        response = self.client.patch(self.url_get_update(passenger_id), data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['trip'], self.trip.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])

    def test_update_passenger_bad_phone_format(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        data = {"phone": "111-111-1111"}
        response = self.client.patch(self.url_get_update(passenger_id), data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_update_passenger_bad_birthdate_format(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        data = {"birthdate": "1111/11/11"}
        response = self.client.patch(self.url_get_update(passenger_id), data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('birthdate', response.data)

    def test_update_passenger_dup_phone_birthdate_trip(self):
        data_one = deepcopy(PASSENGER_DATA_ONE)
        data_one['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data_one, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data_two = deepcopy(PASSENGER_DATA_TWO)
        data_two['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data_two, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        data = {"phone": data_one['phone'], "birthdate": data_one['birthdate']}
        response = self.client.patch(self.url_get_update(passenger_id), data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('The fields trip, phone, birthdate must make a unique set.', response.data['detail'][0])

    def test_update_passenger_no_auth(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        data = {'first_name': 'not happening'}
        response = self.client.patch(self.url_get_update(passenger_id), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_passenger_expired_auth(self):
        data = deepcopy(PASSENGER_DATA_ONE)
        data['trip_id'] = self.trip.id
        response = self.client.post(self.url_list_create, data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        passenger_id = response.data['id']

        token = self.user.auth_tokens.latest('timestamp')
        token.timestamp = timezone.now() - timedelta(days=14)
        token.save()

        response = self.client.patch(self.url_get_update(passenger_id), data=data, format='json', **self.auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
