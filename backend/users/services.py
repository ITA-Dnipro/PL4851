import hashlib
import logging
import secrets
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from .metrics import increment_metric
from .models import PasswordResetToken

PASSWORD_RESET_TOKEN_LIFETIME = timedelta(hours=1)


logger = logging.getLogger(__name__)


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token():
    return secrets.token_urlsafe(32)


@transaction.atomic
def create_password_reset_token(user):
    PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True,
        revoked=False,
    ).delete()
    raw_token = generate_token()

    PasswordResetToken.objects.create(
        user=user,
        token_hash=hash_token(raw_token),
        expires_at=timezone.now() + PASSWORD_RESET_TOKEN_LIFETIME,
    )

    return raw_token


@transaction.atomic
def consume_password_reset_token(raw_token):
    token_hash = hash_token(raw_token)

    try:
        token = PasswordResetToken.objects.select_for_update().get(
            token_hash=token_hash,
        )
    except ObjectDoesNotExist:
        return None

    if token.used_at is not None:
        increment_metric('reused_attempts')
        logger.warning(
            'password_reset_token_reused',
            extra={
                'event': 'password_reset_token_reused',
                'timestamp': timezone.now().isoformat(),
            },
        )
        return None

    if token.expires_at <= timezone.now():
        increment_metric('expired_attempts')
        logger.warning(
            'password_reset_token_expired',
            extra={
                'event': 'password_reset_token_expired',
                'timestamp': timezone.now().isoformat(),
            },
        )
        return None

    if not token.is_valid():
        return None

    token.mark_as_used()
    increment_metric('confirms')
    return token
