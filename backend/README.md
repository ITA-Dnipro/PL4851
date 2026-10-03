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
