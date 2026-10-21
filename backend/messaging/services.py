import uuid
from datetime import datetime, timezone

from messaging.mongo import get_conversations_collection, get_messages_collection


def create_conversation(participants, project_id=None, startup_id=None, meta=None):
    now = datetime.now(timezone.utc)
    conversation_id = str(uuid.uuid4())
    get_conversations_collection().insert_one({
        'conversation_id': conversation_id,
        'participants': participants,
        'project_id': project_id,
        'startup_id': startup_id,
        'created_at': now,
        'last_message_at': now,
        'meta': meta or {},
    })
    return conversation_id


def append_message(conversation_id, sender_id, body, attachments=None, meta=None):
    now = datetime.now(timezone.utc)
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
    get_conversations_collection().update_one(
        {'conversation_id': conversation_id},
        {'$set': {'last_message_at': now}},
    )
    return message
