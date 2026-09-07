from .base import *
import os
from decouple import config, Csv  # Using python-decouple for env vars

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Use python-decouple to load sensitive settings from .env file or environment variables
# Create a .env file in the root directory (where manage.py is) for local development
# Example .env:
# DATABASE_URL=postgres://{{ cookiecutter.postgresql_user }}:{{ cookiecutter.postgresql_password }}@db:{{ cookiecutter.postgresql_port }}/{{ cookiecutter.postgresql_db }}
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/1
# CACHE_URL=redis://redis:6379/2

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="{{ cookiecutter.postgresql_db }}"),
        "USER": config("POSTGRES_USER", default="{{ cookiecutter.postgresql_user }}"),
        "PASSWORD": config(
            "POSTGRES_PASSWORD", default="{{ cookiecutter.postgresql_password }}"
        ),
        "HOST": config(
            "POSTGRES_HOST", default="db"
        ),  # Service name in docker-compose.yml
        "PORT": config(
            "POSTGRES_PORT", default="{{ cookiecutter.postgresql_port }}"
        ),  # Internal port within docker network
    }
}
# Optional: Use DATABASE_URL from environment if defined and dj-database-url is installed
# from dj_database_url import parse as db_url
# DATABASES['default'] = config('DATABASE_URL', cast=db_url, default=f"postgres://{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}@{DATABASES['default']['HOST']}:{DATABASES['default']['PORT']}/{DATABASES['default']['NAME']}")


{% if cookiecutter.use_celery == 'y' %}
# Celery (can override base settings if needed, e.g., different broker for local)
# Reads from .env or defaults provided in cookiecutter.json / docker-compose.yml
CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL", default="{{ cookiecutter.celery_broker_url }}"
)
CELERY_RESULT_BACKEND = config(
    "CELERY_RESULT_BACKEND", default="{{ cookiecutter.celery_result_backend }}"
)
{% endif %}


# Email backend for development (prints emails to console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache (use Redis defined in docker-compose)
CACHE_URL = config("CACHE_URL", default="redis://redis:6379/2")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Add django-extensions if you want it for development
try:
    import django_extensions  # noqa

    INSTALLED_APPS += ["django_extensions"]
except ImportError:
    pass

# Add debug toolbar if you want it for development
try:
    import debug_toolbar  # noqa

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# Observability (optional in local - enable via env)
# Sentry
{% if cookiecutter.include_sentry == 'y' or 'sentry' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    _sentry_dsn = config('SENTRY_DSN', default='')
    if _sentry_dsn and config('SENTRY_ENABLED', default=False, cast=bool):
        sentry_sdk.init(
            dsn=_sentry_dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=1.0, cast=float),
            send_default_pii=True,
        )
except ImportError:
    pass
{% endif %}
{% if 'datadog' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    import ddtrace  # noqa: F401
    from ddtrace import config as dd_config
    from ddtrace import patch_all

    if config('DD_TRACE_ENABLED', default=False, cast=bool):
        dd_config.service = config('DD_SERVICE', default='{{ cookiecutter.project_slug }}')
        dd_config.env = config('DD_ENV', default='development')
        patch_all()
except ImportError:
    pass
{% endif %}
{% if 'opentelemetry' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    if config('OTEL_ENABLED', default=False, cast=bool) or config('OTEL_EXPORTER_OTLP_ENDPOINT', default=''):
        _otel_service = config('OTEL_SERVICE_NAME', default='{{ cookiecutter.project_slug }}')
        _resource = Resource.create({'service.name': _otel_service})
        _provider = TracerProvider(resource=_resource)
        _exporter = OTLPSpanExporter(
            endpoint=config('OTEL_EXPORTER_OTLP_ENDPOINT', default='http://localhost:4318/v1/traces')
        )
        _provider.add_span_processor(BatchSpanProcessor(_exporter))
        trace.set_tracer_provider(_provider)
        DjangoInstrumentor().instrument()
except ImportError:
    pass
{% endif %}
