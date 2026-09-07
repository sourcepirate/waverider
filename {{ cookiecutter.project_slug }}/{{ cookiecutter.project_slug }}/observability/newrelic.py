"""New Relic observability provider."""

import logging
import os

logger = logging.getLogger(__name__)


def init_newrelic():
    license_key = os.getenv("NEW_RELIC_LICENSE_KEY", "")
    app_name = os.getenv("NEW_RELIC_APP_NAME", "{{ cookiecutter.project_slug }}")

    if not license_key:
        return

    try:
        import newrelic.agent
    except ImportError:
        logger.warning("newrelic not installed, skipping New Relic init")
        return

    # Prefer newrelic.ini if present; otherwise initialize via env vars
    config_file = os.getenv("NEW_RELIC_CONFIG_FILE", "newrelic.ini")
    environment = os.getenv("NEW_RELIC_ENVIRONMENT", os.getenv("DJANGO_ENV", "production"))

    try:
        if os.path.exists(config_file):
            newrelic.agent.initialize(config_file, environment)
            logger.info("New Relic initialized via %s (env=%s)", config_file, environment)
        else:
            # Initialize without config file using env vars
            # newrelic.agent.initialize() requires a file, so we fallback to manual config
            # via environment variables; the agent will auto-config from env.
            # We still call initialize with None to trigger env-based config if supported.
            # If file missing, we just log and rely on newrelic admin wrapper.
            logger.info(
                "New Relic config file %s not found, relying on env vars (app=%s)",
                config_file,
                app_name,
            )
            # Attempt to initialize via environment; newer agents support this
            try:
                newrelic.agent.initialize(config_file)
            except Exception:
                pass
    except Exception as exc:  # pragma: no cover
        logger.warning("New Relic init failed: %s", exc)
