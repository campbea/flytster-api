from datetime import date, timedelta
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework import serializers


def is_email(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


def is_password(value):
    long_enough = len(value) >= 8
    contains_digit = bool(re.search(r'[\d]', value))

    return long_enough and contains_digit


def valid_password(value):
    if is_password(value):
        return
    raise serializers.ValidationError(
        'Passwords must be at least 8 characters and contain at least one digit.')
