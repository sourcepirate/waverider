.PHONY: install test lint format migrate shell

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

migrate:
	python manage.py migrate

shell:
	python manage.py shell_plus
