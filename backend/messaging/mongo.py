from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient


@lru_cache
def get_client() -> MongoClient:
    return MongoClient(settings.MONGO_URI)


def get_db():
    return get_client()[settings.MONGO_DB_NAME]


def get_conversations_collection():
    return get_db()['conversations']


def get_messages_collection():
    return get_db()['messages']
