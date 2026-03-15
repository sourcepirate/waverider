# Waverider: Django Celery Ninja Cookiecutter

**Project Purpose**: Cookiecutter template generator for Django projects with async task processing (Celery), REST APIs (Django Ninja), OAuth2/JWT auth, and Docker support.

## Architecture Overview

### Core Stack
- **Web Framework**: Django 5.2.x (LTS) - NOT compatible with Django 6.0
- **API Layer**: Django Ninja (type-hinted async-ready), NOT Django REST Framework
- **Task Queue**: Celery 5.x with Redis broker/backend
- **Auth**: JWT (SimpleJWT) + OAuth2 (django-oauth-toolkit) + Social auth
- **Database**: PostgreSQL (default), managed via `psycopg2-binary`
- **Cache**: Redis via `django-redis`
- **Periodic Tasks**: Celery Beat with database scheduler (`django-celery-beat`)

### Project Structure
```
{{ cookiecutter.project_slug }}/          # Generated Django project root
├── manage.py                             # Django CLI
├── requirements/
│   ├── base.txt      # Shared dependencies
│   ├── local.txt     # Development overrides
│   └── production.txt # Production-specific
├── {{ cookiecutter.project_slug }}/      # Django app package
│   ├── settings/     # Environment-specific configs (base/local/production)
│   ├── urls.py       # Main URL router - mounts NinjaAPI at /api/
│   ├── celery.py     # Celery app initialization with autodiscover
│   ├── asgi.py       # Async gateway (optional)
│   ├── wsgi.py       # WSGI for production (Gunicorn)
│   └── accounts/     # Built-in auth app (users, OAuth2, JWT)
├── docker-compose.yml # Dev environment (Django, Postgres, Redis, Celery)
└── Dockerfile        # Multi-stage build for production
```

## Key Patterns & Conventions

### 1. **Settings Structure (Environment-Aware)**
- `base.py`: Shared configs, installed apps, middleware
- `local.py` & `production.py`: Environment overrides (DEBUG, ALLOWED_HOSTS, DB, Celery)
- Set via: `DJANGO_SETTINGS_MODULE=<project>.settings.local` (default in celery.py)
- Settings groups: DJANGO_APPS, THIRD_PARTY_APPS, LOCAL_APPS for clarity

### 2. **API Routing with Django Ninja**
```python
# In urls.py: Single NinjaAPI instance mounts at /api/
api = NinjaAPI(title=..., version="1.0.0")
api.add_router("/accounts", accounts_router)  # /api/accounts/*

# In accounts/api/__init__.py: Sub-routers nested for modularity
router = Router()
router.add_router("/auth", auth_router)      # /api/accounts/auth/*
router.add_router("/oauth2", oauth2_router)  # /api/accounts/oauth2/*
router.add_router("/users", users_router)    # /api/accounts/users/*
```
- All responses use Pydantic schemas (strict type hints required)
- JWT auth via `HttpBearer` middleware: extract token, validate with `JWTAuthentication`

### 3. **Celery Task Configuration**
- `app.config_from_object('django.conf:settings', namespace='CELERY')` → all settings prefixed `CELERY_`
- `app.autodiscover_tasks()` loads tasks from all INSTALLED_APPS
- Periodic tasks: define in `celery.py` beat_schedule OR use `django-celery-beat` admin UI
- Worker command: `celery -A {{ cookiecutter.project_slug }} worker -l info`
- Beat scheduler: `celery -A {{ cookiecutter.project_slug }} beat -l info` (or use docker-compose)

### 4. **Authentication Layering**
- **JWT**: Use `JWTAuth(HttpBearer)` in endpoint decorators for stateless auth
- **OAuth2 Provider**: `django-oauth-toolkit` endpoints at `/oauth2/authorize`, `/oauth2/token`
- **Social Auth**: Via `social-auth-app-django` (Google, GitHub, etc.)
- **User Profiles**: Pydantic schemas (UserSchema, UserRegisterSchema) with validation via Field

