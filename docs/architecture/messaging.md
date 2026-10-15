# Messaging Subsystem — Architecture & Infra Design

## 1. Context & Scope
- This document proposes a NEW subsystem. As of this writing the project has no
  Redis, MongoDB, Celery/worker, Django Channels, or `notifications` app.
  This doc treats those as additions, not existing integrations.
- Goal: real-time 1:1 and small-group chat, message inbox REST API,
  read receipts/typing/presence, notification fan-out, moderation.

## 2. Why MongoDB for messages, Postgres for everything else
- Messages are high-volume, append-mostly, schema-light (attachments,
  reactions, edit history vary per message) → document store fits naturally,
  avoids wide/sparse Postgres tables and frequent migrations.
- Postgres stays source of truth for Users, Projects, Profiles, Notifications
  (relational integrity, foreign keys to existing `users`/`projects` apps).
- Conversation metadata (participants, permissions) can live in Postgres
  (needs FK integrity with Users/Projects) while message bodies live in Mongo,
  linked by `conversation_id`.

## 3. Channel layer: Redis
- Django Channels requires a channel layer for cross-process pub/sub;
  `channels_redis` backed by Redis is the standard choice.
- Recommended: Redis 7.x, single instance for dev, Sentinel/Cluster for prod.
- Also reusable as Celery broker and cache backend.

## 4. WebSocket routing & auth
- `asgi.py` entrypoint, `ProtocolTypeRouter` splitting `http` vs `websocket`.
- Auth: reuse existing JWT (`djangorestframework-simplejwt`) — token passed
  as query param or Sec-WebSocket-Protocol header at connect time, validated
  in a custom `AuthMiddlewareStack` replacement before `AuthMiddlewareStack`
  hands off to the consumer (JWT doesn't carry Django session cookies).
- Consumer joins a Channels group per conversation (`conversation_<id>`),
  checked against DB membership before allowing `group_add`.

## 5. Message lifecycle
1. Client sends message over WS (or POST /api/messages/ as REST fallback).
2. Consumer validates permissions + sanitizes content.
3. Persist to MongoDB (conversation_id, sender_id, body, attachments, ts).
4. Publish to Redis channel group → fan out to connected participants.
5. Enqueue background job (Celery) to:
   - write a Postgres `Notification` row,
   - push email/webpush if recipient is offline (no active WS connection).

## 6. Scaling & retention
- Mongo: shard by `conversation_id` if volume grows; TTL index for ephemeral
  conversations (optional); archive-to-cold-storage job for old messages.
- Redis: channel layer is not for durability — only pub/sub; message durability
  is MongoDB's job.

## 7. Security
- Auth check on every WS connect and on every group join.
- Sanitize message body (strip/escape HTML) before persisting and before
  broadcast.
- Attachment size/type limits, virus-scan hook placeholder.
- Rate limiting: per-user token bucket (Redis-backed) on message send,
  both WS and REST paths.

## 8. Diagrams
- Sequence: Send → Persist (Mongo) → Publish (Redis) → Deliver (WS) →
  Notify (Celery → Postgres Notification + email/push).
- Flow: Offline user → no active WS in group → Celery task checks presence →
  sends email/push notification.

## 9. Local dev — docker-compose additions
services:
  redis:
    image: redis:7
    ports: ["6379:6379"]
  mongo:
    image: mongo:7
    ports: ["27017:27017"]
    volumes: [mongo_data:/data/db]
  worker:
    build: { context: ., dockerfile: Dockerfile.backend }
    command: celery -A config worker -l info
    depends_on: [redis, mongo, db]
