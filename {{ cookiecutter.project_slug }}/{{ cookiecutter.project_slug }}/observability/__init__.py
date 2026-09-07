"""
Observability initialization for {{ cookiecutter.project_name }}.

Supports: sentry, datadog, newrelic, opentelemetry.
Each provider is initialized lazily; missing dependencies are ignored.
Call ``init_observability()`` from settings or wsgi/asgi if needed.
"""

import logging
import os

logger = logging.getLogger(__name__)


def init_observability():
    """Initialize all configured observability providers.

    This is called from settings/production.py (and optionally local.py).
    It safely handles missing dependencies so the app can run even if
    a provider SDK is not installed.
    """
    # Sentry is typically initialized in settings already; we keep a hook here
    # for consistency if needed via OBSERVABILITY_ENABLED env.
    # Individual providers are also initialized via their own modules.
    providers = os.getenv("OBSERVABILITY_PROVIDERS", "")
    # If generic env not set, try to init all that are available
    # Each init function is idempotent and checks its own env vars.
    try:
        from .sentry import init_sentry  # noqa

        init_sentry()
    except Exception as exc:  # pragma: no cover
        logger.debug("Sentry init skipped: %s", exc)

    try:
        from .datadog import init_datadog  # noqa

        init_datadog()
    except Exception as exc:  # pragma: no cover
        logger.debug("Datadog init skipped: %s", exc)

    try:
        from .newrelic import init_newrelic  # noqa

        init_newrelic()
    except Exception as exc:  # pragma: no cover
        logger.debug("New Relic init skipped: %s", exc)

    try:
        from .otel import init_otel  # noqa

        init_otel()
    except Exception as exc:  # pragma: no cover
        logger.debug("OpenTelemetry init skipped: %s", exc)
