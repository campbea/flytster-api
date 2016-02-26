from django.db import IntegrityError
from django.conf import settings

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Passenger
from .permissions import IsOwner
from .serializers import (CreatePassengerSerializer, PassengerSerializer)


class ListCreatePassenger(generics.ListCreateAPIView):

    model = Passenger

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePassengerSerializer
        return PassengerSerializer

    def get_queryset(self):
        return Passenger.objects.filter(user=self.request.user).order_by(
            'phone', 'birthdate').distinct('phone', 'birthdate')

    def create(self, request, *args, **kwargs):
        passenger_data = self.get_serializer_class()(data=request.data)
        passenger_data.is_valid(raise_exception=True)

        try:
            passenger_data.validated_data['user'] = request.user
            passenger = Passenger.objects.create(**passenger_data.validated_data)
        except IntegrityError:
            return Response({'detail': 'Passenger with this phone and birthdate already exists for this trip.'},
                status=status.HTTP_409_CONFLICT)

        result = PassengerSerializer(passenger)
        return Response(result.data, status=status.HTTP_201_CREATED)


class GetUpdatePassenger(generics.RetrieveUpdateAPIView):

    model = Passenger
    serializer_class = PassengerSerializer
    permission_classes = (IsOwner,)
    queryset = Passenger.objects.all()
