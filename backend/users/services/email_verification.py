import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    base36_to_int,
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

logger = logging.getLogger(__name__)
User = get_user_model()

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


def unverified_accounts(email):
    """Accounts registered with this email that were never verified.

    A verified account deactivated by an admin keeps its email_verified_at,
    so it is not treated as a pending registration.
    """
    return User.objects.filter(
        email__iexact=email, is_active=False, email_verified_at__isnull=True
    )


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


def user_from_uid(uid):
    """The user from the link's uid, or None for a broken or unknown one."""
    try:
        pk = int(force_str(urlsafe_base64_decode(uid)))
    except (TypeError, ValueError, OverflowError):
        return None
    return User.objects.filter(pk=pk).first()


def verify_email(uid, token):
    """Activates the account from the verification link.

    Returns the user, or None when the link is broken, expired or used.
    A verified account is returned as is, so opening the link again isn't an error.
    """
    user = user_from_uid(uid)
    if user is None:
        return None
    if user.email_verified_at is not None:
        return user
    if not email_verification_token.check_token(user, token):
        return None

    user.is_active = True
    user.email_verified_at = timezone.now()
    user.save(update_fields=['is_active', 'email_verified_at'])
    return user


def resend_verification(email):
    """Sends a new link if the email has a pending registration, otherwise nothing."""
    user = unverified_accounts(email).first()
    if user is not None:
        send_verification(user)
