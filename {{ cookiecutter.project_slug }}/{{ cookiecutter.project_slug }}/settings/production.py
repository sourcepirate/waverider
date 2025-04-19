# CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='{{ cookiecutter.celery_result_backend }}')

# Static files storage using whitenoise (recommended for simplicity)
# ... (whitenoise settings)

# Cache (use Redis, configure URL via environment variable)
CACHE_URL = config('CACHE_URL', default='redis://redis:6379/2') # Default assumes redis service name
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # Add production-specific options like connection pooling, timeouts if needed
        }
    }
}

# Email (Configure for your email provider, e.g., SendGrid, Mailgun)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY', default='{{ cookiecutter.django_secret_key }}') # Load from environment

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv(), default=[]) # e.g., ".yourdomain.com"


# Middleware Configuration - Add WhiteNoise
# Insert WhiteNoiseMiddleware right after SecurityMiddleware
# Ensure this modification happens *after* MIDDLEWARE is imported from base.py
# A common way is to copy, modify, and reassign MIDDLEWARE
_MIDDLEWARE = list(MIDDLEWARE) # Copy middleware list from base.py
try:
    # Find the index of SecurityMiddleware and insert WhiteNoise after it
    security_middleware_index = _MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    _MIDDLEWARE.insert(security_middleware_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ValueError:
    # If SecurityMiddleware is not found (unlikely), insert at the beginning
    _MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')
MIDDLEWARE = tuple(_MIDDLEWARE) # Assign the modified tuple back


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
# Use DATABASE_URL environment variable
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='{{ cookiecutter.postgresql_db }}'),
        'USER': config('POSTGRES_USER', default='{{ cookiecutter.postgresql_user }}'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='{{ cookiecutter.postgresql_password }}'),
        'HOST': config('POSTGRES_HOST', default='db'), # Or your DB host
        'PORT': config('POSTGRES_PORT', default='{{ cookiecutter.postgresql_port }}'),
    }
}
# DATABASES['default'] = config('DATABASE_URL', cast=db_url) # Recommended way using dj-database-url

# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='{{ cookiecutter.celery_broker_url }}')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='{{ cookiecutter.celery_result_backend }}')


# Static files storage using whitenoise (recommended for simplicity)
# https://whitenoise.readthedocs.io/en/stable/django.html#using-whitenoise-with-django
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATIC_ROOT is already defined in base.py and should point to where collectstatic gathers files


# Cache (use Redis, configure URL via environment variable)
CACHE_URL = config('CACHE_URL', default='redis://redis:6379/2') # Default assumes redis service name
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # Add production-specific options like connection pooling, timeouts if needed
        }
    }
}

# Email (Configure for your email provider, e.g., SendGrid, Mailgun)
# ... (existing email settings comments) ...


# Security Settings (uncomment and configure as needed)
# ... (existing security settings comments) ...


# Logging (configure as needed)
# ... (existing logging configuration) ...
