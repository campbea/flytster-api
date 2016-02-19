from django.db import IntegrityError
from django.conf import settings

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from authentication.models import AuthToken

from .models import User
from .serializers import (RegisterUserSerializer, LoginSerializer,
    UserSerializer, UserWithTokenSerializer)
from .validators import is_email


class RegisterUser(views.APIView):
    """
    POST: Register a new user, creating a user and auth token.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        new_user = RegisterUserSerializer(data=request.data)

        if not new_user.is_valid():
            return Response(new_user.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                        first_name=new_user.validated_data['first_name'],
                        last_name=new_user.validated_data['last_name'],
                        email=new_user.validated_data['email'],
                        password=new_user.validated_data['password'])
        except IntegrityError:
            return Response({'detail': 'This email already exists.'}, status=status.HTTP_409_CONFLICT)

        result = UserWithTokenSerializer(user)
        return Response(result.data, status=status.HTTP_201_CREATED)


class LoginUser(views.APIView):
    """
    POST: Validates email and password, creates a new auth token, and returns
    the user and token.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        login = LoginSerializer(data=request.data)

        if not login.is_valid():
            return Response(login.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=login.validated_data['email'])
        except User.DoesNotExist:
            error = {'detail': 'No user with that email was found.'}
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(login.validated_data['password']):
            error = {'detail': 'The password is invalid.'}
            return Response(error, status=status.HTTP_401_UNAUTHORIZED)

        user.login()

        result = UserWithTokenSerializer(user)
        return Response(result.data, status=status.HTTP_200_OK)


class LogoutUser(views.APIView):
    """
    DELETE: Logs out a user and deletes their auth token.
    """

    def delete(self, request):
        token = AuthToken.objects.get(token=request.auth)
        token.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class GetUpdateUser(generics.RetrieveUpdateAPIView):
    """
    GET: Retrieves the user's existing profile information.
    PUT/PATCH: Updates a user's profile information.
    """

    model = User
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
