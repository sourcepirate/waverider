from .base import *
import os
from decouple import config, Csv

# SECURITY WARNING: keep the secret key used in production secret!
# Must be set via environment variable in production
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv(), default=[])


# Middleware Configuration - Add WhiteNoise
_MIDDLEWARE = list(MIDDLEWARE)
try:
    security_middleware_index = _MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    _MIDDLEWARE.insert(security_middleware_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ValueError:
    _MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')
MIDDLEWARE = tuple(_MIDDLEWARE)


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='{{ cookiecutter.postgresql_db }}'),
        'USER': config('POSTGRES_USER', default='{{ cookiecutter.postgresql_user }}'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='{{ cookiecutter.postgresql_password }}'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': config('POSTGRES_PORT', default='{{ cookiecutter.postgresql_port }}'),
    }
}


{% if cookiecutter.use_celery == 'y' %}
# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='{{ cookiecutter.celery_broker_url }}')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='{{ cookiecutter.celery_result_backend }}')
{% endif %}


# Static files storage using whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Cache
CACHE_URL = config('CACHE_URL', default='redis://redis:6379/2')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# Observability
# Sentry
{% if cookiecutter.include_sentry == 'y' or 'sentry' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    _sentry_dsn = config('SENTRY_DSN', default='')
    if _sentry_dsn:
        sentry_sdk.init(
            dsn=_sentry_dsn,
            integrations=[
                DjangoIntegration(),
                CeleryIntegration(monitor_beat_tasks=True),
                RedisIntegration(),
            ],
            traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=1.0, cast=float),
            profiles_sample_rate=config('SENTRY_PROFILES_SAMPLE_RATE', default=0.0, cast=float),
            environment=config('SENTRY_ENVIRONMENT', default='production'),
            release=config('SENTRY_RELEASE', default=''),
            send_default_pii=True,
        )
except ImportError:
    pass
{% endif %}

# Datadog APM - initialized via wsgi/asgi or here for non-WSGI contexts
{% if 'datadog' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    import ddtrace  # noqa: F401

    from ddtrace import config as dd_config
    from ddtrace import patch_all

    if config('DD_TRACE_ENABLED', default=False, cast=bool) or config('DD_API_KEY', default=''):
        dd_config.service = config('DD_SERVICE', default='{{ cookiecutter.project_slug }}')
        dd_config.env = config('DD_ENV', default='production')
        dd_config.version = config('DD_VERSION', default='')
        patch_all()
except ImportError:
    pass
{% endif %}

# New Relic - initialized via wsgi/asgi newrelic.agent.initialize(); keep helper here
{% if 'newrelic' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    import newrelic.agent  # noqa: F401

    _nr_license = config('NEW_RELIC_LICENSE_KEY', default='')
    _nr_app_name = config('NEW_RELIC_APP_NAME', default='{{ cookiecutter.project_slug }}')
    _nr_config = config('NEW_RELIC_CONFIG_FILE', default='newrelic.ini')
    if _nr_license:
        import os

        if os.path.exists(_nr_config):
            newrelic.agent.initialize(_nr_config, config('NEW_RELIC_ENVIRONMENT', default='production'))
except ImportError:
    pass
{% endif %}

# OpenTelemetry
{% if 'opentelemetry' in cookiecutter.observability or 'all' in cookiecutter.observability %}
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    _otel_endpoint = config('OTEL_EXPORTER_OTLP_ENDPOINT', default='')
    _otel_enabled = config('OTEL_ENABLED', default=False, cast=bool)
    if _otel_endpoint or _otel_enabled:
        _otel_service = config('OTEL_SERVICE_NAME', default='{{ cookiecutter.project_slug }}')
        _resource = Resource.create({'service.name': _otel_service})
        _provider = TracerProvider(resource=_resource)
        _exporter = OTLPSpanExporter(endpoint=_otel_endpoint or 'http://localhost:4318/v1/traces')
        _provider.add_span_processor(BatchSpanProcessor(_exporter))
        trace.set_tracer_provider(_provider)
        DjangoInstrumentor().instrument()
        try:
            PsycopgInstrumentor().instrument()
        except Exception:
            pass
        try:
            CeleryInstrumentor().instrument()
        except Exception:
            pass
        try:
            RedisInstrumentor().instrument()
        except Exception:
            pass
except ImportError:
    pass
{% endif %}


# Security Settings
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='{{ cookiecutter.author_name }} <noreply@{{ cookiecutter.project_slug }}.com>')
