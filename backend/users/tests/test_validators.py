import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from users.validators import PasswordComplexityValidator

validator = PasswordComplexityValidator()


@pytest.mark.parametrize('password', ['abcdefg1', 'пароль12', 'A1'])
def test_accepts_letters_with_digits(password):
    validator.validate(password)


@pytest.mark.parametrize('password', ['abcdefgh', '12345678', '________'])
def test_rejects_passwords_without_letters_or_digits(password):
    with pytest.raises(ValidationError) as error:
        validator.validate(password)

    assert error.value.code == 'password_too_simple'


def test_is_enabled_in_settings():
    with pytest.raises(ValidationError) as error:
        validate_password('longpassword')

    assert 'password_too_simple' in [e.code for e in error.value.error_list]
