import uuid
from datetime import datetime, timezone

from messaging.mongo import get_conversations_collection, get_messages_collection

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
MAX_PAGE_SIZE = 100


def _validate_pagination(page, page_size):
    if page < 1:
        raise ValueError('page must be >= 1')
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise ValueError(f'page_size must be between 1 and {MAX_PAGE_SIZE}')


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
            'read_receipts': {},
            'meta': meta or {},
        }
    )
    return conversation_id


def _get_conversation_or_raise(conversations, conversation_id):
    conversation = conversations.find_one({'conversation_id': conversation_id})
    if conversation is None:
        raise ValueError(f'Conversation {conversation_id} does not exist')
    return conversation


def create_message(conversation_id, sender_id, body, attachments=None, meta=None):
    conversations = get_conversations_collection()
    conversation = _get_conversation_or_raise(conversations, conversation_id)

    if sender_id not in conversation['participants']:
        raise ValueError(
            f'User {sender_id} is not a participant of conversation {conversation_id}'
        )

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
    conversations.update_one(
        {'conversation_id': conversation_id},
        {'$max': {'last_message_at': now}},
    )
    return message


def get_conversation(conversation_id, page=1, page_size=20):
    _validate_pagination(page, page_size)
    conversations = get_conversations_collection()
    conversation = _get_conversation_or_raise(conversations, conversation_id)

    messages_collection = get_messages_collection()
    query = {'conversation_id': conversation_id}
    total_messages = messages_collection.count_documents(query)
    messages = list(
        messages_collection.find(query)
        .sort([('created_at', -1), ('_id', -1)])
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    return {
        'conversation': conversation,
        'messages': messages,
        'page': page,
        'page_size': page_size,
        'total_messages': total_messages,
    }


def list_conversations_for_user(user_id, page=1, page_size=20):
    _validate_pagination(page, page_size)
    conversations_collection = get_conversations_collection()
    query = {'participants': user_id}
    total_count = conversations_collection.count_documents(query)
    conversations = list(
        conversations_collection.find(query)
        .sort([('last_message_at', -1), ('_id', -1)])
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    return {
        'results': conversations,
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
    }


def mark_messages_read(conversation_id, user_id):
    conversations = get_conversations_collection()
    _get_conversation_or_raise(conversations, conversation_id)

    now = datetime.now(timezone.utc)
    conversations.update_one(
        {'conversation_id': conversation_id},
        {'$set': {f'read_receipts.{user_id}': now}},
    )
    return now


def get_unread_count(conversation_id, user_id):
    conversations = get_conversations_collection()
    conversation = _get_conversation_or_raise(conversations, conversation_id)

    last_read_at = conversation.get('read_receipts', {}).get(str(user_id), EPOCH)
    return get_messages_collection().count_documents(
        {
            'conversation_id': conversation_id,
            'sender_id': {'$ne': user_id},
            'created_at': {'$gt': last_read_at},
        }
    )
