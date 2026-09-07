"""Sentry observability provider."""

import logging
import os

logger = logging.getLogger(__name__)


def init_sentry():
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        # Also check legacy config from settings
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
    except ImportError:
        logger.warning("sentry-sdk not installed, skipping Sentry init")
        return

    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0"))
    environment = os.getenv("SENTRY_ENVIRONMENT", os.getenv("DJANGO_ENV", "production"))
    release = os.getenv("SENTRY_RELEASE", "")

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(monitor_beat_tasks=True),
            RedisIntegration(),
        ],
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        environment=environment,
        release=release or None,
        send_default_pii=True,
    )
    logger.info("Sentry initialized (environment=%s)", environment)
