import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from messaging.presence import get_client, mark_offline, mark_online
from messaging.services import create_conversation, create_message
from notifications.models import Notification

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture(autouse=True)
def _clean_presence():
    client = get_client()
    for key in client.scan_iter(match='presence:*'):
        client.delete(key)


@pytest.fixture
def user_a():
    return User.objects.create_user(
        email='sender@example.com',
        password='Str0ng-pass!',
        first_name='Sender',
        last_name='S',
        role=User.Role.STARTUP,
    )


@pytest.fixture
def user_b():
    return User.objects.create_user(
        email='recipient@example.com',
        password='Str0ng-pass!',
        first_name='Recipient',
        last_name='R',
        role=User.Role.STARTUP,
    )


def test_offline_recipient_gets_notification_and_email(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    create_message(conversation_id, user_a.pk, 'hello there')

    notification = Notification.objects.get(
        recipient=user_b, conversation_id=conversation_id
    )
    assert notification.source_user_id == user_a.pk
    assert notification.type == Notification.NotificationType.MESSAGE
    assert notification.snippet == 'hello there'
    assert notification.is_read is False

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user_b.email]


def test_online_recipient_does_not_get_notification(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    mark_online(user_b.pk, 'test-channel')

    create_message(conversation_id, user_a.pk, 'hello there')

    assert not Notification.objects.filter(
        recipient=user_b, conversation_id=conversation_id
    ).exists()
    assert len(mail.outbox) == 0

    mark_offline(user_b.pk, 'test-channel')


def test_sender_never_gets_notified_about_own_message(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    create_message(conversation_id, user_a.pk, 'hello there')

    assert not Notification.objects.filter(
        recipient=user_a, conversation_id=conversation_id
    ).exists()
