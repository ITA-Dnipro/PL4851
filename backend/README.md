# Backend

Django + Django REST Framework API.

## Requirements

- Python 3.11

## Setup

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # app deps + linters/formatters
cp .env.example .env
```

Fill in `SECRET_KEY` in `.env`. See [Database](#database) below.

Code style and pre-commit hooks are described in the [root README](../README.md#code-style--linting).

## Database

By default (empty `DB_NAME`) the project uses SQLite — no setup needed.

To use PostgreSQL locally, create a user and a database (pick any names and password):

```bash
sudo -u postgres psql -c "CREATE USER <db_user> WITH PASSWORD '<db_password>';"
sudo -u postgres psql -c "CREATE DATABASE <db_name> OWNER <db_user>;"
```

Then set the same values in `.env`:

```
DB_NAME=<db_name>
DB_USER=<db_user>
DB_PASSWORD=<db_password>
DB_HOST=localhost
DB_PORT=5432
```

## Commands

```bash
python manage.py migrate     # apply migrations
python manage.py runserver   # start dev server at http://127.0.0.1:8000
```

Health check: `GET /api/health/` returns `{"status": "ok"}`.

## Landing content

`GET /api/content/landing/` returns the landing page content: hero, banner, "for whom" and "why worth" blocks.

Content is edited in the admin:

- **Content: sections** — the blocks themselves (texts, images, cards);
- **Content: pages → Landing Page** — which blocks are shown on the page.

Load the initial content after `migrate`:

```bash
python manage.py loaddata landing
```

The fixture lives in `content/pages/fixtures/landing.json`. Loading it again overwrites the landing records with the fixture data, so changes made in the admin will be lost.

## Authentication

`POST /api/auth/login/` — log in with email and password.

```json
{ "email": "user@example.com", "password": "P@ssw0rd", "remember": true }
```

Response `200`:

```json
{ "access": "<jwt>", "user": { "id": 1, "email": "user@example.com", "role": "startup" } }
```

The refresh token is set in the `refresh_token` cookie: `HttpOnly` (JavaScript can't read it), `SameSite=Lax`, `Path=/api/auth/`, `Secure` when `DEBUG` is off. Without `"remember": true` it's a session cookie, removed when the browser closes.

- Access token lives 15 minutes, refresh token 1 day (30 days with `"remember": true`).
- Send the access token as `Authorization: Bearer <access>`. Keep it in memory, not in `localStorage`.
- Errors: `400` invalid data, `401` wrong email or password, `429` too many requests or too many failed attempts: 5 for this email from one client (IP) → that client is locked for 15 minutes; 20 for this email from any clients → the email is locked for 1 hour.

`POST /api/auth/refresh/` — get a new access token, e.g. when the old one expires or after a page reload. No body: the token is taken from the cookie.

Response `200`:

```json
{ "access": "<jwt>" }
```

- The refresh token itself stays the same, so the session still ends 1 day (or 30 days) after login.
- Errors: `401` no cookie, or the token is invalid, expired, revoked, or the user is inactive or deleted. The client should then show the login page.

`POST /api/auth/logout/` — revoke the refresh token and delete the cookie. No body.

- Always returns `204`, even without a cookie or with an invalid one: the client can't delete an `HttpOnly` cookie, so it relies on this endpoint.
- The access token can't be revoked and keeps working until it expires (up to 15 minutes), so the client should drop it on logout.
- Issued and revoked refresh tokens are stored in the database (admin: **Token Blacklist**). Expired ones can be removed with `python manage.py flushexpiredtokens`.

Frontend requests to `/api/auth/` must use `credentials: 'include'`, otherwise the browser doesn't send or save the cookie. CORS allows it for the origins in `CORS_ALLOWED_ORIGINS`. `SameSite=Lax` works while the frontend and the API are on the same site (as `localhost:5173` and `localhost:8000` are); on different domains the cookie would need `SameSite=None` and CSRF protection.

- Use `localhost` for both the frontend and the API, not `127.0.0.1`: for the browser they are different sites, so the cookie isn't sent and refresh returns `401`.
- Login, refresh and logout check the `Origin` header: requests from other sites get `403`, so a foreign page can't log the user in or out through a form. Allowed origins are the API's own (the browsable API) and `CORS_ALLOWED_ORIGINS`; requests without `Origin` (curl, Postman) are allowed.

## Investors

Public investor profiles. Only verified investors (`is_verified=True`) are returned: an unverified or unknown id gets `404`.

`GET /api/investors/` — paginated list for investor cards.

- Query params (all optional): `page`, `page_size` (default 8), `search` (by investor name), `type` (`private`, `fund` or `company`).
- Each item: `investor_id`, `investor_name`, `investor_type`, `investment_min`.

`GET /api/investors/{id}/` — full profile.

```json
{
  "investor_id": 31,
  "investor_name": "Green Capital",
  "investor_type": "fund",
  "investor_description": "We invest in craft food and eco packaging.",
  "contact": { "phone": "+380501234567" },
  "investment_min": "50000.00",
  "is_verified": true
}
```

- `investor_description` is plain text; empty optional fields come as `""` (`investor_description`, `contact.phone`) or `null` (`investment_min`).
- `investment_min` is a string to keep the decimal precision.

Load sample investors (users and profiles with ids 31–33, one of them unverified):

```bash
python manage.py loaddata investors
```
