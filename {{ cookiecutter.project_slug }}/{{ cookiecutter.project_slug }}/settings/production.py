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


# Sentry
{% if cookiecutter.include_sentry == 'y' %}
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN', default=''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=1.0, cast=float),
    send_default_pii=True,
)
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
