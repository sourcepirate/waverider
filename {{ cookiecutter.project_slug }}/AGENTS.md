# {{ cookiecutter.project_name }} - Agent Instructions

This file is the single source of truth for AI coding agents. It is read by OpenCode, Claude Code (via `CLAUDE.md` bridge), Gemini CLI (via `GEMINI.md` bridge), Pi (`AGENTS.md` native), and other agents.

## Project Overview

- **Name**: {{ cookiecutter.project_name }} (`{{ cookiecutter.project_slug }}`)
- **Description**: {{ cookiecutter.project_description }}
- **Stack**: Django 5.x + Django Ninja + Celery + Redis + PostgreSQL
- **Python**: >=3.12, managed with `uv`
- **Auth**: JWT (SimpleJWT) + {% if cookiecutter.include_oauth2 == 'y' %}OAuth2 (django-oauth-toolkit, social-auth-app-django){% else %}JWT only (OAuth2 disabled){% endif %}
- **API docs**: `/api/docs` (Ninja Swagger)

## Project Structure

```
{{ cookiecutter.project_slug }}/
├── manage.py
├── pyproject.toml              # uv dependencies, ruff, pytest, coverage
├── docker-compose.yml          # web, db (postgres), redis, celeryworker, celerybeat
├── Dockerfile
├── .env.example / .env.oauth2.example
├── {{ cookiecutter.project_slug }}/
│   ├── settings/
│   │   ├── base.py             # shared config (DJANGO_APPS, THIRD_PARTY_APPS, LOCAL_APPS)
│   │   ├── local.py            # DEBUG, DB via DATABASE_URL, CACHE_URL
│   │   └── production.py       # production overrides
│   ├── urls.py                 # single NinjaAPI at /api/, mounts accounts_router
│   ├── celery.py               # Celery app, namespace CELERY, autodiscover_tasks
│   ├── wsgi.py / asgi.py
│   └── accounts/               # auth app
│       ├── api/
│       │   ├── __init__.py     # aggregates routers: auth, oauth2, users
│       │   ├── auth.py         # register / login
│       │   ├── users.py        # user profile
│       │   ├── oauth2.py       # OAuth2 bridge
│       │   └── schemas.py      # Pydantic schemas
│       ├── oauth2/
│       │   ├── api.py
│       │   ├── providers.py    # google, github, facebook, etc.
│       │   ├── utils.py
│       │   └── schemas.py
│       └── tests/test_api_package.py
└── requirements/ (legacy, prefer pyproject.toml)
```

## Essential Commands

```bash
# Install deps
uv sync

# Env
cp .env.example .env   # + .env.oauth2.example if OAuth2 enabled

# Run (docker)
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose logs -f web

# Run (local)
python manage.py migrate
python manage.py runserver
celery -A {{ cookiecutter.project_slug }} worker -l info          # worker
celery -A {{ cookiecutter.project_slug }} beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Tests & quality
uv run pytest
uv run pytest --cov
uv run ruff check .
uv run ruff format .
uv run pre-commit run --all-files
```

## Conventions & Patterns

### Settings
- `DJANGO_SETTINGS_MODULE={{ cookiecutter.project_slug }}.settings.local` by default (see `celery.py`)
- `base.py` groups: `DJANGO_APPS`, `THIRD_PARTY_APPS`, `LOCAL_APPS`; `local.py`/`production.py` override
- Secrets via `python-decouple` / `os.getenv` from `.env`; never commit `.env`

### Django Ninja APIs
```python
from ninja import Router
router = Router()

@router.post("/register", auth=None)
def register(request, payload: UserRegisterSchema): ...
```
- Single `NinjaAPI` in `urls.py`: `api.add_router("/accounts", accounts_router)`
- Sub-routers in `accounts/api/__init__.py` aggregate `auth`, `oauth2`, `users`
- All I/O via Pydantic schemas (`accounts/api/schemas.py`, `accounts/schemas.py`)
- JWT via `HttpBearer`: `auth=JWTAuth()` where needed; token endpoints at `/api/token/…`

### Celery
- `app.config_from_object('django.conf:settings', namespace='CELERY')` → all keys `CELERY_*`
- `app.autodiscover_tasks()` loads `tasks.py` from each app
- Beat uses `DatabaseScheduler` (`django_celery_beat`) – configure via admin or `beat_schedule` in `celery.py`

### Auth
- JWT: `djangorestframework-simplejwt`, settings `SIMPLE_JWT` in `base.py`
- OAuth2: `django-oauth-toolkit` + `social-auth-app-django`; providers in `accounts/oauth2/providers.py`

### Code Style
- Line length 100, ruff target `py312`, single quotes, isort compatible
- Use `uv` (`pyproject.toml`), not `pip install` directly; Dockerfile uses `uv sync`
- Prefer async-ready Ninja patterns, but keep Django ORM sync where needed

## Testing
- `pytest` with `pytest-django` (`DJANGO_SETTINGS_MODULE={{ cookiecutter.project_slug }}.settings.local`)
- Tests live in `{{ cookiecutter.project_slug }}/accounts/tests/test_api_package.py` (classes: `AuthAPITestCase`, `UsersAPITestCase`, `OAuth2*`)
- Add new app tests under `<app>/tests/` with `test_*.py`

## Agent Guidelines

1. **Read before edit**: Inspect `AGENTS.md`, `{{ cookiecutter.project_slug }}/settings/base.py`, `{{ cookiecutter.project_slug }}/urls.py`, `{{ cookiecutter.project_slug }}/accounts/api/__init__.py` to understand routing.
2. **Preserve template variables**: Never remove `{% raw %}{{ cookiecutter.* }}{% endraw %}` syntax from template files; they are rendered at project generation.
3. **Verify**: After changes run `uv run ruff check .`, `uv run pytest`, and `python -m py_compile` on edited files.
4. **No secrets**: Don't commit `.env`, use `.env.example` as template.
5. **Docker-first**: Ensure `docker-compose.yml` and `Dockerfile` stay `uv`-based.
6. **Keep bridges in sync**: `CLAUDE.md` and `GEMINI.md` are thin bridges to `AGENTS.md` – update `AGENTS.md` first.

## CI

- GitHub: `.github/workflows/django-ci.yml` (uv sync, pytest, ruff)
- GitLab: `.gitlab-ci.yml`

## Deployment Notes
- Production: `DJANGO_SETTINGS_MODULE={{ cookiecutter.project_slug }}.settings.production`, `DEBUG=False`, `ALLOWED_HOSTS` set, `collectstatic` via WhiteNoise, Gunicorn behind reverse proxy, Celery worker/beat as services.

---
Generated from cookiecutter-django-celery-ninja template. Update this file as project evolves; all agents (Claude, Gemini, OpenCode, Pi) read it.
