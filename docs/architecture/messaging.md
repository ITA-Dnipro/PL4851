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
- Auth: connection is accepted over WSS, but the socket stays unauthenticated
  until the client sends a first `auth` message containing the existing JWT
  (`djangorestframework-simplejwt`). No bearer token is ever placed in the
  connection URL/query string — WS handshake URLs are frequently retained in
  proxy/access logs, which would leak a still-valid token. No other message
  type is processed until the `auth` message has been validated; unauthenticated
  or invalid-token sockets are closed.
- Auth deadline: the client has a fixed window (e.g. 10s) after connect to
  send the `auth` message. If it has not arrived (or failed validation) by
  then, the consumer closes the socket. This bounds how long an
  unauthenticated connection can be held open and prevents it being used to
  exhaust server connection capacity.
- Consumer joins a Channels group per conversation (`conversation_<id>`) only
  after auth succeeds, checked against DB membership before allowing `group_add`.

## 5. Message lifecycle
1. Client sends message over WS (authenticated connection, see §4), or
   POST /api/messages/ as REST fallback.
2. Both entry points — the WS consumer and the REST view — run the same
   checks via a shared service: authenticate the request, verify the sender
   is a participant of the conversation, apply per-user rate limiting, then
   validate/sanitize the message content. Neither path persists content that
   skipped this service.
3. Persist to MongoDB (conversation_id, sender_id, body, attachments, ts).
4. Publish to Redis channel group → fan out to connected participants.
5. Enqueue background job (Celery) to:
   - write a Postgres `Notification` row,
   - push email/webpush if recipient is offline (see §6.1 for presence).

### 5.1 Failure recovery
- Redis channel-layer delivery is fire-and-forget: a client disconnected at
  publish time simply misses that broadcast. Reconnecting clients must not
  rely on the channel layer to "catch up" — instead, the REST inbox endpoint
  supports cursor-based pagination (`?after_id=<last_seen_message_id>`), and
  clients fetch everything after their last known message id on (re)connect.
- Celery notification jobs must be durable against worker/process crashes:
  use an outbox pattern (write a `pending` outbox row in the same DB
  transaction as the triggering event, have a reconciler/retry task sweep
  unprocessed outbox rows) or Celery's own ack-late + retry semantics with
  idempotent task bodies, so a crash mid-task does not silently drop the
  Notification row or the offline email/push delivery.

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

## 6.1 Presence
- Channels groups are broadcast-only pub/sub — there is no API to enumerate
  who is currently a member of `conversation_<id>`, so presence cannot be
  derived from group membership.
- Presence is tracked in a separate registry: on successful auth, the
  consumer writes a Redis key (e.g. `presence:<user_id>:<channel_name>`) with
  a short TTL, refreshed by a periodic heartbeat/ping from the client; the
  key expires automatically if the connection drops without a clean close.
- The Celery notification task queries this registry (not the Channels
  group) to decide whether the recipient has any live connection before
  deciding to send an offline email/push notification.

## 8. Diagrams
- Sequence: Send → Persist (Mongo) → Publish (Redis) → Deliver (WS) →
  Notify (Celery → Postgres Notification + email/push).
- Flow: Offline user → presence registry has no live key for the user →
  Celery task sends email/push notification.

## 9. Local dev — docker-compose additions

Merge these into the existing `docker-compose.yml` (add the new services, and
merge `mongo_data` into the existing top-level `volumes:` map alongside
`postgres_data`):

```yaml
services:
  redis:
    image: redis:7
    ports: ["127.0.0.1:6379:6379"]
  mongo:
    image: mongo:7
    ports: ["127.0.0.1:27017:27017"]
    volumes: [mongo_data:/data/db]
  worker:
    build: { context: ., dockerfile: Dockerfile.backend }
    command: celery -A config worker -l info
    depends_on: [redis, mongo, db]

volumes:
  mongo_data:
```
