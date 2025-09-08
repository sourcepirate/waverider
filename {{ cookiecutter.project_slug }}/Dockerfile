# Start from a Python base image
FROM python:3.12-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# Add build-essential and libpq-dev temporarily for building psycopg2 if not using binary
# Add gettext for internationalization support if needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # Required for psycopg2 non-binary builds (keep if switching from -binary)
    # build-essential libpq-dev \
    # Optional: For PostgreSQL client tools (psql)
    postgresql-client \
    # Optional: For internationalization
    # gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app \
    && adduser --system --ingroup app app

# --- Development Stage ---
# We might use this stage later for development-specific setup if needed
# FROM base as development
# RUN pip install --upgrade pip setuptools wheel
# COPY ./requirements/local.txt /app/requirements/local.txt
# RUN pip install --no-cache-dir -r /app/requirements/local.txt
# COPY . /app/


# --- Production Stage ---
FROM base as production

# Install pip requirements
RUN pip install --upgrade pip setuptools wheel
# Copy only requirements first to leverage Docker cache
COPY ./requirements /app/requirements
RUN pip install --no-cache-dir -r /app/requirements/production.txt

# Copy project code
COPY . /app/

# Change ownership to the non-root user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Run gunicorn
# The specific command might be overridden in docker-compose.yml
# Use --bind 0.0.0.0 to allow connections from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "{{ cookiecutter.project_slug }}.wsgi:application"] 