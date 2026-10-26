from messaging.mongo import get_conversations_collection, get_messages_collection
from messaging.services import create_conversation, create_message


def test_create_conversation_and_create_message_real_mongo():
    conversation_id = create_conversation(participants=[1, 2])
    create_message(conversation_id, sender_id=1, body='hello')

    stored_message = get_messages_collection().find_one(
        {'conversation_id': conversation_id}
    )
    conv = get_conversations_collection().find_one({'conversation_id': conversation_id})

    assert stored_message['body'] == 'hello'
    assert conv['last_message_at'] == stored_message['created_at']
