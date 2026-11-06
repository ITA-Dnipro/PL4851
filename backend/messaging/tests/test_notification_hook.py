import time

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

import messaging.services as services_module
from messaging.presence import mark_conversation_offline, mark_conversation_online
from messaging.services import create_conversation, create_message
from notifications.models import Notification

pytestmark = pytest.mark.django_db

User = get_user_model()


def _wait_until(predicate, timeout=1.0, interval=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


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

    assert _wait_until(lambda: len(mail.outbox) == 1)
    assert mail.outbox[0].to == [user_b.email]


def test_recipient_joined_to_this_conversation_does_not_get_notification(
    user_a, user_b
):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    mark_conversation_online(conversation_id, user_b.pk, 'test-channel')

    create_message(conversation_id, user_a.pk, 'hello there')

    assert not Notification.objects.filter(
        recipient=user_b, conversation_id=conversation_id
    ).exists()
    assert len(mail.outbox) == 0

    mark_conversation_offline(conversation_id, user_b.pk, 'test-channel')


def test_recipient_online_in_other_conversation_still_gets_notification(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    other_conversation_id = create_conversation([user_a.pk, user_b.pk])
    mark_conversation_online(other_conversation_id, user_b.pk, 'test-channel')

    create_message(conversation_id, user_a.pk, 'hello there')

    assert Notification.objects.filter(
        recipient=user_b, conversation_id=conversation_id
    ).exists()
    assert _wait_until(lambda: len(mail.outbox) == 1)

    mark_conversation_offline(other_conversation_id, user_b.pk, 'test-channel')


def test_message_still_persists_if_notification_fails(user_a, user_b, monkeypatch):
    def _boom(*args, **kwargs):
        raise ConnectionError('redis unreachable')

    monkeypatch.setattr(services_module, 'notify_new_message', _boom)

    conversation_id = create_conversation([user_a.pk, user_b.pk])
    message = create_message(conversation_id, user_a.pk, 'hello there')

    assert message['body'] == 'hello there'
    assert not Notification.objects.filter(
        recipient=user_b, conversation_id=conversation_id
    ).exists()


def test_sender_never_gets_notified_about_own_message(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    create_message(conversation_id, user_a.pk, 'hello there')

    assert not Notification.objects.filter(
        recipient=user_a, conversation_id=conversation_id
    ).exists()
