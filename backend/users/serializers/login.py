from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

INVALID_CREDENTIALS_MESSAGE = 'Invalid email or password'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    remember = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            email=attrs['email'],
            password=attrs['password'],
        )

        if user is None:
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

        attrs['user'] = user
        return attrs


class LoginUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='user_id')
    email = serializers.EmailField()
    role = serializers.CharField()
