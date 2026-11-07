import logging
import threading

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from notifications.models import Notification

logger = logging.getLogger(__name__)

User = get_user_model()

EMAIL_SUBJECT = 'New message'
MAX_SNIPPET_LENGTH = 140


def notify_new_message(recipient_id, source_user_id, conversation_id, body):
    notification = Notification.objects.create(
        recipient_id=recipient_id,
        source_user_id=source_user_id,
        type=Notification.NotificationType.MESSAGE,
        conversation_id=conversation_id,
        snippet=body[:MAX_SNIPPET_LENGTH],
    )

    try:
        recipient_email = User.objects.get(pk=recipient_id).email
    except User.DoesNotExist:
        return notification

    # Sent on a plain OS thread (not the asgiref thread-sensitive executor)
    # so a slow SMTP server can't stall every other sync_to_async call.
    threading.Thread(
        target=_send_email,
        args=(recipient_email, notification.snippet),
        daemon=True,
    ).start()
    return notification


def _send_email(recipient_email, snippet):
    try:
        send_mail(
            subject=EMAIL_SUBJECT,
            message=f'You have a new message: {snippet}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
        )
    except Exception:
        logger.exception('Failed to send notification email to %s', recipient_email)
