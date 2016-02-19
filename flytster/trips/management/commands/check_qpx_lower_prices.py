import datetime

from django.conf import settings
# from django.core.mail import send_mail
from django.core.management.base import BaseCommand
# ]from django.template.loader import render_to_string

from trips.models import Trip


class Command(BaseCommand):

    def handle(self, *args, **options):
        upcoming_trips = Trip.objects.filter(expiration__lt=datetime.date.today())

        if upcoming_trips:
            # 1. For each trip check google QPX if trip price is cheaper
            # 2. If price is cheaper than current cheapest_price save as new cheapest_price and send user update
            print("upcoming_trips")
