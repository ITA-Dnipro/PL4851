from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from users.exceptions import EmailNotVerified
from users.services.email_verification import unverified_accounts

INVALID_CREDENTIALS_MESSAGE = 'Invalid email or password'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    remember = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        # Django doesn't authenticate inactive users, so a registration waiting
        # for verification is checked here; the password is still required, so
        # the answer doesn't reveal the account to someone who doesn't know it
        pending = unverified_accounts(attrs['email']).first()
        if pending is not None:
            if pending.check_password(attrs['password']):
                raise EmailNotVerified()
            raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

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
