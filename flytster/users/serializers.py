from rest_framework import serializers, status

from .models import FlytsterUser
from .validators import valid_password, valid_verification_token


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
    email_pending = serializers.SerializerMethodField()

    class Meta:
        model = FlytsterUser
        fields = ('id', 'first_name', 'last_name', 'email',
            'email_pending', 'is_verified', 'timestamp')
        read_only_fields = ('is_verified')

    def get_email_pending(self, obj):
        if hasattr(obj, 'email_token') and obj.email_token.id and not obj.email_token.is_expired:
            return obj.email_token.email.lower()
        else:
            return None

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            email = validated_data.pop('email').lower()
            instance.send_verification_email(email)
        return super(UserSerializer, self).update(instance, validated_data)


class UserWithTokenSerializer(UserSerializer):

    token = serializers.SerializerMethodField('get_auth_token')

    class Meta:
        model = FlytsterUser
        fields = ('id', 'first_name', 'last_name', 'email', 'is_verified', 'token', 'timestamp')
        read_only_fields = ('is_verified')

    def get_auth_token(self, obj):
        return obj.auth_tokens.latest('timestamp').token


class VerifyTokenSerializer(serializers.Serializer):

    token = serializers.CharField(min_length=20, max_length=20, validators=[valid_verification_token])


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(min_length=8, validators=[valid_password])
    new_password = serializers.CharField(min_length=8, validators=[valid_password])


class RequestPasswordResetSerializer(serializers.Serializer):

    email = LowerEmailField()


class ResetPasswordSerializer(serializers.Serializer):

    token = serializers.CharField(min_length=20, max_length=20, validators=[valid_verification_token])
    new_password = serializers.CharField(min_length=8, validators=[valid_password])
