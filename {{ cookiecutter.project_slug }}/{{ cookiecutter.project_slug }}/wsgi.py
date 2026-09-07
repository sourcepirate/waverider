"""
WSGI config for {{ cookiecutter.project_name }} project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

{% if 'datadog' in cookiecutter.observability or 'all' in cookiecutter.observability %}
# Datadog APM - patch early before Django imports
try:
    import ddtrace
    ddtrace.patch_all()
except ImportError:
    pass
{% endif %}
{% if 'newrelic' in cookiecutter.observability or 'all' in cookiecutter.observability %}
# New Relic - initialize agent early
try:
    import newrelic.agent
    import os as _os
    _nr_config = _os.getenv("NEW_RELIC_CONFIG_FILE", "newrelic.ini")
    _nr_env = _os.getenv("NEW_RELIC_ENVIRONMENT", "production")
    if _os.path.exists(_nr_config) and _os.getenv("NEW_RELIC_LICENSE_KEY"):
        newrelic.agent.initialize(_nr_config, _nr_env)
except ImportError:
    pass
except Exception:
    pass
{% endif %}

from django.core.wsgi import get_wsgi_application

# Default to local settings if DJANGO_SETTINGS_MODULE is not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ cookiecutter.project_slug }}.settings.local')

application = get_wsgi_application() 