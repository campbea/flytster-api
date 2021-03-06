import re

from rest_framework import serializers, status

from .models import FlytsterUser


# Validators
def valid_phone(value):
    if re.match(r'^\d{10}$', value):
        return
    raise serializers.ValidationError('Phone numbers must be 10 digits.')

def valid_password(value):
    long_enough = len(value) >= 8
    contains_digit = bool(re.search(r'[\d]', value))
    if long_enough and contains_digit:
        return
    raise serializers.ValidationError(
        'Passwords must be at least 8 characters and contain at least one digit.')


def valid_verification_token(value):
    if re.match(r'^[abcdefghjkmnopqrstuvwxyz0123456789]{20}$', value):
        return
    raise serializers.ValidationError('{} is not a valid verification token.'.format(value))


def valid_phone_token(value):
    if re.match(r'^[abcdefghjkmnopqrstuvwxyz0123456789]{6}$', value):
        return
    raise serializers.ValidationError('{} is not a valid phone token.'.format(value))


# Custom always-lowercase email field
class LowerEmailField(serializers.EmailField):

    def to_internal_value(self, data):
        value = super(LowerEmailField, self).to_internal_value(data)
        return value.lower()


# Serializers
class RegisterUserSerializer(serializers.Serializer):

    first_name = serializers.CharField(max_length=20)
    last_name = serializers.CharField(max_length=20)
    email = LowerEmailField()
    password = serializers.CharField(min_length=8, validators=[valid_password])


class LoginSerializer(serializers.Serializer):

    email = LowerEmailField()
    password = serializers.CharField(min_length=8, validators=[valid_password])


class UserSerializer(serializers.ModelSerializer):

    email = LowerEmailField()
    phone = serializers.CharField(allow_null=True, validators=[valid_phone])
    email_pending = serializers.SerializerMethodField()
    phone_pending = serializers.SerializerMethodField()

    class Meta:
        model = FlytsterUser
        fields = ('id', 'first_name', 'last_name', 'email', 'phone',
            'email_pending', 'email_verified', 'phone_pending', 'phone_verified',
            'recieve_notifications', 'timestamp')
        read_only_fields = ('email_verified', 'phone_verified')

    def get_email_pending(self, obj):
        if hasattr(obj, 'email_token') and obj.email_token.id and not obj.email_token.is_expired:
            return obj.email_token.email.lower()
        else:
            return None

    def get_phone_pending(self, obj):
        if hasattr(obj, 'phone_token') and obj.phone_token.id and not obj.phone_token.is_expired:
            return obj.phone_token.phone
        else:
            return None

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            email = validated_data.pop('email').lower()
            instance.send_verification_email(email)

        if 'phone' in validated_data and validated_data['phone'] is not None:
            phone = validated_data.pop('phone')
            instance.send_verification_sms(phone)

        return super(UserSerializer, self).update(instance, validated_data)


class UserWithTokenSerializer(UserSerializer):

    token = serializers.SerializerMethodField('get_auth_token')

    class Meta:
        model = FlytsterUser
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'email_verified',
            'phone_verified', 'recieve_notifications', 'token', 'timestamp')
        read_only_fields = ('email_verified', 'phone_verified')

    def get_auth_token(self, obj):
        return obj.auth_tokens.latest('timestamp').token


class VerifyEmailTokenSerializer(serializers.Serializer):

    token = serializers.CharField(min_length=20, max_length=20, validators=[valid_verification_token])


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(min_length=8, validators=[valid_password])
    new_password = serializers.CharField(min_length=8, validators=[valid_password])


class RequestPasswordResetSerializer(serializers.Serializer):

    email = LowerEmailField()


class ResetPasswordSerializer(serializers.Serializer):

    token = serializers.CharField(min_length=20, max_length=20, validators=[valid_verification_token])
    new_password = serializers.CharField(min_length=8, validators=[valid_password])


class VerifyPhoneTokenSerializer(serializers.Serializer):

    token = serializers.CharField(min_length=6, max_length=6, validators=[valid_phone_token])
