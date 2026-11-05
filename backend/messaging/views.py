from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from messaging import services
from messaging.serializers import (
    ConversationCreateResponseSerializer,
    ConversationCreateSerializer,
    ConversationListResponseSerializer,
    MessageCreateSerializer,
    MessageListResponseSerializer,
    MessageSerializer,
)
from projects.models import Project
from startups.models import StartupProfile


def _parse_pagination(request, default_page_size=20):
    try:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', default_page_size))
    except (TypeError, ValueError):
        raise ValidationError('page and page_size must be integers')
    return page, page_size


def _get_conversation_or_403(conversation_id, user_id):
    conversation = services.get_conversation_meta(conversation_id)
    if conversation is None:
        raise NotFound('Conversation not found')
    if user_id not in conversation['participants']:
        raise PermissionDenied('Not a participant of this conversation')
    return conversation


class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == 'POST':
            self.throttle_scope = 'create_conversation'
            return [ScopedRateThrottle()]
        return []

    @extend_schema(
        summary='List conversations for the current user',
        responses=ConversationListResponseSerializer,
    )
    def get(self, request):
        page, page_size = _parse_pagination(request)
        try:
            result = services.list_conversations_for_user(
                request.user.pk, page, page_size
            )
        except ValueError as exc:
            raise ValidationError(str(exc))

        conversations = result['results']
        project_ids = {c['project_id'] for c in conversations if c.get('project_id')}
        startup_ids = {c['startup_id'] for c in conversations if c.get('startup_id')}
        projects = {p.project_id: p for p in Project.objects.filter(pk__in=project_ids)}
        startups = {
            s.startup_id: s for s in StartupProfile.objects.filter(pk__in=startup_ids)
        }

        enriched = []
        for conv in conversations:
            project = projects.get(conv.get('project_id'))
            startup = startups.get(conv.get('startup_id'))
            enriched.append(
                {
                    'conversation_id': conv['conversation_id'],
                    'participants': conv['participants'],
                    'last_message_at': conv['last_message_at'],
                    'last_message': services.get_last_message(conv['conversation_id']),
                    'unread_count': services.get_unread_count(
                        conv['conversation_id'], request.user.pk
                    ),
                    'project': (
                        {'id': project.project_id, 'title': project.project_title}
                        if project
                        else None
                    ),
                    'startup': (
                        {'id': startup.startup_id, 'name': startup.startup_name}
                        if startup
                        else None
                    ),
                }
            )

        serializer = ConversationListResponseSerializer(
            {
                'results': enriched,
                'page': result['page'],
                'page_size': result['page_size'],
                'total_count': result['total_count'],
            }
        )
        return Response(serializer.data)

    @extend_schema(
        summary='Create a conversation',
        request=ConversationCreateSerializer,
        responses={201: ConversationCreateResponseSerializer},
        examples=[
            OpenApiExample(
                'Create a 1:1 conversation',
                value={'participants': [1, 2], 'project_id': None},
            )
        ],
    )
    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participants = serializer.validated_data['participants']

        if request.user.pk not in participants:
            raise ValidationError('participants must include the requesting user')

        conversation_id = services.create_conversation(
            participants=participants,
            project_id=serializer.validated_data.get('project_id'),
            startup_id=serializer.validated_data.get('startup_id'),
        )
        return Response(
            {'conversation_id': conversation_id}, status=status.HTTP_201_CREATED
        )


class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == 'POST':
            self.throttle_scope = 'send_message'
            return [ScopedRateThrottle()]
        return []

    @extend_schema(
        summary='List messages in a conversation (paginated)',
        responses=MessageListResponseSerializer,
    )
    def get(self, request, conversation_id):
        _get_conversation_or_403(conversation_id, request.user.pk)
        page, page_size = _parse_pagination(request, default_page_size=50)

        try:
            result = services.get_conversation(conversation_id, page, page_size)
        except ValueError as exc:
            raise ValidationError(str(exc))

        serializer = MessageSerializer(result['messages'], many=True)
        return Response(
            {
                'results': serializer.data,
                'page': result['page'],
                'page_size': result['page_size'],
                'total_messages': result['total_messages'],
            }
        )

    @extend_schema(
        summary='Send a message (non-WebSocket fallback)',
        request=MessageCreateSerializer,
        responses={201: MessageSerializer},
        examples=[OpenApiExample('Send a text message', value={'body': 'Hello there'})],
    )
    def post(self, request, conversation_id):
        _get_conversation_or_403(conversation_id, request.user.pk)

        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = services.create_message(
            conversation_id,
            request.user.pk,
            serializer.validated_data['body'],
            attachments=serializer.validated_data.get('attachments', []),
        )
        serialized_message = MessageSerializer(message).data

        async_to_sync(get_channel_layer().group_send)(
            f'conversation.{conversation_id}',
            {'type': 'message_received', 'message': serialized_message},
        )

        return Response(serialized_message, status=status.HTTP_201_CREATED)


class ConversationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Mark all messages in a conversation as read',
        request=None,
        responses={204: None},
    )
    def post(self, request, conversation_id):
        _get_conversation_or_403(conversation_id, request.user.pk)
        services.mark_messages_read(conversation_id, request.user.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
