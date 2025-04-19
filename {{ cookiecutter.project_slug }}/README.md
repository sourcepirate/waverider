# {{ cookiecutter.project_name }}

[![PyUp](https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/shield.svg)](https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/)
<!-- This badge assumes you host the generated project on GitHub under the username provided during setup. -->
<!-- You'll need to enable PyUp (or similar service like Snyk, Dependabot) on your repository for the badge to work. -->

{{ cookiecutter.project_description }}

# Generated using Django 5.x

Built with the [Cookiecutter Django Celery Ninja](https://github.com/your-github-username/cookiecutter-django-celery-ninja) template (update link!).

## Core Features

*   **Web Framework:** Django 5.x
*   **API:** Django Ninja (Fast, async-ready, type-hinted APIs)
*   **Async Tasks:** Celery & Celery Beat (for background jobs and scheduled tasks)
*   **Database:** PostgreSQL
*   **Caching:** Redis (via `django-redis`)
*   **Authentication:** JWT (via `djangorestframework-simplejwt`) with basic register/login API endpoints in the `accounts` app.
*   **Permissions:** Object-level permissions via `django-guardian`.
*   **Development:** Docker Compose setup for PostgreSQL, Redis, Web App, Celery Worker, and Celery Beat.
*   **Production Static Files:** WhiteNoise configured for efficient static file serving.
*   **Settings Management:** `python-decouple` for loading settings from environment variables / `.env` file.
*   **Testing:** `pytest` and `pytest-django` setup.
*   **CI Security:** GitHub Actions workflow includes `safety` checks for vulnerable dependencies.

## Development Setup

{% if cookiecutter.use_docker == 'y' -%}
### Using Docker (Recommended)

This project uses Docker Compose for a consistent local development environment.

**Prerequisites:**

*   Docker ([Install Docker](https://docs.docker.com/get-docker/))
*   Docker Compose ([Usually included with Docker Desktop](https://docs.docker.com/compose/install/))

**Steps:**

1.  **Create Environment File:**
    Copy the example environment file. It contains defaults matching the `docker-compose.yml`. You *must* have a `.env` file for Docker Compose to read variables.
    ```bash
    cp .env.example .env
    ```
    *Review the `.env` file and adjust secrets like `DJANGO_SECRET_KEY` if necessary for local dev, although the default generated one is usually fine.*

2.  **Build and Run Containers:**
    This command builds the images (if they don't exist) and starts all services (database, redis, web, celery worker, celery beat) in the background.
    ```bash
    docker-compose up --build -d
    ```

3.  **Apply Database Migrations:**
    This command initializes the database schema for Django's built-in apps, your project's apps (`accounts`), and third-party apps (`django-guardian`, `django-celery-beat`, etc.). Wait a few seconds for the database container (`db`) to be ready (check with `docker-compose ps`).
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4.  **Create Superuser (Optional):**
    To access the Django admin interface.
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

5.  **Access the Application:**
    *   **Web Application / API:** [http://localhost:8000](http://localhost:8000)
    *   **API Docs (Swagger UI):** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
    *   **Admin Interface:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

**Common Docker Compose Commands:**

*   **Stop containers:** `docker-compose down`
*   **Stop and remove volumes (database data will be lost!):** `docker-compose down -v`
*   **View logs:** `docker-compose logs -f [service_name]` (e.g., `web`, `celeryworker`, `celerybeat`, `db`, `redis`)
*   **Run a management command:** `docker-compose exec web python manage.py <command>` (e.g., `shell_plus`, `collectstatic`)
*   **Run tests:** `docker-compose exec web pytest`

{% else -%}
### Without Docker (Manual Setup)

**Prerequisites:**

*   Python 3.8+
*   PostgreSQL Server (running and accessible)
*   Redis Server (running and accessible)
*   Virtualenv (recommended)

**Steps:**

1.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements/local.txt
    ```

3.  **Set Environment Variables:**
    Create a `.env` file in the project root. Copy variables from `.env.example` and adjust connection details (HOST, PORT) for your manually running PostgreSQL and Redis instances.
    ```dotenv
    # .env (Example for Manual Setup)
    DJANGO_SETTINGS_MODULE={{ cookiecutter.project_slug }}.settings.local
    DJANGO_SECRET_KEY='{{ cookiecutter.django_secret_key }}' # Replace if needed
    POSTGRES_DB={{ cookiecutter.postgresql_db }}
    POSTGRES_USER={{ cookiecutter.postgresql_user }}
    POSTGRES_PASSWORD={{ cookiecutter.postgresql_password }}
    POSTGRES_HOST=localhost # Or your DB host
    POSTGRES_PORT={{ cookiecutter.postgresql_port }} # Or your DB port
    CELERY_BROKER_URL=redis://localhost:6379/0 # Or your Redis URL
    CELERY_RESULT_BACKEND=redis://localhost:6379/1 # Or your Redis URL
    CACHE_URL=redis://localhost:6379/2 # Or your Redis URL
    ```
    Load the environment variables. You might need `export $(cat .env | xargs)` or use a tool like `direnv`.

4.  **Setup Database:**
    Ensure your PostgreSQL server is running and the database `{{ cookiecutter.postgresql_db }}` exists with user `{{ cookiecutter.postgresql_user }}` having the correct permissions and password.

5.  **Apply Database Migrations:**
    This command initializes the database schema for Django's built-in apps, your project's apps (`accounts`), and third-party apps (`django-guardian`, `django-celery-beat`, etc.).
    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser (Optional):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Development Server:**
    ```bash
    python manage.py runserver
    ```

8.  **Run Celery Worker:**
    Open a new terminal, activate the virtual environment, load `.env` variables, and run:
    ```bash
    celery -A {{ cookiecutter.project_slug }}.celery worker --loglevel=info
    ```

9.  **Run Celery Beat:**
    Open another terminal, activate the virtual environment, load `.env` variables, and run:
    ```bash
    celery -A {{ cookiecutter.project_slug }}.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```

10. **Access the Application:**
    *   **Web Application / API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
    *   **API Docs (Swagger UI):** [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
    *   **Admin Interface:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

{% endif -%}

## Running Tests

Ensure your development environment is running (Docker or Manual).

```bash
{% if cookiecutter.use_docker == 'y' -%}
# Inside Docker
docker-compose exec web pytest
{% else -%}
# Manual Setup (ensure virtualenv is active and .env loaded)
pytest
{% endif -%}
```

## Deployment

Deploying this project involves several steps beyond the scope of this README. Key considerations:

*   **Settings:** Use `settings/production.py` (`DJANGO_SETTINGS_MODULE={{ cookiecutter.project_slug }}.settings.production`).
*   **Environment Variables:** Securely provide all required environment variables (secrets, database URLs, allowed hosts, etc.) to your production environment. Do NOT commit `.env` files with production secrets.
*   **`ALLOWED_HOSTS`:** Configure this setting in your production environment.
*   **`DEBUG`:** Ensure `DEBUG=False` in production.
*   **Web Server:** Use a production-grade WSGI server like Gunicorn (already included) or uvicorn (for ASGI), typically run behind a reverse proxy like Nginx.
*   **Static Files:** Run `python manage.py collectstatic` during your deployment process. WhiteNoise is configured to serve these files. Configure Nginx or a CDN for optimal performance if needed.
*   **Media Files:** Configure `MEDIA_ROOT` and `MEDIA_URL`. Production usually requires a persistent shared storage solution (like AWS S3, Google Cloud Storage) rather than the local filesystem.
*   **Celery:** Run Celery workers and Celery Beat as persistent background services (e.g., using `systemd` or `supervisor`).
*   **Database/Redis:** Use managed database and Redis services or properly secured and backed-up instances.
*   **Security:** Review Django's deployment checklist: [https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/) 