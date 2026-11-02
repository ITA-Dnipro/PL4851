import mongomock
import pytest

from messaging import mongo as mongo_module
from messaging.services import (
    create_conversation,
    create_message,
    get_conversation,
    get_unread_count,
    list_conversations_for_user,
    mark_messages_read,
)


@pytest.fixture(autouse=True)
def fake_mongo(monkeypatch):
    client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_module, 'get_client', lambda: client)


def test_create_conversation_and_create_message():
    conversation_id = create_conversation(participants=[1, 2])
    message = create_message(conversation_id, sender_id=1, body='hello')

    assert message['conversation_id'] == conversation_id

    stored_message = mongo_module.get_messages_collection().find_one(
        {'conversation_id': conversation_id}
    )
    conv = mongo_module.get_conversations_collection().find_one(
        {'conversation_id': conversation_id}
    )
    assert conv['last_message_at'] == stored_message['created_at']


def test_create_message_rejects_unknown_conversation():
    with pytest.raises(ValueError):
        create_message('does-not-exist', sender_id=1, body='hello')


def test_create_message_rejects_non_participant():
    conversation_id = create_conversation(participants=[1, 2])

    with pytest.raises(ValueError):
        create_message(conversation_id, sender_id=999, body='hello')


def test_get_conversation_paginates_messages_newest_first():
    conversation_id = create_conversation(participants=[1, 2])
    create_message(conversation_id, sender_id=1, body='first')
    create_message(conversation_id, sender_id=2, body='second')
    create_message(conversation_id, sender_id=1, body='third')

    page = get_conversation(conversation_id, page=1, page_size=2)

    assert page['total_messages'] == 3
    assert [m['body'] for m in page['messages']] == ['third', 'second']


def test_list_conversations_for_user_sorted_by_recency():
    conversation_a = create_conversation(participants=[1, 2])
    conversation_b = create_conversation(participants=[1, 3])
    create_message(conversation_a, sender_id=1, body='hi')
    create_message(conversation_b, sender_id=1, body='hey')

    page = list_conversations_for_user(1, page=1, page_size=10)

    assert page['total_count'] == 2
    assert page['results'][0]['conversation_id'] == conversation_b


@pytest.mark.parametrize('page,page_size', [(0, 20), (1, 0), (1, -1), (1, 101)])
def test_get_conversation_rejects_invalid_pagination(page, page_size):
    conversation_id = create_conversation(participants=[1, 2])

    with pytest.raises(ValueError):
        get_conversation(conversation_id, page=page, page_size=page_size)


@pytest.mark.parametrize('page,page_size', [(0, 20), (1, 0), (1, -1), (1, 101)])
def test_list_conversations_for_user_rejects_invalid_pagination(page, page_size):
    with pytest.raises(ValueError):
        list_conversations_for_user(1, page=page, page_size=page_size)


def test_mark_messages_read_resets_unread_count():
    conversation_id = create_conversation(participants=[1, 2])
    create_message(conversation_id, sender_id=1, body='hello')

    assert get_unread_count(conversation_id, user_id=2) == 1

    mark_messages_read(conversation_id, user_id=2)

    assert get_unread_count(conversation_id, user_id=2) == 0
