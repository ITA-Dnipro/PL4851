import asyncio

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from messaging import services

AUTH_TIMEOUT_SECONDS = 10


def _serialize_message(message):
    return {
        'conversation_id': message['conversation_id'],
        'sender_id': message['sender_id'],
        'body': message['body'],
        'attachments': message['attachments'],
        'status': message['status'],
        'created_at': message['created_at'].isoformat(),
    }


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        self.user = None
        self.joined_conversations = set()
        await self.accept()
        self._auth_timeout_handle = asyncio.get_event_loop().call_later(
            AUTH_TIMEOUT_SECONDS,
            lambda: asyncio.ensure_future(self.close(code=4401)),
        )

    async def disconnect(self, close_code):
        handle = getattr(self, '_auth_timeout_handle', None)
        if handle is not None:
            handle.cancel()

        for group_name in list(self.joined_conversations):
            await self._broadcast_presence(group_name, 'offline')
            await self.channel_layer.group_discard(group_name, self.channel_name)

        if self.authenticated:
            await self.channel_layer.group_discard(
                f'user.{self.user.pk}', self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')

        if not self.authenticated:
            if message_type != 'auth':
                await self.close(code=4401)
                return
            await self._handle_auth(content)
            return

        handler = {
            'join_conversation': self._handle_join_conversation,
            'leave_conversation': self._handle_leave_conversation,
            'send_message': self._handle_send_message,
            'mark_read': self._handle_mark_read,
            'typing': self._handle_typing,
        }.get(message_type)

        if handler is None:
            await self.send_json({'type': 'error', 'detail': 'Unknown message type'})
            return

        try:
            await handler(content)
        except ValueError as exc:
            await self.send_json({'type': 'error', 'detail': str(exc)})
        except Exception:
            await self.send_json({'type': 'error', 'detail': 'Internal error'})

    async def _handle_auth(self, content):
        token = content.get('token')
        user = await self._authenticate(token) if token else None

        if user is None:
            await self.close(code=4401)
            return

        self.user = user
        self.authenticated = True
        handle = getattr(self, '_auth_timeout_handle', None)
        if handle is not None:
            handle.cancel()

        await self.channel_layer.group_add(f'user.{user.pk}', self.channel_name)
        await self.send_json({'type': 'auth_ok'})

    @database_sync_to_async
    def _authenticate(self, token):
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            return JWTAuthentication().get_user(validated_token)
        except (TokenError, InvalidToken):
            return None

    async def _handle_join_conversation(self, content):
        conversation_id = content.get('conversation_id')
        is_member = await sync_to_async(services.is_participant)(
            conversation_id, self.user.pk
        )
        if not is_member:
            raise ValueError('Not a participant of this conversation')

        group_name = f'conversation.{conversation_id}'
        await self.channel_layer.group_add(group_name, self.channel_name)
        self.joined_conversations.add(group_name)
        await self.send_json(
            {'type': 'joined_conversation', 'conversation_id': conversation_id}
        )
        await self._broadcast_presence(group_name, 'online')

    async def _handle_leave_conversation(self, content):
        conversation_id = content.get('conversation_id')
        group_name = f'conversation.{conversation_id}'

        if group_name in self.joined_conversations:
            await self._broadcast_presence(group_name, 'offline')
            await self.channel_layer.group_discard(group_name, self.channel_name)
            self.joined_conversations.discard(group_name)

        await self.send_json(
            {'type': 'left_conversation', 'conversation_id': conversation_id}
        )

    async def _handle_send_message(self, content):
        conversation_id = content.get('conversation_id')
        body = content.get('body')
        attachments = content.get('attachments', [])

        message = await sync_to_async(services.create_message)(
            conversation_id, self.user.pk, body, attachments=attachments
        )
        await self.channel_layer.group_send(
            f'conversation.{conversation_id}',
            {'type': 'message_received', 'message': _serialize_message(message)},
        )

    async def _handle_mark_read(self, content):
        conversation_id = content.get('conversation_id')
        await sync_to_async(services.mark_messages_read)(conversation_id, self.user.pk)
        await self.channel_layer.group_send(
            f'conversation.{conversation_id}',
            {
                'type': 'read_receipt',
                'conversation_id': conversation_id,
                'user_id': self.user.pk,
            },
        )

    async def _handle_typing(self, content):
        conversation_id = content.get('conversation_id')
        group_name = f'conversation.{conversation_id}'
        if group_name not in self.joined_conversations:
            raise ValueError('Join the conversation before sending typing events')

        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'typing',
                'conversation_id': conversation_id,
                'user_id': self.user.pk,
            },
        )

    async def _broadcast_presence(self, group_name, status):
        conversation_id = group_name.removeprefix('conversation.')
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'presence',
                'conversation_id': conversation_id,
                'user_id': self.user.pk,
                'status': status,
            },
        )

    # Channel-layer event handlers (dispatched by the "type" key above).

    async def message_received(self, event):
        await self.send_json({'type': 'message_received', 'message': event['message']})

    async def read_receipt(self, event):
        if event.get('user_id') == getattr(self.user, 'pk', None):
            return
        await self.send_json(
            {
                'type': 'read_receipt',
                'conversation_id': event['conversation_id'],
                'user_id': event['user_id'],
            }
        )

    async def typing(self, event):
        if event.get('user_id') == getattr(self.user, 'pk', None):
            return
        await self.send_json(
            {
                'type': 'typing',
                'conversation_id': event['conversation_id'],
                'user_id': event['user_id'],
            }
        )

    async def presence(self, event):
        if event.get('user_id') == getattr(self.user, 'pk', None):
            return
        await self.send_json(
            {
                'type': 'presence',
                'conversation_id': event['conversation_id'],
                'user_id': event['user_id'],
                'status': event['status'],
            }
        )
