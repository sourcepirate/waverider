# Cookiecutter Django Celery Ninja

[![Build Status](https://github.com/sourcepirate/waverider/workflows/Test%20Cookiecutter%20Template/badge.svg)](https://github.com/sourcepirate/waverider/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/github/license/sourcepirate/waverider.svg)](https://github.com/sourcepirate/waverider/blob/main/LICENSE)
[![Cookiecutter](https://img.shields.io/badge/cookiecutter-template-green.svg)](https://github.com/cookiecutter/cookiecutter)

A Cookiecutter template for creating Django projects with Celery, Celery Beat, Django Ninja for APIs, and Docker support.

## Features

*   **Django {{ django_version | default('5.0') }}**: The core web framework.
*   **Django Ninja**: Fast, async-ready API framework with type hints.
*   **Celery & Celery Beat**: Asynchronous task processing and periodic tasks.
*   **PostgreSQL**: Default database.
*   **Redis**: Default Celery broker and result backend.
*   **Docker & Docker Compose**: For containerized development and deployment setup.
*   **Environment Variables**: Settings managed via `.env` file using `python-decouple`.
*   **Basic Settings Structure**: Separate settings for `local` and `production`.
*   **Gunicorn**: Production WSGI server.
*   **Whitenoise**: Simplified static file serving for production (optional).
*   **Observability**: Optional integrations for Sentry, Datadog, New Relic, and OpenTelemetry via `observability` (comma-separated, e.g. `sentry,datadog` or `all`).
*   **Coding Agents**: Optional configs for Claude Code, Gemini CLI, OpenCode, Pi, and Copilot via `coding_agents` (shared `AGENTS.md`).

## Prerequisites

*   Python 3.8+
*   Cookiecutter: `pip install cookiecutter`
*   Docker & Docker Compose (if using the Docker setup `use_docker=y`)

## Usage

Generate your project using Cookiecutter:

```bash
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja
```

Or from a local clone:

```bash
cookiecutter /path/to/cookiecutter-django-celery-ninja
```

You will be prompted for configuration values (like project name, author, database settings, etc.). See `cookiecutter.json` for details.

### Coding Agents

The template can generate configuration for multiple AI coding agents:

```bash
# All agents (default)
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input coding_agents=all

# Select specific agents (comma-separated)
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input coding_agents="claude,gemini,opencode"

# No agent configs
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input coding_agents=none
```

**Supported:** `claude` (→ `CLAUDE.md` + `.claude/`), `gemini` (→ `GEMINI.md` + `.gemini/settings.json`), `opencode` (→ `opencode.json` + `AGENTS.md`), `pi` (→ `AGENTS.md` + `.pi/settings.json`), `copilot` (→ `.github/copilot-instructions.md`). `AGENTS.md` is the canonical single source of truth; `CLAUDE.md`/`GEMINI.md` are thin `@AGENTS.md` bridges.

### Observability

The template supports multiple observability providers: Sentry, Datadog, New Relic, and OpenTelemetry.

```bash
# No observability (default)
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability=none

# Single provider
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability=sentry
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability=datadog
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability=newrelic
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability=opentelemetry

# Multiple providers (comma-separated)
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability="sentry,datadog"

# All providers
cookiecutter gh:your-github-username/cookiecutter-django-celery-ninja --no-input observability=all
```

**Provider details:**

| Provider | SDK | Env vars | Notes |
|----------|-----|----------|-------|
| Sentry | `sentry-sdk[django]` | `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE` | Init in `settings/production.py` + `settings/local.py` (when enabled). Legacy `include_sentry=y` still works. |
| Datadog | `ddtrace` | `DD_API_KEY`, `DD_SERVICE`, `DD_TRACE_ENABLED` | `ddtrace.patch_all()` in `wsgi.py`/`asgi.py`. |
| New Relic | `newrelic` | `NEW_RELIC_LICENSE_KEY`, `NEW_RELIC_APP_NAME` | `newrelic.ini` + `newrelic.agent.initialize()`. |
| OpenTelemetry | `opentelemetry-*` | `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME` | Instruments Django/Psycopg/Celery/Redis; `otel-collector` service in `docker-compose.yml`. |

Generated observability code lives in `{{project_slug}}/observability/` (post-gen hook removes unselected providers) and is guarded by `try/except ImportError`.

## Testing the Template

This template includes comprehensive testing using tox to ensure all functionality works correctly.

### Prerequisites for Testing

Install test dependencies:

```bash
pip install -r test-requirements.txt
```

### Running Tests

#### Using Tox (Recommended)

Run all tests across multiple Python versions:

```bash
# Run basic validation
tox -e validate

# Run quick tests  
tox -e quick-test

# Run template tests
tox -e template-test

# Run all validation tests
tox -e all-tests

# Run tests for specific Python version
tox -e py311

# Run all environments
tox
```

#### Using Makefile

```bash
# Traditional test methods
make test          # Run all tests
make test-basic    # Basic validation only
make test-gen      # Test cookiecutter generation
make test-full     # Full test suite

# Tox-based tests
make tox-test      # Run tox tests
make tox-validate  # Run tox validation
make tox-all       # Run all tox environments
```

#### Direct Script Execution

```bash
# Individual test scripts
python validate_template.py          # Comprehensive validation
python tests/quick_test.py           # Quick validation
python tests/run_tests.py            # Full test suite
python -m pytest tests/test_cookiecutter.py -v  # Pytest tests
```

### Available Tox Environments

* `validate`: Template structure validation
* `quick-test`: Quick validation checks
* `template-test`: Full template testing
* `py38`, `py39`, `py310`, `py311`, `py312`: Python version-specific tests
* `lint`: Code linting with flake8, black, isort
* `format`: Code formatting with black and isort
* `coverage`: Test coverage reporting
* `all-tests`: Comprehensive test suite

## Generated Project Setup

After generating the project, navigate to the project directory (`cd your_project_slug`) and follow the instructions in the generated project's `README.md`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
