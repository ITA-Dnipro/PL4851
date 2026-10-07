import hashlib
import secrets
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from .models import PasswordResetToken


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token():
    return secrets.token_urlsafe(32)


def create_password_reset_token(user):
    raw_token = generate_token()

    PasswordResetToken.objects.create(
        user=user,
        token_hash=hash_token(raw_token),
        expires_at=timezone.now() + timedelta(hours=1),
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

    if not token.is_valid():
        return None

    token.mark_as_used()
    return token
