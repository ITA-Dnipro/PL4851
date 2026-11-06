from django.conf import settings
from django.db import models

MAX_LENGTH_SNIPPET = 255
MAX_LENGTH_CONVERSATION_ID = 36


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        MESSAGE = 'message', 'Message'

    notification_id = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    source_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.MESSAGE,
    )
    conversation_id = models.CharField(
        max_length=MAX_LENGTH_CONVERSATION_ID, blank=True
    )
    snippet = models.CharField(max_length=MAX_LENGTH_SNIPPET, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['recipient', 'is_read', '-created_at'],
                name='notification_inbox_idx',
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.type} -> {self.recipient_id}'
