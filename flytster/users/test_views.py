import pytest
pytestmark = pytest.mark.django_db

import json
from datetime import timedelta
from uuid import uuid4

from django.core.urlresolvers import reverse
from django.test import Client
from django.utils import timezone
from rest_framework import status

from users.models import FlytsterUser
from authentication.models import AuthToken, EmailToken, PasswordToken, PhoneToken


class UserSetupFixture:
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


@pytest.fixture(scope="function")
def user_setup():
    return UserSetupFixture()


# Test User Authentication
def test_expired_auth(user_setup):
    token = user_setup.user.auth_tokens.latest('timestamp')
    token.timestamp = timezone.now() - timedelta(days=14)
    token.save()

    url = reverse('get_update_user')
    response = user_setup.client.get(url, **user_setup.auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_no_auth(user_setup):
    url = reverse('get_update_user')
    response = user_setup.client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test User Registration
def test_register_user(user_setup):
    url = reverse('register')
    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'dabbin@gmail.com',
        'password': 'Password1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['token']
    assert response.data['email'] == data['email']

def test_register_user_uppercase_email(user_setup):
    url = reverse('register')
    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'DABBIN@gmail.com',
        'password': 'Password1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['token']
    assert response.data['email'] == 'dabbin@gmail.com'

def test_register_bad_email(user_setup):
    url = reverse('register')
    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'DABBIN',
        'password': 'Password1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_register_no_name(user_setup):
    url = reverse('register')
    data = {
        'email': 'dabbin@gmail.com',
        'password': 'Password1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_register_dup_email(user_setup):
    url = reverse('register')
    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'dabbin@gmail.com',
        'password': 'Password1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'dabbin@gmail.com',
        'password': 'Password1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_409_CONFLICT

def test_register_no_pass(user_setup):
    url = reverse('register')
    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'dabbin@gmail.com'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_register_bad_pass(user_setup):
    url = reverse('register')
    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'dabbin@gmail.com',
        'password': 'Password'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = {
        'first_name': 'Cam',
        'last_name': 'Newton',
        'email': 'dabbin@gmail.com',
        'password': 'Pass1'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# Test User Login
def test_login(user_setup):
    url = reverse('login')
    old_token = user_setup.auth['HTTP_AUTHORIZATION']
    data = {
        'email': 'flyhigh@gmail.com',
        'password': 'Password1',
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['first_name'] == 'Fly'
    assert response.data['last_name'] == 'High'
    assert response.data['id'] == user_setup.user.id
    assert response.data['token'] != old_token

def test_login_user_uppercase_email(user_setup):
    url = reverse('login')
    old_token = user_setup.auth['HTTP_AUTHORIZATION']
    data = {
        'email': 'Flyhigh@gmail.com',
        'password': 'Password1',
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['first_name'] == 'Fly'
    assert response.data['last_name'] == 'High'
    assert response.data['id'] == user_setup.user.id
    assert response.data['token'] != old_token

def test_login_no_old_token(user_setup):
    url = reverse('login')
    old_token = AuthToken.objects.get(user=user_setup.user)
    old_token.delete()
    data = {
        'email': 'Flyhigh@gmail.com',
        'password': 'Password1',
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['first_name'] == 'Fly'
    assert response.data['last_name'] == 'High'
    assert response.data['id'] == user_setup.user.id
    assert 'token' in response.data

def test_login_no_user_email_exists(user_setup):
    url = reverse('login')
    data = {
        'email': 'high@gmail.com',
        'password': 'Password1',
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_login_invalid_email(user_setup):
    url = reverse('login')
    data = {
        'email': 'Flyhigh.com',
        'password': 'Password1',
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_incorrect_pass(user_setup):
    url = reverse('login')
    data = {
        'email': 'Flyhigh@gmail.com',
        'password': 'password1',
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test User Logout
def test_logout(user_setup):
    url = reverse('login')
    data = {
        'email': 'flyhigh@gmail.com',
        'password': 'Password1',
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['token']
    assert response.data['id'] == user_setup.user.id

    auth = {'HTTP_AUTHORIZATION': response.data['token']}
    url = reverse('logout')

    response = user_setup.client.delete(url, **auth)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_double_logout(user_setup):
    url = reverse('logout')

    response = user_setup.client.delete(url, **user_setup.auth)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = user_setup.client.delete(url, **user_setup.auth)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test Get Update User
def test_get_user(user_setup):
    url = reverse('get_update_user')

    response = user_setup.client.get(url, **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['email'] == user_setup.user.email

def test_update_user(user_setup):
    url = reverse('get_update_user')
    data = {'first_name': 'Boomer'}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['first_name'] == 'Boomer'

def test_update_user_email(user_setup):
    url = reverse('get_update_user')
    data = {'email': 'booyah@gmail.com'}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['email'] == user_setup.user.email
    assert response.data['email_pending'] == data['email']

    user = FlytsterUser.objects.get(id=user_setup.user.id)
    user.verify_email_token(user.email_token.token)

    response = user_setup.client.get(url, **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['email'] == data['email']
    assert response.data['email_verified']

def test_update_user_phone(user_setup):
    new_phone = '3174554303'
    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == None

def test_update_user_phone_then_verify(user_setup):
    new_phone = '3174554303'
    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == None

    token = PhoneToken.objects.get(user=user_setup.user).token
    url = reverse('verify_phone')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['phone_verified']
    assert response.data['phone'] == new_phone

    url = reverse('get_update_user')
    data = {'phone': None}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_setup.user.id
    assert response.data['phone_pending'] == None
    assert response.data['phone'] == None

def test_update_user_phone_new_phone(user_setup):
    user_setup.user.phone = '3174554303'
    user_setup.user.phone_verified = True
    user_setup.user.save()

    user_id = user_setup.user.id
    new_phone = '3174554304'

    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_id
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == user_setup.user.phone

def test_update_user_phone_new_phone_old_phone(user_setup):
    user_setup.user.phone = '3174554303'
    user_setup.user.phone_verified = True
    user_setup.user.save()

    user_id = user_setup.user.id
    new_phone = '3174554304'

    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_id
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == user_setup.user.phone

    data = {'phone': user_setup.user.phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_id
    assert response.data['phone_pending'] == None
    assert response.data['phone'] == user_setup.user.phone

def test_update_user_phone_token_changes(user_setup):
    user_setup.user.phone = '3174554303'
    user_setup.user.phone_verified = True
    user_setup.user.save()

    user_id = user_setup.user.id
    new_phone = '3174554304'

    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_id
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == user_setup.user.phone

    token = PhoneToken.objects.get(user=user_setup.user).token

    new_phone = '3174554305'
    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_id
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == user_setup.user.phone

    new_token = PhoneToken.objects.get(user=user_setup.user).token

    assert token != new_token

def test_update_user_phone_bad_data(user_setup):
    new_phone = '10notvalid'
    url = reverse('get_update_user')
    data = {'phone': new_phone}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['phone'][0] == 'Phone numbers must be 10 digits.'

def test_update_user_phone_and_email(user_setup):
    user_setup.user.phone = '3174554303'
    user_setup.user.phone_verified = True
    user_setup.user.save()

    user_id = user_setup.user.id
    new_phone = '3174554304'
    new_email = 'flyhigh2222@gmail.com'

    url = reverse('get_update_user')
    data = {'phone': new_phone, 'email': new_email}

    response = user_setup.client.patch(url, data=json.dumps(data),
                            content_type='application/json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == user_id
    assert response.data['email_pending'] == new_email
    assert response.data['email'] == user_setup.user.email
    assert response.data['phone_pending'] == new_phone
    assert response.data['phone'] == user_setup.user.phone


# Test Email Verification
def test_verify_email(user_setup):
    user_setup.user.send_verification_email('flyhigh2@gmail.com')
    token = EmailToken.objects.get(user=user_setup.user).token
    url = reverse('verify_email')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'flyhigh2@gmail.com'
    assert response.data['email_verified']
    assert response.data['email_pending'] == None


def test_verify_email_bad_token(user_setup):
    user_setup.user.send_verification_email('flyhigh@gmail.com')
    token = '$$$$$$$$$$'
    url = reverse('verify_email')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_verify_email_wrong_token(user_setup):
    user_setup.user.send_verification_email('flyhigh2@gmail.com')
    good_token = EmailToken.objects.get(user=user_setup.user).token
    bad_token = uuid4().hex[:20]
    while good_token == bad_token:
        bad_token = uuid4().hex[:20]
    url = reverse('verify_email')

    data = {'token': bad_token}
    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail']
    assert 'invalid' in response.data['detail'].lower()

def test_verify_email_expired_code(user_setup):
    user_setup.user.send_verification_email('flyhigh2@gmail.com')
    et = EmailToken.objects.get(user=user_setup.user)
    et.timestamp = timezone.now() - timedelta(days=7)
    et.save()
    token = et.token
    url = reverse('verify_email')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code, status.HTTP_404_NOT_FOUND
    assert response.data['detail']
    assert 'expired' in response.data['detail'].lower()

def test_verify_email_no_code(user_setup):
    assert EmailToken.objects.filter(user=user_setup.user).exists() == False
    token = uuid4().hex[:20]
    url = reverse('verify_email')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail']
    assert 'invalid' in response.data['detail'].lower()


# Test Phone Verification
def test_verify_phone(user_setup):
    user_setup.user.send_verification_sms('3174554303')
    token = PhoneToken.objects.get(user=user_setup.user).token

    url = reverse('verify_phone')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['phone_verified']
    assert response.data['phone'] == '3174554303'

def test_verify_phone_bad_token(user_setup):
    user_setup.user.send_verification_sms('3174554303')
    token = '$$$$$$$$$'

    url = reverse('verify_phone')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_verify_phone_wrong_token(user_setup):
    user_setup.user.send_verification_sms('3174554303')
    token = PhoneToken.objects.get(user=user_setup.user).token
    bad_token = uuid4().hex[:6]
    while token == bad_token:
        bad_token = uuid4().hex[:6]

    url = reverse('verify_phone')
    data = {'token': bad_token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail']
    assert 'invalid' in response.data['detail'].lower()

def test_verify_phone_expired_token(user_setup):
    user_setup.user.send_verification_sms('3174554303')
    pt = PhoneToken.objects.get(user=user_setup.user)
    pt.timestamp = timezone.now() - timedelta(days=7)
    pt.save()
    token = pt.token

    url = reverse('verify_phone')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail']
    assert 'expired' in response.data['detail'].lower()

def test_verify_phone_no_token(user_setup):
    url = reverse('verify_phone')
    data = {'token': 'abc123'}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail']
    assert 'does not have' in response.data['detail'].lower()

def test_verify_phone_existing_phone_exists(user_setup):
    user_setup.user.send_verification_sms('3174554303')
    token = PhoneToken.objects.get(user=user_setup.user).token

    new_user = FlytsterUser.objects.create_user(
        first_name='Flytster',
        last_name='LLC',
        email='flytster@gmail.com',
        password='supersecret1',
        phone='3174554303'
    )

    url = reverse('verify_phone')
    data = {'token': token}

    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_409_CONFLICT


# Test User Password Change
def test_change_password(user_setup):
    url = reverse('change_pass')
    data = {
        'old_password': 'Password1',
        'new_password': 'NewPass2',
    }
    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_200_OK

    # refresh user from db
    user = FlytsterUser.objects.get(id=user_setup.user.id)
    assert user.check_password(data['new_password'])

def test_change_password_bad_password(user_setup):
    url = reverse('change_pass')
    data = {
        'old_password': 'Password1',
        'new_password': 'basspassss',
    }
    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_change_password_wrong_old_pass(user_setup):
    url = reverse('change_pass')
    data = {
        'old_password': 'NotTheRightPassword1',
        'new_password': 'NewPassword2',
    }
    response = user_setup.client.post(url, data=data, format='json', **user_setup.auth)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_change_password_no_auth(user_setup):
    url = reverse('change_pass')

    data = {
        'old_password': 'Password1',
        'new_password': 'NewPassword2',
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test User Request Password Change
def test_request_password_reset(user_setup):
    url = reverse('request_pass')
    data = {'email': 'flyhigh@gmail.com'}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    assert 'email' in response.data['detail']

def test_request_password_reset_bad_input(user_setup):
    url = reverse('request_pass')
    data = {'email': 'flyhigh'}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_request_password_reset_non_user(user_setup):
    url = reverse('request_pass')
    data = {'email': 'nonuser@gmail.com'}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test User Reset Password
def test_reset_password(user_setup):
    url = reverse('request_pass')
    data = {'email': user_setup.user.email}
    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    token = PasswordToken.objects.get(user=user_setup.user).token
    old_pass = user_setup.user.password
    url = reverse('reset_pass')
    data = {
        'token': token,
        'new_password': 'NewPassword2'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['token']
    new_pass = FlytsterUser.objects.get(email=user_setup.user.email).password
    assert old_pass != new_pass

def test_reset_password_double(user_setup):
    url = reverse('request_pass')
    data = {'email': user_setup.user.email}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    first_token = PasswordToken.objects.get(user=user_setup.user).token

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    second_token = PasswordToken.objects.get(user=user_setup.user).token
    assert first_token != second_token

def test_reset_pass_bad_code(user_setup):
    url = reverse('request_pass')
    data = {'email': user_setup.user.email}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    url = reverse('reset_pass')
    data = {
        'reset_code': '$$$$$$$$$$$$',
        'new_password': 'NewPassword2'
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_reset_pass_wrong_code(user_setup):
    url = reverse('request_pass')
    data = {'email': user_setup.user.email}
    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    good_token = PasswordToken.objects.get(user=user_setup.user).token
    bad_token = uuid4().hex[:20]
    while good_token == bad_token:
        bad_token = uuid4().hex[:20]

    assert good_token != bad_token

    url = reverse('reset_pass')
    data = {
        'token': bad_token,
        'new_password': 'NewPassword2'
    }
    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_reset_pass_expired_code(user_setup):
    url = reverse('request_pass')
    data = {'email': user_setup.user.email}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    pt = PasswordToken.objects.get(user=user_setup.user)
    pt.timestamp = timezone.now() - timedelta(days=7)
    pt.save()
    url = reverse('reset_pass')
    data = {
        'token': pt.token,
        'new_password': 'NewPassword2'
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_reset_pass_bad_pass(user_setup):
    url = reverse('request_pass')
    data = {'email': user_setup.user.email}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    token = PasswordToken.objects.get(user=user_setup.user).token
    url = reverse('reset_pass')
    data = {
        'token': token,
        'new_password': 'BadNewPass'
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_password_reset_email_case_insensitivity(user_setup):
    url = reverse('request_pass')
    data = {'email': 'FLYHIGH@GMAIL.com'}

    response = user_setup.client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK

    token = PasswordToken.objects.get(user=user_setup.user).token
    old_pass = user_setup.user.password
    url = reverse('reset_pass')
    data = {
        'token': token,
        'new_password': 'NewPassword2'
    }

    response = user_setup.client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['token']
    new_pass = FlytsterUser.objects.get(email=user_setup.user.email).password
    assert old_pass != new_pass
