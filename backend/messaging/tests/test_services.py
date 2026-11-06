import mongomock
import pytest
from django.contrib.auth import get_user_model

from messaging import mongo as mongo_module
from messaging.services import (
    create_conversation,
    create_message,
    get_conversation,
    get_unread_count,
    list_conversations_for_user,
    mark_messages_read,
)

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture(autouse=True)
def fake_mongo(monkeypatch):
    client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_module, 'get_client', lambda: client)


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


@pytest.fixture
def user_c():
    return User.objects.create_user(
        email='c@example.com',
        password='Str0ng-pass!',
        first_name='C',
        last_name='C',
        role=User.Role.STARTUP,
    )


def test_create_conversation_and_create_message(user_a, user_b):
    conversation_id = create_conversation(participants=[user_a.pk, user_b.pk])
    message = create_message(conversation_id, sender_id=user_a.pk, body='hello')

    assert message['conversation_id'] == conversation_id

    stored_message = mongo_module.get_messages_collection().find_one(
        {'conversation_id': conversation_id}
    )
    conv = mongo_module.get_conversations_collection().find_one(
        {'conversation_id': conversation_id}
    )
    assert conv['last_message_at'] == stored_message['created_at']


def test_create_message_rejects_unknown_conversation(user_a):
    with pytest.raises(ValueError):
        create_message('does-not-exist', sender_id=user_a.pk, body='hello')


def test_create_message_rejects_non_participant(user_a, user_b):
    conversation_id = create_conversation(participants=[user_a.pk, user_b.pk])

    with pytest.raises(ValueError):
        create_message(conversation_id, sender_id=999, body='hello')


def test_get_conversation_paginates_messages_newest_first(user_a, user_b):
    conversation_id = create_conversation(participants=[user_a.pk, user_b.pk])
    create_message(conversation_id, sender_id=user_a.pk, body='first')
    create_message(conversation_id, sender_id=user_b.pk, body='second')
    create_message(conversation_id, sender_id=user_a.pk, body='third')

    page = get_conversation(conversation_id, page=1, page_size=2)

    assert page['total_messages'] == 3
    assert [m['body'] for m in page['messages']] == ['third', 'second']


def test_list_conversations_for_user_sorted_by_recency(user_a, user_b, user_c):
    conversation_a = create_conversation(participants=[user_a.pk, user_b.pk])
    conversation_b = create_conversation(participants=[user_a.pk, user_c.pk])
    create_message(conversation_a, sender_id=user_a.pk, body='hi')
    create_message(conversation_b, sender_id=user_a.pk, body='hey')

    page = list_conversations_for_user(user_a.pk, page=1, page_size=10)

    assert page['total_count'] == 2
    assert page['results'][0]['conversation_id'] == conversation_b


@pytest.mark.parametrize('page,page_size', [(0, 20), (1, 0), (1, -1), (1, 101)])
def test_get_conversation_rejects_invalid_pagination(page, page_size, user_a, user_b):
    conversation_id = create_conversation(participants=[user_a.pk, user_b.pk])

    with pytest.raises(ValueError):
        get_conversation(conversation_id, page=page, page_size=page_size)


@pytest.mark.parametrize('page,page_size', [(0, 20), (1, 0), (1, -1), (1, 101)])
def test_list_conversations_for_user_rejects_invalid_pagination(
    page, page_size, user_a
):
    with pytest.raises(ValueError):
        list_conversations_for_user(user_a.pk, page=page, page_size=page_size)


def test_mark_messages_read_resets_unread_count(user_a, user_b):
    conversation_id = create_conversation(participants=[user_a.pk, user_b.pk])
    create_message(conversation_id, sender_id=user_a.pk, body='hello')

    assert get_unread_count(conversation_id, user_id=user_b.pk) == 1

    mark_messages_read(conversation_id, user_id=user_b.pk)

    assert get_unread_count(conversation_id, user_id=user_b.pk) == 0
