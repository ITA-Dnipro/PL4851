import time

import pytest
from django.contrib.auth import get_user_model

import notifications.services as services_module
from notifications.models import Notification
from notifications.services import notify_new_message

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def recipient():
    return User.objects.create_user(
        email='recipient@example.com',
        password='Str0ng-pass!',
        first_name='R',
        last_name='R',
        role=User.Role.STARTUP,
    )


def test_notify_new_message_does_not_block_on_slow_email(recipient, monkeypatch):
    def _slow_send_mail(*args, **kwargs):
        time.sleep(0.3)

    monkeypatch.setattr(services_module, 'send_mail', _slow_send_mail)

    start = time.monotonic()
    notify_new_message(
        recipient.pk, source_user_id=None, conversation_id='c1', body='hi'
    )
    elapsed = time.monotonic() - start

    assert elapsed < 0.2


def test_notify_new_message_creates_notification_row(recipient):
    notification = notify_new_message(
        recipient.pk, source_user_id=None, conversation_id='c1', body='hi there'
    )

    assert notification.pk is not None
    assert Notification.objects.filter(pk=notification.pk).exists()
