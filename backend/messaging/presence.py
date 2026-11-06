import time
from functools import lru_cache

import redis
from django.conf import settings

PRESENCE_TTL_SECONDS = 60
PRESENCE_REFRESH_INTERVAL_SECONDS = 20


@lru_cache
def get_client():
    return redis.from_url(settings.REDIS_URL)


def _conversation_key(conversation_id, user_id):
    return f'presence:conversation:{conversation_id}:{user_id}'


def mark_conversation_online(conversation_id, user_id, channel_name):
    expires_at = time.time() + PRESENCE_TTL_SECONDS
    get_client().zadd(
        _conversation_key(conversation_id, user_id), {channel_name: expires_at}
    )


def mark_conversation_offline(conversation_id, user_id, channel_name):
    get_client().zrem(_conversation_key(conversation_id, user_id), channel_name)


def is_conversation_online(conversation_id, user_id):
    client = get_client()
    key = _conversation_key(conversation_id, user_id)
    client.zremrangebyscore(key, '-inf', time.time())
    return client.zcard(key) > 0
