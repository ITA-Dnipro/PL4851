from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from investors.models import MAX_LENGTH_INVESTOR_NAME
from startups.models import MAX_LENGTH_STARTUP_NAME
from users.exceptions import EmailAlreadyRegistered
from users.models import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME

User = get_user_model()

MAX_LENGTH_COMPANY_NAME = min(MAX_LENGTH_STARTUP_NAME, MAX_LENGTH_INVESTOR_NAME)
PASSWORDS_DO_NOT_MATCH_MESSAGE = 'Passwords do not match.'


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=MAX_LENGTH_EMAIL)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
    first_name = serializers.CharField(max_length=MAX_LENGTH_NAME)
    last_name = serializers.CharField(max_length=MAX_LENGTH_NAME)
    company_name = serializers.CharField(max_length=MAX_LENGTH_COMPANY_NAME)
    role = serializers.ChoiceField(choices=User.Role.choices)
    legal_form = serializers.ChoiceField(choices=User.LegalForm.choices)

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise EmailAlreadyRegistered()
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': PASSWORDS_DO_NOT_MATCH_MESSAGE}
            )

        # An unsaved user lets the validators compare the password with the
        # email and names
        user = User(
            email=attrs['email'],
            first_name=attrs['first_name'],
            last_name=attrs['last_name'],
        )
        try:
            validate_password(attrs['password'], user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)})

        return attrs
