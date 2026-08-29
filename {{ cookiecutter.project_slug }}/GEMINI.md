@AGENTS.md

# Gemini CLI Instructions

This file bridges Gemini CLI to the canonical `AGENTS.md`.

- **Read `AGENTS.md` first** – full project context, commands, and conventions are defined there.
- Gemini CLI loads `GEMINI.md` automatically. If your Gemini CLI supports `contextFileName`, it is configured to read `AGENTS.md` as well (see `.gemini/settings.json` if present).
- Keep Gemini-specific overrides below. Prefer editing `AGENTS.md` for shared rules.

## Gemini-Specific Notes

- Follow the same Django Ninja / Celery / JWT patterns described in `AGENTS.md`.
- Use `uv` for dependency management; never use raw `pip install` in docs.
- Test with `uv run pytest`; lint with `uv run ruff check .`.

---
Project: {{ cookiecutter.project_name }} ({{ cookiecutter.project_slug }})
