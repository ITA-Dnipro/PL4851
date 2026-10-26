import uuid
from datetime import datetime, timezone

from messaging.mongo import get_conversations_collection, get_messages_collection


def create_conversation(participants, project_id=None, startup_id=None, meta=None):
    now = datetime.now(timezone.utc)
    conversation_id = str(uuid.uuid4())
    get_conversations_collection().insert_one(
        {
            'conversation_id': conversation_id,
            'participants': participants,
            'project_id': project_id,
            'startup_id': startup_id,
            'created_at': now,
            'last_message_at': now,
            'meta': meta or {},
        }
    )
    return conversation_id


def append_message(conversation_id, sender_id, body, attachments=None, meta=None):
    now = datetime.now(timezone.utc)
    conversations = get_conversations_collection()
    if conversations.find_one({'conversation_id': conversation_id}) is None:
        raise ValueError(f'Conversation {conversation_id} does not exist')

    message = {
        'conversation_id': conversation_id,
        'sender_id': sender_id,
        'body': body,
        'attachments': attachments or [],
        'status': 'sent',
        'created_at': now,
        'meta': meta or {},
    }
    get_messages_collection().insert_one(message)
    conversations.update_one(
        {'conversation_id': conversation_id},
        {'$max': {'last_message_at': now}},
    )
    return message
