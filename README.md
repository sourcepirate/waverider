# Cookiecutter Django Celery Ninja

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

## Generated Project Setup

After generating the project, navigate to the project directory (`cd your_project_slug`) and follow the instructions in the generated project's `README.md`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
