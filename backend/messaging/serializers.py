from django.contrib.auth import get_user_model
from rest_framework import serializers

from projects.models import Project
from startups.models import StartupProfile

User = get_user_model()


class ConversationCreateSerializer(serializers.Serializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    project_id = serializers.IntegerField(required=False, allow_null=True)
    startup_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_participants(self, value):
        unique_ids = set(value)
        if len(unique_ids) < 2:
            raise serializers.ValidationError(
                'participants must include at least 2 distinct users'
            )
        existing_ids = set(
            User.objects.filter(pk__in=unique_ids).values_list('user_id', flat=True)
        )
        missing_ids = unique_ids - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f'Unknown user ids: {sorted(missing_ids)}'
            )
        return list(unique_ids)

    def validate_project_id(self, value):
        if value is None:
            return value
        is_visible = (
            Project.objects.exclude(status=Project.ProjectStatus.DRAFT)
            .filter(pk=value)
            .exists()
        )
        if not is_visible:
            raise serializers.ValidationError('Unknown or inaccessible project_id')
        return value

    def validate_startup_id(self, value):
        if value is None:
            return value
        is_visible = StartupProfile.objects.filter(pk=value, is_verified=True).exists()
        if not is_visible:
            raise serializers.ValidationError('Unknown or inaccessible startup_id')
        return value


class MessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=4000, allow_blank=False)
    attachments = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )


class MessageSerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    sender_id = serializers.IntegerField()
    body = serializers.CharField()
    attachments = serializers.ListField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class ConversationSummarySerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    participants = serializers.ListField(child=serializers.IntegerField())
    last_message_at = serializers.DateTimeField()
    last_message = MessageSerializer(allow_null=True)
    unread_count = serializers.IntegerField()
    project = serializers.DictField(allow_null=True)
    startup = serializers.DictField(allow_null=True)


class ConversationListResponseSerializer(serializers.Serializer):
    results = ConversationSummarySerializer(many=True)
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_count = serializers.IntegerField()


class ConversationCreateResponseSerializer(serializers.Serializer):
    conversation_id = serializers.CharField()


class MessageListResponseSerializer(serializers.Serializer):
    results = MessageSerializer(many=True)
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_messages = serializers.IntegerField()
