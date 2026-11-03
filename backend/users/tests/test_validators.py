import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from users.validators import PasswordComplexityValidator

validator = PasswordComplexityValidator()


@pytest.mark.parametrize('password', ['Abcdefg1', 'aB3', 'Craft-2026!'])
def test_accepts_upper_and_lower_latin_letters_with_a_digit(password):
    validator.validate(password)


@pytest.mark.parametrize(
    'password',
    [
        'abcdefg1',  # no uppercase
        'ABCDEFG1',  # no lowercase
        'Abcdefgh',  # no digit
        '12345678',
        '________',
    ],
)
def test_rejects_passwords_missing_a_required_character(password):
    with pytest.raises(ValidationError) as error:
        validator.validate(password)

    assert error.value.code == 'password_too_simple'


@pytest.mark.parametrize('password', ['Пароль-Ok7', 'Craft2026ї', 'ҐAbc1234'])
def test_rejects_cyrillic_letters(password):
    with pytest.raises(ValidationError) as error:
        validator.validate(password)

    assert error.value.code == 'password_has_cyrillic'


def test_is_enabled_in_settings():
    with pytest.raises(ValidationError) as error:
        validate_password('longpassword1')

    assert 'password_too_simple' in [e.code for e in error.value.error_list]


def test_describes_the_rule():
    help_text = validator.get_help_text()

    assert validator.message in help_text
    assert validator.cyrillic_message in help_text
