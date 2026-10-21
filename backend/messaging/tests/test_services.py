import mongomock
import pytest

from messaging import mongo as mongo_module
from messaging.services import append_message, create_conversation


@pytest.fixture(autouse=True)
def fake_mongo(monkeypatch):
    client = mongomock.MongoClient()
    monkeypatch.setattr(mongo_module, 'get_client', lambda: client)


def test_create_conversation_and_append_message():
    conversation_id = create_conversation(participants=[1, 2])
    message = append_message(conversation_id, sender_id=1, body='hello')

    assert message['conversation_id'] == conversation_id

    stored_message = mongo_module.get_messages_collection().find_one(
        {'conversation_id': conversation_id}
    )
    conv = mongo_module.get_conversations_collection().find_one(
        {'conversation_id': conversation_id}
    )
    assert conv['last_message_at'] == stored_message['created_at']
