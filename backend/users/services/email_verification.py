import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import base36_to_int, urlsafe_base64_encode

logger = logging.getLogger(__name__)

EMAIL_SUBJECT = 'Підтвердження email'


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Signs email verification links; a token stops working after activation."""

    key_salt = 'users.services.email_verification.EmailVerificationTokenGenerator'

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{user.email}{user.is_active}{timestamp}'

    def check_token(self, user, token):
        if not super().check_token(user, token):
            return False

        # The parent class only knows PASSWORD_RESET_TIMEOUT
        timestamp = base36_to_int(token.split('-')[0])
        age = self._num_seconds(self._now()) - timestamp
        return age <= settings.EMAIL_VERIFICATION_TIMEOUT


email_verification_token = EmailVerificationTokenGenerator()


def build_verification_link(uid, token):
    query = urlencode({'uid': uid, 'token': token})
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}/verify-email?{query}'


def send_verification_email(user, uid, token):
    body = render_to_string(
        'users/emails/email_verification.txt',
        {
            'user_name': user.first_name,
            'verification_link': build_verification_link(uid, token),
        },
    )
    send_mail(
        subject=EMAIL_SUBJECT,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_verification(user):
    """Emails the verification link once the transaction is committed."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    def send():
        try:
            send_verification_email(user, uid, token)
        except Exception:
            logger.exception('Failed to send the email verification link')

    transaction.on_commit(send)
