# Use uv for fast dependency management
FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.12-slim-bullseye AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary from the uv image
COPY --from=uv /uv /usr/local/bin/uv

# Create a non-root user
RUN addgroup --system app \
    && adduser --system --ingroup app app


# --- Development Stage ---
FROM base AS development
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --group dev
COPY . /app/
RUN chown -R app:app /app
USER app


# --- Production Stage ---
FROM base AS production
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev --no-install-project
COPY . /app/
RUN uv sync --frozen --no-dev
RUN chown -R app:app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "{{ cookiecutter.project_slug }}.wsgi:application"]
