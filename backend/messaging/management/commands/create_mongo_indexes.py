from django.core.management.base import BaseCommand

from messaging.mongo import get_conversations_collection, get_messages_collection


class Command(BaseCommand):
    help = 'Create MongoDB indexes for messaging collections (idempotent).'

    def handle(self, *args, **options):
        messages = get_messages_collection()
        messages.create_index([('conversation_id', 1), ('created_at', 1)])
        # No TTL index: messages are kept indefinitely by default until a
        # retention policy is decided. Add a TTL index on created_at then.

        conversations = get_conversations_collection()
        conversations.create_index('participants')
        conversations.create_index('last_message_at')

        self.stdout.write(self.style.SUCCESS('Mongo indexes created.'))
