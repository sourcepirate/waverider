"""Datadog APM observability provider.

Datadog recommends early patching via ``ddtrace.patch_all()`` or
``ddtrace.auto``. This module provides an explicit init for Django/Celery.
"""

import logging
import os

logger = logging.getLogger(__name__)


def init_datadog():
    # Datadog is configured via env vars: DD_API_KEY, DD_APP_KEY, DD_SERVICE, etc.
    # Only initialize if DD_API_KEY or explicit enable flag is set.
    enabled = os.getenv("DD_TRACE_ENABLED", "")
    api_key = os.getenv("DD_API_KEY", "")
    if not api_key and enabled.lower() not in ("true", "1", "yes"):
        # Allow init if DD_TRACE_ENABLED is true even without API key (local dev)
        # but skip silently if no config at all to avoid noise.
        if not enabled:
            return

    try:
        import ddtrace  # noqa: F401
        from ddtrace import patch_all, config  # noqa

        # Configure service name if provided
        service = os.getenv("DD_SERVICE", "{{ cookiecutter.project_slug }}")
        env = os.getenv("DD_ENV", os.getenv("DJANGO_ENV", "production"))
        version = os.getenv("DD_VERSION", "")

        # ddtrace config is via env vars, but we can also set programmatically
        # https://docs.datadoghq.com/tracing/trace_collection/automatic_instrumentation/dd_libraries/python/
        config.service = service
        if env:
            config.env = env
        if version:
            config.version = version

        # Patch all supported libraries (Django, Celery, Redis, Psycopg, etc.)
        patch_all()

        logger.info("Datadog ddtrace initialized (service=%s env=%s)", service, env)
    except ImportError:
        logger.warning("ddtrace not installed, skipping Datadog init")
        return
