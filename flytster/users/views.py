from django.db import IntegrityError
from django.conf import settings

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from authentication.models import AuthToken, InvalidTokenError, PasswordToken

from .models import FlytsterUser
from .serializers import (RegisterUserSerializer, LoginSerializer,
    UserSerializer, UserWithTokenSerializer, VerifyEmailTokenSerializer,
    ChangePasswordSerializer, RequestPasswordResetSerializer, ResetPasswordSerializer,
    VerifyPhoneTokenSerializer)


class RegisterUser(views.APIView):
    """
    POST: Register a new user, creating a user and auth token.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        new_user = RegisterUserSerializer(data=request.data)
        new_user.is_valid(raise_exception=True)

        try:
            user = FlytsterUser.objects.create_user(
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
    POST: Validates email and password, creates a new auth token.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        login = LoginSerializer(data=request.data)
        login.is_valid(raise_exception=True)

        try:
            user = FlytsterUser.objects.get(email__iexact=login.validated_data['email'])
        except FlytsterUser.DoesNotExist:
            error = {'detail': 'No user with that email was found.'}
            return Response(error, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(login.validated_data['password']):
            error = {'detail': 'The password is invalid.'}
            return Response(error, status=status.HTTP_403_FORBIDDEN)

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

    model = FlytsterUser
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class VerifyUserEmail(views.APIView):
    """
    POST: If the token is valid, verifies a user's email.
    """

    def post(self, request):
        token = VerifyEmailTokenSerializer(data=request.data)
        token.is_valid(raise_exception=True)

        try:
            request.user.verify_email_token(token.validated_data['token'])
        except InvalidTokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        result = UserSerializer(request.user)
        return Response(result.data, status=status.HTTP_200_OK)


class ChangePassword(views.APIView):
    """
    POST: Change a user's password while user is logged in.
    """

    def post(self, request):
        passwords = ChangePasswordSerializer(data=request.data)
        passwords.is_valid(raise_exception=True)

        if not request.user.check_password(passwords.validated_data['old_password']):
            return Response(
                {'old_password': 'Incorrect user password.'},
                status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(passwords.validated_data['new_password'])
        request.user.save()

        return Response(status=status.HTTP_200_OK)


class RequestPasswordReset(views.APIView):
    """
    POST: Generates a request token for a user and sends it via email
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        user_email = RequestPasswordResetSerializer(data=request.data)
        user_email.is_valid(raise_exception=True)

        try:
            user = FlytsterUser.objects.get(email__iexact=user_email.validated_data['email'])
        except FlytsterUser.DoesNotExist:
            return Response(
                {'detail': 'A user with that email could not be found.'},
                status=status.HTTP_404_NOT_FOUND)

        user.request_password_reset()

        return Response(
            {'detail': 'A reset code has been sent to your email address.'},
            status=status.HTTP_200_OK)


class ResetPassword(views.APIView):
    """
    POST: If the provided token is valid, resets a user's password and logs them in.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        reset_data = ResetPasswordSerializer(data=request.data)
        reset_data.is_valid(raise_exception=True)

        try:
            token = PasswordToken.objects.select_related(
                'user').get(token=reset_data.validated_data['token'])
        except PasswordToken.DoesNotExist:
            return Response(
                {'detail': 'Invalid token for this user.'},
                status=status.HTTP_404_NOT_FOUND)

        if token.is_expired:
            return Response(
                {'detail': 'The given token has expired.'},
                status=status.HTTP_404_NOT_FOUND)

        user = token.user
        user.set_password(reset_data.validated_data['new_password'])
        user.save()
        user.login()
        token.delete()

        result = UserWithTokenSerializer(user)
        return Response(result.data, status=status.HTTP_200_OK)


class VerifyPhone(views.APIView):
    """
    POST: If the provided token is valid, verifies a user's phone number.
    """

    def post(self, request):
        verify = VerifyPhoneTokenSerializer(data=request.data)
        verify.is_valid(raise_exception=True)

        try:
            request.user.verify_phone(verify.validated_data['token'])
        except InvalidTokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response(
                {'detail': 'That phone number is already verified by another user.'},
                status=status.HTTP_409_CONFLICT)

        result = UserSerializer(request.user)
        return Response(result.data, status=status.HTTP_200_OK)
