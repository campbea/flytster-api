import json
import datetime

from django.conf import settings

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Trip, TripSearch
from .permissions import IsOwner
from .serializers import TripSearchPostSerializer, TripSearchSerializer
from .utils import create_trip_search_from_qpx_trip_option, InvalidTripOption


class TripSearchListCreate(generics.ListCreateAPIView):
    """
    POST: Create a TripSearch instance from a user's selected flight data.
    GET:  Get all TripSearch instances that are not expired
    """

    model = TripSearch

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TripSearchPostSerializer
        return TripSearchSerializer

    def get_queryset(self):
        return self.model.objects.filter(
            user=self.request.user).filter(expiration__gt=datetime.date.today())

    def post(self, request):
        new_trip_search = self.get_serializer_class()(data=request.data)

        if not new_trip_search.is_valid():
            return Response(new_trip_search.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            trip_search = create_trip_search_from_qpx_trip_option(
                request.user, new_trip_search.validated_data['trip_option'])
        except InvalidTripOption as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        result = TripSearchSerializer(trip_search)
        return Response(result.data, status=status.HTTP_201_CREATED)


class TripSearchRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """
    GET: Retrieve a specific TripSearch instance
    DELETE: Delete a TripSearch instance
    """

    model = TripSearch
    serializer_class = TripSearchSerializer
    permission_classes = (IsOwner,)
    queryset = TripSearch.objects.all()
