from rest_framework import serializers, status

from .models import User
from .validators import valid_password


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

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'is_verified', 'timestamp')
        read_only_fields = ('is_verified')


class UserWithTokenSerializer(UserSerializer):

    token = serializers.SerializerMethodField('get_auth_token')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'is_verified', 'token', 'timestamp')
        read_only_fields = ('is_verified')

    def get_auth_token(self, obj):
        return obj.auth_tokens.latest('timestamp').token
