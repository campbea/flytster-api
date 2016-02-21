import json
import datetime

from django.conf import settings

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Trip, TripStatus
from .permissions import IsOwner
from .serializers import TripPostSerializer, TripSerializer
from .utils import create_flights_from_trip_option_data, InvalidTripOption


class TripListCreateView(generics.ListCreateAPIView):
    """
    POST: Create a Trip instance from a user's selected flight.
    GET:  Get all Trip instances that are selected and not expired
    """

    model = Trip

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TripPostSerializer
        return TripSerializer

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).filter(
            status__is_selected=True).filter(status__is_expired=False)

    def post(self, request):
        new_trip = self.get_serializer_class()(data=request.data)

        if not new_trip.is_valid():
            return Response(new_trip.errors, status=status.HTTP_400_BAD_REQUEST)

        trip = Trip.objects.create(
            user = request.user,
            status = TripStatus.objects.create(),
            data = new_trip.validated_data['trip_option'])

        try:
             # This takes care of validation and if there is an error the trip is deleted
            create_flights_from_trip_option_data(trip)
        except InvalidTripOption as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        result = TripSerializer(trip)
        return Response(result.data, status=status.HTTP_201_CREATED)


class TripRetrieveView(generics.RetrieveAPIView):
    """
    GET: Retrieve a specific TripSearch instance
    """

    model = Trip
    serializer_class = TripSerializer
    permission_classes = (IsOwner,)
    queryset = Trip.objects.all()
