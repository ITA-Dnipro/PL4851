from functools import lru_cache

import redis
from django.conf import settings

PRESENCE_TTL_SECONDS = 60


@lru_cache
def get_client():
    return redis.from_url(settings.REDIS_URL)


def _key(user_id, channel_name):
    return f'presence:{user_id}:{channel_name}'


def mark_online(user_id, channel_name):
    get_client().set(_key(user_id, channel_name), '1', ex=PRESENCE_TTL_SECONDS)


def mark_offline(user_id, channel_name):
    get_client().delete(_key(user_id, channel_name))


def is_online(user_id):
    pattern = _key(user_id, '*')
    return next(get_client().scan_iter(match=pattern, count=10), None) is not None
