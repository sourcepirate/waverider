# Makefile for Django OAuth2 Cookiecutter Template

# Detect Python executable
PYTHON := $(shell command -v python 2> /dev/null || command -v python3 2> /dev/null || echo "python")

.PHONY: help test test-basic test-generation test-full install-deps clean tox-test tox-validate tox-all

help:
	@echo "Available commands:"
	@echo "  make test        - Run all tests"
	@echo "  make test-basic  - Run basic template validation"
	@echo "  make test-gen    - Test cookiecutter generation"
	@echo "  make test-full   - Run full test suite with pytest"
	@echo "  make install     - Install test dependencies"
	@echo "  make clean       - Clean up test artifacts"
	@echo "  make check-py    - Check Python executable"
	@echo "  make tox-test    - Run tests using tox"
	@echo "  make tox-validate- Run validation using tox"
	@echo "  make tox-all     - Run all tox environments"

check-py:
	@echo "Using Python: $(PYTHON)"
	@$(PYTHON) --version

install:
	@echo "Installing test dependencies..."
	$(PYTHON) -m pip install -r test-requirements.txt

test-basic:
	@echo "Running basic template validation..."
	$(PYTHON) validate_template.py

test-gen:
	@echo "Testing cookiecutter generation..."
	$(PYTHON) -c "import tempfile, shutil, os; from cookiecutter.main import cookiecutter; temp_dir = tempfile.mkdtemp(); cookiecutter('.', no_input=True, output_dir=temp_dir); print('✓ Generation successful'); shutil.rmtree(temp_dir)"

test-full:
	@echo "Running full test suite..."
	$(PYTHON) tests/run_tests.py

test: test-basic test-gen test-full
	@echo "All tests completed!"

clean:
	@echo "Cleaning up test artifacts..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf /tmp/test-output* 2>/dev/null || true

# Development shortcuts
dev-install:
	$(PYTHON) -m pip install -r test-requirements.txt
	$(PYTHON) -m pip install pre-commit
	pre-commit install

dev-test:
	$(PYTHON) validate_template.py
	@echo "Quick validation completed!"

# Generate a test project for manual testing
generate-test-project:
	@echo "Generating test project..."
	cookiecutter . --output-dir /tmp/test-projects
	@echo "Test project generated in /tmp/test-projects/"

# Tox targets
tox-test:
	@echo "Running tox tests..."
	tox -e py

tox-validate:
	@echo "Running tox validation..."
	tox -e validate,quick-test,template-test

tox-all:
	@echo "Running all tox environments..."
	tox -e all-tests

tox-lint:
	@echo "Running tox linting..."
	tox -e lint

tox-format:
	@echo "Running tox formatting..."
	tox -e format

tox-coverage:
	@echo "Running tox with coverage..."
	tox -e coverage
