@AGENTS.md

# Claude Code Instructions

This file bridges Claude Code to the canonical `AGENTS.md`.

- **Read `AGENTS.md` first** – it contains the full project context, stack, structure, commands, and conventions.
- Claude Code loads `CLAUDE.md` automatically; the `@AGENTS.md` import above pulls in the shared instructions.
- Keep Claude-specific overrides (if any) below this line. Prefer editing `AGENTS.md` for shared rules.

## Claude-Specific Notes

- Use `uv run` prefix for all Python commands (`uv run pytest`, `uv run ruff check .`).
- When adding new API endpoints, follow Ninja pattern in `{{ cookiecutter.project_slug }}/accounts/api/` and register via `accounts/api/__init__.py`.
- For Celery tasks, create `<app>/tasks.py` with `@app.task` and rely on `autodiscover_tasks`.
- Verify changes with `uv run ruff check . && uv run ruff format --check . && uv run pytest`.

---
Project: {{ cookiecutter.project_name }} ({{ cookiecutter.project_slug }})
