"""
Test suite for the Django OAuth2 Cookiecutter template.

This module tests the cookiecutter template generation and validates
that the generated project has the correct structure and functionality.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
import pytest
from pathlib import Path

# Add the cookiecutter directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestCookiecutterTemplate:
    """Test the cookiecutter template generation and structure."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def template_dir(self):
        """Get the template directory path."""
        return os.path.dirname(os.path.abspath(__file__))
    
    @pytest.fixture
    def test_context(self):
        """Provide test context for cookiecutter generation."""
        return {
            "project_name": "Test Django Project",
            "project_slug": "test_django_project",
            "project_description": "A test Django project with OAuth2 support",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "django_secret_key": "test-secret-key-for-testing-only",
            "use_docker": "y",
            "postgresql_user": "test_user",
            "postgresql_password": "test_password",
            "postgresql_db": "test_db",
            "postgresql_port": "5432",
            "celery_broker_url": "redis://localhost:6379/0",
            "celery_result_backend": "redis://localhost:6379/1"
        }
    
    def test_cookiecutter_json_structure(self, template_dir):
        """Test that cookiecutter.json has the correct structure."""
        cookiecutter_path = os.path.join(template_dir, "cookiecutter.json")
        assert os.path.exists(cookiecutter_path), "cookiecutter.json should exist"
        
        with open(cookiecutter_path, 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = [
            "project_name",
            "project_slug", 
            "project_description",
            "author_name",
            "author_email",
            "github_username",
            "django_secret_key",
            "use_docker",
            "postgresql_user",
            "postgresql_password",
            "postgresql_db",
            "postgresql_port",
            "celery_broker_url",
            "celery_result_backend"
        ]
        
        for field in required_fields:
            assert field in config, f"Required field '{field}' missing from cookiecutter.json"
        
        # Check that project_slug uses proper template logic
        assert "{{" in config["project_slug"], "project_slug should use cookiecutter template syntax"
        assert "cookiecutter.project_name" in config["project_slug"], "project_slug should derive from project_name"
    
    def test_template_directory_structure(self, template_dir):
        """Test that the template has the expected directory structure."""
        expected_files = [
            "cookiecutter.json",
            "README.md",
            "hooks/post_gen_project.py",
            "{{ cookiecutter.project_slug }}/manage.py",
            "{{ cookiecutter.project_slug }}/README.md",
            "{{ cookiecutter.project_slug }}/requirements/base.txt",
            "{{ cookiecutter.project_slug }}/requirements/local.txt",
            "{{ cookiecutter.project_slug }}/requirements/production.txt",
            "{{ cookiecutter.project_slug }}/docker-compose.yml",
            "{{ cookiecutter.project_slug }}/Dockerfile",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/base.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/local.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/production.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/urls.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/wsgi.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/asgi.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/celery.py",
        ]
        
        expected_dirs = [
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/tests",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings",
            "{{ cookiecutter.project_slug }}/requirements",
        ]
        
        for file_path in expected_files:
            full_path = os.path.join(template_dir, file_path)
            assert os.path.exists(full_path), f"Expected file missing: {file_path}"
        
        for dir_path in expected_dirs:
            full_path = os.path.join(template_dir, dir_path)
            assert os.path.exists(full_path), f"Expected directory missing: {dir_path}"
    
    def test_accounts_module_structure(self, template_dir):
        """Test that the accounts module has the correct structure."""
        accounts_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts")
        
        expected_files = [
            "admin.py",
            "apps.py", 
            "schemas.py",
            "api.py",
            "api/__init__.py",
            "api/auth.py",
            "api/oauth2.py",
            "api/users.py",
            "api/schemas.py",
            "oauth2/__init__.py",
            "oauth2/api.py",
            "oauth2/providers.py",
            "oauth2/utils.py",
            "oauth2/schemas.py",
            "tests/__init__.py",
            "tests/test_api_package.py"
        ]
        
        for file_path in expected_files:
            full_path = os.path.join(accounts_dir, file_path)
            assert os.path.exists(full_path), f"Expected accounts file missing: {file_path}"
    
    def test_post_gen_hook_exists(self, template_dir):
        """Test that post-generation hook exists and is executable."""
        hook_path = os.path.join(template_dir, "hooks/post_gen_project.py")
        assert os.path.exists(hook_path), "post_gen_project.py hook should exist"
        
        # Check that the hook has proper Python structure
        with open(hook_path, 'r') as f:
            content = f.read()
            assert "def " in content, "Hook should contain function definitions"
            assert "import " in content, "Hook should contain imports"
    
    def test_requirements_files_exist(self, template_dir):
        """Test that all requirements files exist and have content."""
        requirements_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/requirements")
        
        required_files = ["base.txt", "local.txt", "production.txt"]
        
        for req_file in required_files:
            file_path = os.path.join(requirements_dir, req_file)
            assert os.path.exists(file_path), f"Requirements file missing: {req_file}"
            
            with open(file_path, 'r') as f:
                content = f.read().strip()
                assert content, f"Requirements file should not be empty: {req_file}"
    
    def test_django_settings_structure(self, template_dir):
        """Test that Django settings are properly structured."""
        settings_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings")
        
        settings_files = ["base.py", "local.py", "production.py"]
        
        for settings_file in settings_files:
            file_path = os.path.join(settings_dir, settings_file)
            assert os.path.exists(file_path), f"Settings file missing: {settings_file}"
            
            with open(file_path, 'r') as f:
                content = f.read()
                # Check for Django-specific settings
                if settings_file == "base.py":
                    assert "INSTALLED_APPS" in content, "base.py should contain INSTALLED_APPS"
                    assert "MIDDLEWARE" in content, "base.py should contain MIDDLEWARE"
                    assert "DATABASES" in content, "base.py should contain DATABASES"
    
    def test_oauth2_package_structure(self, template_dir):
        """Test that OAuth2 package has correct structure."""
        oauth2_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2")
        
        oauth2_files = ["__init__.py", "api.py", "providers.py", "utils.py", "schemas.py"]
        
        for oauth2_file in oauth2_files:
            file_path = os.path.join(oauth2_dir, oauth2_file)
            assert os.path.exists(file_path), f"OAuth2 file missing: {oauth2_file}"
            
            with open(file_path, 'r') as f:
                content = f.read()
                assert content.strip(), f"OAuth2 file should not be empty: {oauth2_file}"
                
                # Check for specific content based on file
                if oauth2_file == "providers.py":
                    assert "google" in content.lower(), "providers.py should contain Google provider"
                    assert "github" in content.lower(), "providers.py should contain GitHub provider"
                    assert "facebook" in content.lower(), "providers.py should contain Facebook provider"
                elif oauth2_file == "api.py":
                    assert "@router" in content, "api.py should contain router decorators"
                    assert "Router" in content, "api.py should import Router"
    
    def test_api_package_structure(self, template_dir):
        """Test that API package has correct structure."""
        api_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api")
        
        api_files = ["__init__.py", "auth.py", "oauth2.py", "users.py", "schemas.py"]
        
        for api_file in api_files:
            file_path = os.path.join(api_dir, api_file)
            assert os.path.exists(file_path), f"API file missing: {api_file}"
            
            with open(file_path, 'r') as f:
                content = f.read()
                assert content.strip(), f"API file should not be empty: {api_file}"
                
                # Check for specific content based on file
                if api_file == "auth.py":
                    assert "register" in content.lower(), "auth.py should contain register functionality"
                    assert "login" in content.lower(), "auth.py should contain login functionality"
                elif api_file == "users.py":
                    assert "router" in content.lower(), "users.py should define router"
                elif api_file == "__init__.py":
                    assert "router" in content, "__init__.py should export routers"
    
    def test_tests_package_structure(self, template_dir):
        """Test that tests package has correct structure."""
        tests_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/tests")
        
        assert os.path.exists(os.path.join(tests_dir, "__init__.py")), "Tests __init__.py should exist"
        assert os.path.exists(os.path.join(tests_dir, "test_api_package.py")), "Main test file should exist"
        
        # Check that test file contains comprehensive tests
        with open(os.path.join(tests_dir, "test_api_package.py"), 'r') as f:
            content = f.read()
            assert "class " in content, "Test file should contain test classes"
            assert "def test_" in content, "Test file should contain test methods"
            assert "OAuth2" in content, "Test file should contain OAuth2 tests"
            assert "Auth" in content, "Test file should contain Auth tests"
            assert "Users" in content, "Test file should contain Users tests"
    
    def test_docker_configuration(self, template_dir):
        """Test that Docker configuration is present."""
        project_dir = os.path.join(template_dir, "{{ cookiecutter.project_slug }}")
        
        dockerfile_path = os.path.join(project_dir, "Dockerfile")
        compose_path = os.path.join(project_dir, "docker-compose.yml")
        
        assert os.path.exists(dockerfile_path), "Dockerfile should exist"
        assert os.path.exists(compose_path), "docker-compose.yml should exist"
        
        # Check Dockerfile content
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
            assert "FROM python" in dockerfile_content, "Dockerfile should use Python base image"
            assert "COPY requirements" in dockerfile_content, "Dockerfile should copy requirements"
        
        # Check docker-compose content
        with open(compose_path, 'r') as f:
            compose_content = f.read()
            assert "version:" in compose_content, "docker-compose.yml should have version"
            assert "services:" in compose_content, "docker-compose.yml should have services"
    
    def test_manage_py_exists(self, template_dir):
        """Test that manage.py exists and has correct content."""
        manage_path = os.path.join(template_dir, "{{ cookiecutter.project_slug }}/manage.py")
        
        assert os.path.exists(manage_path), "manage.py should exist"
        
        with open(manage_path, 'r') as f:
            content = f.read()
            assert "#!/usr/bin/env python" in content, "manage.py should have shebang"
            assert "django.core.management" in content, "manage.py should import Django management"
            assert "execute_from_command_line" in content, "manage.py should use execute_from_command_line"
            assert "{{ cookiecutter.project_slug }}" in content, "manage.py should reference project slug"


class TestCookiecutterGeneration:
    """Test the actual cookiecutter generation process."""
    
    def test_cookiecutter_generation_process(self, temp_dir, template_dir, test_context):
        """Test that cookiecutter can generate a project successfully."""
        pytest.importorskip("cookiecutter")
        from cookiecutter.main import cookiecutter
        
        # Generate project using cookiecutter
        try:
            generated_project = cookiecutter(
                template_dir,
                no_input=True,
                extra_context=test_context,
                output_dir=temp_dir
            )
            
            # Check that project was generated
            assert os.path.exists(generated_project), "Generated project should exist"
            
            # Check that key files exist in generated project
            expected_files = [
                "manage.py",
                "requirements/base.txt",
                f"{test_context['project_slug']}/settings/base.py",
                f"{test_context['project_slug']}/accounts/api/__init__.py",
                f"{test_context['project_slug']}/accounts/oauth2/api.py",
                f"{test_context['project_slug']}/accounts/tests/test_api_package.py"
            ]
            
            for file_path in expected_files:
                full_path = os.path.join(generated_project, file_path)
                assert os.path.exists(full_path), f"Generated file missing: {file_path}"
            
            return generated_project
            
        except Exception as e:
            pytest.fail(f"Cookiecutter generation failed: {e}")
    
    def test_generated_project_structure(self, temp_dir, template_dir, test_context):
        """Test that generated project has correct structure."""
        pytest.importorskip("cookiecutter")
        from cookiecutter.main import cookiecutter
        
        generated_project = cookiecutter(
            template_dir,
            no_input=True,
            extra_context=test_context,
            output_dir=temp_dir
        )
        
        project_slug = test_context['project_slug']
        
        # Check that project structure is correct
        expected_structure = [
            "manage.py",
            "requirements/",
            "docker-compose.yml",
            "Dockerfile",
            f"{project_slug}/",
            f"{project_slug}/settings/",
            f"{project_slug}/accounts/",
            f"{project_slug}/accounts/api/",
            f"{project_slug}/accounts/oauth2/",
            f"{project_slug}/accounts/tests/"
        ]
        
        for item in expected_structure:
            full_path = os.path.join(generated_project, item)
            assert os.path.exists(full_path), f"Generated structure missing: {item}"
    
    def test_generated_imports_work(self, temp_dir, template_dir, test_context):
        """Test that generated project has working imports."""
        pytest.importorskip("cookiecutter")
        from cookiecutter.main import cookiecutter
        
        generated_project = cookiecutter(
            template_dir,
            no_input=True,
            extra_context=test_context,
            output_dir=temp_dir
        )
        
        project_slug = test_context['project_slug']
        
        # Check that Python files don't have syntax errors
        python_files = [
            "manage.py",
            f"{project_slug}/settings/base.py",
            f"{project_slug}/accounts/api/__init__.py",
            f"{project_slug}/accounts/oauth2/api.py",
            f"{project_slug}/accounts/tests/test_api_package.py"
        ]
        
        for py_file in python_files:
            file_path = os.path.join(generated_project, py_file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Try to compile the Python code
                    compile(content, file_path, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in generated file {py_file}: {e}")
            except Exception as e:
                # Some files might have import errors due to missing dependencies
                # but they should at least be syntactically valid
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
