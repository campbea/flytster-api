import json
import datetime

from django.conf import settings

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from sabre.soap_requests import (start_sabre_session, close_sabre_session,
    check_air_availability, book_air_segment)

from .models import Trip, TripStatus
from .permissions import IsOwnerOrAdmin
from .serializers import TripPostSerializer, TripSerializer
from .utils import create_flights_from_trip_data, InvalidTripOption


class TripListCreateView(generics.ListCreateAPIView):
    """
    POST: Create a Trip instance from a Google QPX tripOption.
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
        new_trip.is_valid(raise_exception=True)

        trip = Trip.objects.create(
            user = request.user,
            status = TripStatus.objects.create(),
            data = new_trip.validated_data['trip_option'])

        try:
            create_flights_from_trip_data(trip)
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
    permission_classes = (IsOwnerOrAdmin,)
    queryset = Trip.objects.all()


class CheckAvailabilityView(generics.RetrieveAPIView):
    """
    POST: Book trip with Sabre
    """
    model = Trip
    serializer_class = TripSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get(self, request, *args, **kwargs):
        trip = self.model.objects.get(pk=kwargs['pk'])

        start_sabre_session()
        check_air_availability('token', trip)

        result = TripSerializer(trip)
        return Response(result.data, status=status.HTTP_200_OK)
