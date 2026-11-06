import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from config.asgi import application
from messaging.presence import get_client
from messaging.services import create_conversation
from notifications.models import Notification

pytestmark = [pytest.mark.websocket, pytest.mark.django_db(transaction=True)]

User = get_user_model()


async def _connect_authenticated(user):
    communicator = WebsocketCommunicator(application, '/ws/chat/')
    connected, _ = await communicator.connect()
    assert connected

    token = str(AccessToken.for_user(user))
    await communicator.send_json_to({'type': 'auth', 'token': token})
    response = await communicator.receive_json_from()
    assert response == {'type': 'auth_ok'}

    return communicator


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        email='alice@example.com',
        password='Str0ng-pass!',
        first_name='Alice',
        last_name='A',
        role=User.Role.STARTUP,
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        email='bob@example.com',
        password='Str0ng-pass!',
        first_name='Bob',
        last_name='B',
        role=User.Role.STARTUP,
    )


async def test_rejects_unauthenticated_non_auth_messages():
    communicator = WebsocketCommunicator(application, '/ws/chat/')
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to(
        {'type': 'join_conversation', 'conversation_id': 'x'}
    )

    with pytest.raises(Exception):
        await communicator.receive_json_from()

    await communicator.disconnect()


async def test_rejects_invalid_token():
    communicator = WebsocketCommunicator(application, '/ws/chat/')
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({'type': 'auth', 'token': 'garbage'})

    close_message = await communicator.receive_output()
    assert close_message['type'] == 'websocket.close'
    assert close_message['code'] == 4401

    await communicator.disconnect()


async def test_send_message_persists_and_broadcasts(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk, user_b.pk])

    sender = await _connect_authenticated(user_a)
    receiver = await _connect_authenticated(user_b)

    await sender.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    assert await sender.receive_json_from() == {
        'type': 'joined_conversation',
        'conversation_id': conversation_id,
    }

    await receiver.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    assert await receiver.receive_json_from() == {
        'type': 'joined_conversation',
        'conversation_id': conversation_id,
    }
    await sender.receive_json_from()

    await sender.send_json_to(
        {'type': 'send_message', 'conversation_id': conversation_id, 'body': 'hello'}
    )

    event = await receiver.receive_json_from()
    assert event['type'] == 'message_received'
    assert event['message']['body'] == 'hello'
    assert event['message']['sender_id'] == user_a.pk

    await sender.disconnect()
    await receiver.disconnect()


async def test_rest_send_message_broadcasts_to_websocket_participants(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk, user_b.pk])

    receiver = await _connect_authenticated(user_b)
    await receiver.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    assert await receiver.receive_json_from() == {
        'type': 'joined_conversation',
        'conversation_id': conversation_id,
    }

    def _post_message():
        client = APIClient()
        client.force_authenticate(user=user_a)
        return client.post(
            reverse(
                'messaging:message-list',
                kwargs={'conversation_id': conversation_id},
            ),
            {'body': 'hello from REST'},
            format='json',
        )

    response = await sync_to_async(_post_message)()
    assert response.status_code == 201

    event = await receiver.receive_json_from()
    assert event['type'] == 'message_received'
    assert event['message']['body'] == 'hello from REST'
    assert event['message']['sender_id'] == user_a.pk

    await receiver.disconnect()


async def test_rejects_non_object_json_frame():
    communicator = WebsocketCommunicator(application, '/ws/chat/')
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to(['not', 'an', 'object'])

    response = await communicator.receive_json_from()
    assert response == {'type': 'error', 'detail': 'Invalid message'}

    await communicator.disconnect()


async def test_rejects_token_for_inactive_user(user_a):
    communicator = WebsocketCommunicator(application, '/ws/chat/')
    connected, _ = await communicator.connect()
    assert connected

    token = str(AccessToken.for_user(user_a))
    await _db(_deactivate, user_a)

    await communicator.send_json_to({'type': 'auth', 'token': token})

    with pytest.raises(Exception):
        await communicator.receive_json_from()

    await communicator.disconnect()


async def test_rejects_non_string_conversation_id(user_a, user_b):
    communicator = await _connect_authenticated(user_a)

    await communicator.send_json_to(
        {'type': 'join_conversation', 'conversation_id': {'$ne': None}}
    )

    response = await communicator.receive_json_from()
    assert response['type'] == 'error'

    await communicator.disconnect()


def _deactivate(user):
    user.is_active = False
    user.save(update_fields=['is_active'])


async def test_join_rejects_non_participant(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk])

    communicator = await _connect_authenticated(user_b)
    await communicator.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )

    response = await communicator.receive_json_from()
    assert response['type'] == 'error'

    await communicator.disconnect()


async def test_mark_read_rejects_non_participant(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk])

    communicator = await _connect_authenticated(user_b)
    await communicator.send_json_to(
        {'type': 'mark_read', 'conversation_id': conversation_id}
    )

    response = await communicator.receive_json_from()
    assert response['type'] == 'error'

    await communicator.disconnect()


async def test_mark_read_emits_read_receipt(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk, user_b.pk])

    sender = await _connect_authenticated(user_a)
    receiver = await _connect_authenticated(user_b)

    await sender.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    await sender.receive_json_from()
    await receiver.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    await receiver.receive_json_from()
    await sender.receive_json_from()  # presence from receiver joining

    await receiver.send_json_to(
        {'type': 'mark_read', 'conversation_id': conversation_id}
    )

    event = await sender.receive_json_from()
    assert event == {
        'type': 'read_receipt',
        'conversation_id': conversation_id,
        'user_id': user_b.pk,
    }

    await sender.disconnect()
    await receiver.disconnect()


async def test_connected_recipient_gets_no_notification(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk, user_b.pk])

    sender = await _connect_authenticated(user_a)
    receiver = await _connect_authenticated(user_b)

    await sender.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    await sender.receive_json_from()
    await receiver.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    await receiver.receive_json_from()
    await sender.receive_json_from()  # presence from receiver joining

    await sender.send_json_to(
        {'type': 'send_message', 'conversation_id': conversation_id, 'body': 'hi'}
    )
    await receiver.receive_json_from()

    exists = await _db(
        lambda: Notification.objects.filter(
            recipient=user_b, conversation_id=conversation_id
        ).exists()
    )
    assert exists is False

    await sender.disconnect()
    await receiver.disconnect()


async def test_disconnected_recipient_gets_notification(user_a, user_b):
    conversation_id = await _db(create_conversation, [user_a.pk, user_b.pk])

    sender = await _connect_authenticated(user_a)
    await sender.send_json_to(
        {'type': 'join_conversation', 'conversation_id': conversation_id}
    )
    await sender.receive_json_from()

    await sender.send_json_to(
        {'type': 'send_message', 'conversation_id': conversation_id, 'body': 'hi'}
    )
    # the group_send echoes back to the sender too; use it as a sync point
    await sender.receive_json_from()

    exists = await _db(
        lambda: Notification.objects.filter(
            recipient=user_b, conversation_id=conversation_id
        ).exists()
    )
    assert exists is True

    await sender.disconnect()


@pytest.fixture(autouse=True)
def _clean_presence():
    client = get_client()
    for key in client.scan_iter(match='presence:*'):
        client.delete(key)


async def _db(func, *args, **kwargs):
    from asgiref.sync import sync_to_async

    return await sync_to_async(func)(*args, **kwargs)
