import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from notifications.models import Notification

pytestmark = pytest.mark.django_db

User = get_user_model()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user_a():
    return User.objects.create_user(
        email='a@example.com',
        password='Str0ng-pass!',
        first_name='A',
        last_name='A',
        role=User.Role.STARTUP,
    )


@pytest.fixture
def user_b():
    return User.objects.create_user(
        email='b@example.com',
        password='Str0ng-pass!',
        first_name='B',
        last_name='B',
        role=User.Role.STARTUP,
    )


def test_unauthenticated_list_is_rejected():
    client = APIClient()
    response = client.get(reverse('notifications:notification-list'))
    assert response.status_code == 401


def test_list_returns_only_own_notifications(user_a, user_b):
    Notification.objects.create(
        recipient=user_a, source_user=user_b, conversation_id='c1', snippet='hi'
    )
    Notification.objects.create(
        recipient=user_b, source_user=user_a, conversation_id='c2', snippet='hey'
    )

    client = auth_client(user_a)
    response = client.get(reverse('notifications:notification-list'))

    assert response.status_code == 200
    results = response.json()['results']
    assert len(results) == 1
    assert results[0]['conversation_id'] == 'c1'


def test_mark_read(user_a, user_b):
    notification = Notification.objects.create(
        recipient=user_a, source_user=user_b, conversation_id='c1', snippet='hi'
    )

    client = auth_client(user_a)
    response = client.patch(
        reverse(
            'notifications:notification-read',
            kwargs={'notification_id': notification.pk},
        )
    )

    assert response.status_code == 200
    notification.refresh_from_db()
    assert notification.is_read is True


def test_mark_read_other_users_notification_returns_404(user_a, user_b):
    notification = Notification.objects.create(
        recipient=user_b, source_user=user_a, conversation_id='c1', snippet='hi'
    )

    client = auth_client(user_a)
    response = client.patch(
        reverse(
            'notifications:notification-read',
            kwargs={'notification_id': notification.pk},
        )
    )

    assert response.status_code == 404