### 5. **Template Rendering with Jinja2**
- File names & content: `{{ cookiecutter.variable_name }}` syntax
- Generated at project init via cookiecutter post_gen_project.py hook
- Config source: [cookiecutter.json](cookiecutter.json) (project_slug, author, DB credentials, Redis URLs, etc.)

## Testing & Validation

### Makefile Commands
```bash
make test           # Run all validations (basic + gen + full)
make test-basic     # Validate template structure (JSON, files, imports)
make test-gen       # Test cookiecutter generation into /tmp
make test-full      # Full pytest suite (integration tests)
make clean          # Remove .pyc, __pycache__, .pytest_cache
make install        # Install test-requirements.txt
```

### Tox Environments
```bash
tox -e validate        # Template structure validation
tox -e quick-test      # Quick sanity checks
tox -e template-test   # Full template generation & tests
tox -e py311           # Test on Python 3.11
tox -e lint            # flake8 + black + isort checks
```

### Test Structure
- [validate_template.py](validate_template.py): Checks cookiecutter.json validity, file existence, imports
- [tests/](tests/) directory: pytest suite testing generated projects
- Coverage tracked via tox coverage env

## Critical Files & Their Roles

| File | Purpose |
|------|---------|
| [cookiecutter.json](cookiecutter.json) | Template variables (project name, DB config, secrets) |
| [{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/base.py]({{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/base.py) | Django config: apps, middleware, database, Celery defaults |
| [{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/celery.py]({{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/celery.py) | Celery app init, settings binding, autodiscover tasks |
| [{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/urls.py]({{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/urls.py) | NinjaAPI mount point, JWT/OAuth2 token endpoints |
| [{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/__init__.py]({{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/__init__.py) | Auth routers aggregation |
| [hooks/post_gen_project.py](hooks/post_gen_project.py) | Post-generation hook: generates SECRET_KEY, installs deps, runs migrations |

## Common Workflows

### Adding a New API Endpoint
1. Create router in `accounts/api/<module>.py` using `@router.get/post/put` decorators
2. Use Pydantic schemas for request/response validation (imported in url config)
3. Inject JWT auth: `auth=jwt_auth` parameter in decorator
4. Add to `accounts/api/__init__.py`: `router.add_router("/<path>", <module>_router)`

### Extending Authentication
- **Add social provider**: Configure `SOCIAL_AUTH_*` in settings, add to social_auth_app_django URLs
- **Custom JWT claims**: Extend `JWTAuth` class, override `get_user()` logic
- **OAuth2 scopes**: Define in django-oauth-toolkit admin or via programmatic registration

### Adding Celery Tasks
1. Create `<app>/tasks.py`: `@app.task` decorated functions
2. Celery autodiscover loads automatically on worker startup
3. Schedule via beat_schedule in `celery.py` or django-celery-beat admin

### Deployment to Production
- Environment vars sourced via `python-decouple` (read from `.env`)
- Docker: multi-stage Dockerfile, entrypoint runs migrations + gunicorn
- Static files: WhiteNoise middleware configured in production.py
- Database migrations: `python manage.py migrate` in post_gen_project.py

## Known Constraints & Gotchas

1. **Django version**: Locked to 5.2.x - Django 6.0 incompatibility tracked in base.txt comment
2. **NinjaAPI single instance**: Must be created in urls.py (not app-level routers)
3. **Celery settings namespace**: All Celery config must use `CELERY_` prefix (e.g., `CELERY_BROKER_URL`)
4. **PostgreSQL required**: No SQLite for production; psycopg2-binary ensures no compilation
5. **Redis dual-purpose**: One DB (0) for Celery broker, another (1) for results backend - separate DB instances in production
6. **Email configuration**: Not yet included; add smtp settings + celery task for async sends

## Extension Points

- **New apps**: Add to LOCAL_APPS in base.py, create `api/` subpackage with routers
- **Custom middleware**: Append to MIDDLEWARE list in base.py
- **Cache backends**: Extend CACHES config in settings (redis already configured)
- **Database signals**: Define in app-level `signals.py`, auto-connect in `apps.py`
- **Management commands**: Create `<app>/management/commands/<cmd>.py` (autodiscovered)
