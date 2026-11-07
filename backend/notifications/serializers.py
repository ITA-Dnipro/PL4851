from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'notification_id',
            'type',
            'source_user',
            'conversation_id',
            'snippet',
            'is_read',
            'created_at',
        ]
        read_only_fields = fields
