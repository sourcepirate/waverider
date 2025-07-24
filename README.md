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
python validate_template.py    # Comprehensive validation
python quick_test.py          # Quick validation
python run_tests.py           # Full test suite
python -m pytest test_cookiecutter.py -v  # Pytest tests
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
