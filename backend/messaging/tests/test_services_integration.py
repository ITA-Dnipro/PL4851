import pytest
from django.contrib.auth import get_user_model

from messaging.mongo import get_conversations_collection, get_messages_collection
from messaging.services import create_conversation, create_message

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_create_conversation_and_create_message_real_mongo():
    user_a = User.objects.create_user(
        email='real-mongo-a@example.com',
        password='Str0ng-pass!',
        first_name='A',
        last_name='A',
        role=User.Role.STARTUP,
    )
    user_b = User.objects.create_user(
        email='real-mongo-b@example.com',
        password='Str0ng-pass!',
        first_name='B',
        last_name='B',
        role=User.Role.STARTUP,
    )

    conversation_id = create_conversation(participants=[user_a.pk, user_b.pk])
    create_message(conversation_id, sender_id=user_a.pk, body='hello')

    stored_message = get_messages_collection().find_one(
        {'conversation_id': conversation_id}
    )
    conv = get_conversations_collection().find_one({'conversation_id': conversation_id})

    assert stored_message['body'] == 'hello'
    assert conv['last_message_at'] == stored_message['created_at']
