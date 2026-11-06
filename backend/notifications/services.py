import logging

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
    _send_email(notification)
    return notification


def _send_email(notification):
    try:
        recipient = User.objects.get(pk=notification.recipient_id)
    except User.DoesNotExist:
        return

    send_mail(
        subject=EMAIL_SUBJECT,
        message=f'You have a new message: {notification.snippet}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient.email],
    )
