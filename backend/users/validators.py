import re

from django.core.exceptions import ValidationError

# Latin letters only, as in the rule shown on the registration form
HAS_UPPERCASE = re.compile(r'[A-Z]')
HAS_LOWERCASE = re.compile(r'[a-z]')
HAS_DIGIT = re.compile(r'[0-9]')
# The Cyrillic and Cyrillic Supplement blocks, Ukrainian letters included
HAS_CYRILLIC = re.compile(r'[Ѐ-ԯ]')


class PasswordComplexityValidator:
    """Requires an uppercase letter, a lowercase letter and a digit, no Cyrillic."""

    message = (
        'Password must contain at least one uppercase letter (A-Z), '
        'one lowercase letter (a-z) and one digit (0-9).'
    )
    cyrillic_message = 'Password must not contain Cyrillic letters.'

    def validate(self, password, user=None):
        if HAS_CYRILLIC.search(password):
            raise ValidationError(self.cyrillic_message, code='password_has_cyrillic')

        patterns = (HAS_UPPERCASE, HAS_LOWERCASE, HAS_DIGIT)
        if not all(pattern.search(password) for pattern in patterns):
            raise ValidationError(self.message, code='password_too_simple')

    def get_help_text(self):
        return f'{self.message} {self.cyrillic_message}'
