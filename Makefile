# Makefile for Django OAuth2 Cookiecutter Template

.PHONY: help test test-basic test-generation test-full install-deps clean

help:
	@echo "Available commands:"
	@echo "  make test        - Run all tests"
	@echo "  make test-basic  - Run basic template validation"
	@echo "  make test-gen    - Test cookiecutter generation"
	@echo "  make test-full   - Run full test suite with pytest"
	@echo "  make install     - Install test dependencies"
	@echo "  make clean       - Clean up test artifacts"

install:
	@echo "Installing test dependencies..."
	pip install -r test-requirements.txt

test-basic:
	@echo "Running basic template validation..."
	python validate_template.py

test-gen:
	@echo "Testing cookiecutter generation..."
	python -c "import tempfile, shutil, os; from cookiecutter.main import cookiecutter; temp_dir = tempfile.mkdtemp(); cookiecutter('.', no_input=True, output_dir=temp_dir); print('✓ Generation successful'); shutil.rmtree(temp_dir)"

test-full:
	@echo "Running full test suite..."
	python run_tests.py

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
	pip install -r test-requirements.txt
	pip install pre-commit
	pre-commit install

dev-test:
	python validate_template.py
	@echo "Quick validation completed!"

# Generate a test project for manual testing
generate-test-project:
	@echo "Generating test project..."
	cookiecutter . --output-dir /tmp/test-projects
	@echo "Test project generated in /tmp/test-projects/"
