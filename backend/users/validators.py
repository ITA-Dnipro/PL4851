import re

from django.core.exceptions import ValidationError

HAS_LETTER = re.compile(r'[^\W\d_]')
HAS_DIGIT = re.compile(r'\d')


class PasswordComplexityValidator:
    """Requires at least one letter and one digit in the password."""

    message = 'Password must contain at least one letter and one digit.'

    def validate(self, password, user=None):
        if not HAS_LETTER.search(password) or not HAS_DIGIT.search(password):
            raise ValidationError(self.message, code='password_too_simple')

    def get_help_text(self):
        return self.message
