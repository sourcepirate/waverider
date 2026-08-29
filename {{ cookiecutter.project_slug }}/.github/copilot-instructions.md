# Copilot Instructions

Follow `AGENTS.md` as the canonical project instructions.

- Stack: Django 5.x, Django Ninja, Celery, Redis, PostgreSQL, uv
- Use `uv run` for Python commands
- APIs via Ninja `Router`, schemas via Pydantic, JWT auth via `HttpBearer`
- Settings: `{{ cookiecutter.project_slug }}.settings.local` by default
- Test with `uv run pytest`, lint with `uv run ruff check .`

See `AGENTS.md` and `CLAUDE.md`/`GEMINI.md` for full details.
