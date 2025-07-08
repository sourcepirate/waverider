"""
Basic Template Validation Tests

These tests validate the template structure without requiring cookiecutter
to be installed. They check file existence, content, and basic structure.
"""

import os
import sys
import json
import re
from pathlib import Path


class TestTemplateStructure:
    """Test the template structure without cookiecutter generation."""
    
    def __init__(self):
        self.template_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_template_dir = os.path.join(self.template_dir, "{{ cookiecutter.project_slug }}")
    
    def test_cookiecutter_json_validity(self):
        """Test that cookiecutter.json is valid JSON."""
        cookiecutter_path = os.path.join(self.template_dir, "cookiecutter.json")
        
        assert os.path.exists(cookiecutter_path), "cookiecutter.json should exist"
        
        try:
            with open(cookiecutter_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise AssertionError(f"cookiecutter.json is not valid JSON: {e}")
        
        # Check required fields
        required_fields = [
            "project_name", "project_slug", "project_description",
            "author_name", "author_email", "github_username",
            "django_secret_key", "use_docker", "postgresql_user",
            "postgresql_password", "postgresql_db", "postgresql_port",
            "celery_broker_url", "celery_result_backend"
        ]
        
        missing_fields = [field for field in required_fields if field not in config]
        assert not missing_fields, f"Missing required fields: {missing_fields}"
        
        print("✓ cookiecutter.json is valid and contains all required fields")
    
    def test_essential_files_exist(self):
        """Test that essential template files exist."""
        essential_files = [
            "README.md",
            "cookiecutter.json",
            "hooks/post_gen_project.py",
            "{{ cookiecutter.project_slug }}/manage.py",
            "{{ cookiecutter.project_slug }}/README.md",
            "{{ cookiecutter.project_slug }}/docker-compose.yml",
            "{{ cookiecutter.project_slug }}/Dockerfile",
            "{{ cookiecutter.project_slug }}/requirements/base.txt",
            "{{ cookiecutter.project_slug }}/requirements/local.txt",
            "{{ cookiecutter.project_slug }}/requirements/production.txt",
        ]
        
        missing_files = []
        for file_path in essential_files:
            full_path = os.path.join(self.template_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        assert not missing_files, f"Missing essential files: {missing_files}"
        print(f"✓ All {len(essential_files)} essential files exist")
    
    def test_django_structure_exists(self):
        """Test that Django project structure exists."""
        django_files = [
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/base.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/local.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/production.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/urls.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/wsgi.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/asgi.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/celery.py",
        ]
        
        missing_files = []
        for file_path in django_files:
            full_path = os.path.join(self.template_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        assert not missing_files, f"Missing Django files: {missing_files}"
        print(f"✓ All {len(django_files)} Django structure files exist")
    
    def test_accounts_app_structure(self):
        """Test that accounts app has correct structure."""
        accounts_files = [
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/admin.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/apps.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/schemas.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/auth.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/oauth2.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/users.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/schemas.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/api.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/providers.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/utils.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/schemas.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/tests/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/tests/test_api_package.py",
        ]
        
        missing_files = []
        for file_path in accounts_files:
            full_path = os.path.join(self.template_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        assert not missing_files, f"Missing accounts app files: {missing_files}"
        print(f"✓ All {len(accounts_files)} accounts app files exist")
    
    def test_python_files_syntax(self):
        """Test that Python files have valid syntax (skip template files)."""
        python_files = []
        
        # Find all Python files in the template
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Skip files with cookiecutter template variables
                    if '{{ cookiecutter.' in content:
                        continue
                    
                    # Try to compile the Python code
                    compile(content, py_file, 'exec')
            except SyntaxError as e:
                relative_path = os.path.relpath(py_file, self.template_dir)
                syntax_errors.append(f"{relative_path}: {e}")
            except UnicodeDecodeError as e:
                # Skip files with encoding issues
                continue
        
        # Only report syntax errors if we found any non-template files with errors
        if syntax_errors:
            assert False, f"Syntax errors found in non-template files: {syntax_errors}"
        
        print(f"✓ All {len(python_files)} Python files have valid syntax (template files skipped)")
        return True
    
    def test_requirements_files_content(self):
        """Test that requirements files have valid content."""
        requirements_files = [
            "{{ cookiecutter.project_slug }}/requirements/base.txt",
            "{{ cookiecutter.project_slug }}/requirements/local.txt",
            "{{ cookiecutter.project_slug }}/requirements/production.txt",
        ]
        
        for req_file in requirements_files:
            full_path = os.path.join(self.template_dir, req_file)
            assert os.path.exists(full_path), f"Requirements file missing: {req_file}"
            
            with open(full_path, 'r') as f:
                content = f.read().strip()
                assert content, f"Requirements file is empty: {req_file}"
                
                # Check for basic Django requirements
                if "base.txt" in req_file:
                    assert "Django" in content, f"Django missing from {req_file}"
                    assert "django-ninja" in content, f"django-ninja missing from {req_file}"
        
        print("✓ All requirements files have valid content")
    
    def test_docker_files_content(self):
        """Test that Docker files have valid content."""
        dockerfile_path = os.path.join(self.template_dir, "{{ cookiecutter.project_slug }}/Dockerfile")
        compose_path = os.path.join(self.template_dir, "{{ cookiecutter.project_slug }}/docker-compose.yml")
        
        # Test Dockerfile
        assert os.path.exists(dockerfile_path), "Dockerfile should exist"
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
            assert "FROM python" in dockerfile_content, "Dockerfile should use Python base image"
            assert ("COPY requirements" in dockerfile_content or 
                   "COPY ./requirements" in dockerfile_content), "Dockerfile should copy requirements"
            assert "RUN pip install" in dockerfile_content, "Dockerfile should install dependencies"
        
        # Test docker-compose.yml
        assert os.path.exists(compose_path), "docker-compose.yml should exist"
        with open(compose_path, 'r') as f:
            compose_content = f.read()
            assert "version:" in compose_content, "docker-compose.yml should have version"
            assert "services:" in compose_content, "docker-compose.yml should have services"
            assert "web:" in compose_content, "docker-compose.yml should have web service"
        
        print("✓ Docker files have valid content")
    
    def test_oauth2_implementation(self):
        """Test that OAuth2 implementation is complete."""
        oauth2_files = [
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/api.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/providers.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/utils.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/schemas.py",
        ]
        
        for oauth2_file in oauth2_files:
            full_path = os.path.join(self.template_dir, oauth2_file)
            assert os.path.exists(full_path), f"OAuth2 file missing: {oauth2_file}"
            
            with open(full_path, 'r') as f:
                content = f.read()
                assert content.strip(), f"OAuth2 file is empty: {oauth2_file}"
                
                # Check for specific OAuth2 content
                if "providers.py" in oauth2_file:
                    assert "google" in content.lower(), "Google provider missing"
                    assert "github" in content.lower(), "GitHub provider missing"
                    assert "facebook" in content.lower(), "Facebook provider missing"
                elif "api.py" in oauth2_file:
                    assert "router" in content, "Router missing from OAuth2 API"
                    assert "authorize" in content.lower(), "Authorize endpoint missing"
                    assert "callback" in content.lower(), "Callback endpoint missing"
        
        print("✓ OAuth2 implementation is complete")
    
    def test_api_structure_complete(self):
        """Test that API structure is complete."""
        api_files = [
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/__init__.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/auth.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/oauth2.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/users.py",
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/schemas.py",
        ]
        
        for api_file in api_files:
            full_path = os.path.join(self.template_dir, api_file)
            assert os.path.exists(full_path), f"API file missing: {api_file}"
            
            with open(full_path, 'r') as f:
                content = f.read()
                assert content.strip(), f"API file is empty: {api_file}"
                
                # Check for specific API content
                if "auth.py" in api_file:
                    assert "register" in content.lower(), "Register endpoint missing"
                    assert "login" in content.lower(), "Login endpoint missing"
                elif "users.py" in api_file:
                    assert "router" in content, "Router missing from users API"
                elif "__init__.py" in api_file:
                    assert "router" in content, "Router export missing from API package"
        
        print("✓ API structure is complete")
    
    def test_comprehensive_tests_exist(self):
        """Test that comprehensive tests exist."""
        test_file = os.path.join(
            self.template_dir, 
            "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/tests/test_api_package.py"
        )
        
        assert os.path.exists(test_file), "Main test file should exist"
        
        with open(test_file, 'r') as f:
            content = f.read()
            
            # Check for test classes
            required_test_classes = [
                "AuthAPITestCase",
                "UsersAPITestCase", 
                "OAuth2ProvidersTestCase",
                "OAuth2UtilsTestCase",
                "OAuth2APITestCase"
            ]
            
            missing_classes = [cls for cls in required_test_classes if cls not in content]
            assert not missing_classes, f"Missing test classes: {missing_classes}"
            
            # Check for test methods
            test_methods = re.findall(r'def (test_\w+)', content)
            assert len(test_methods) >= 20, f"Should have at least 20 test methods, found {len(test_methods)}"
        
        print(f"✓ Comprehensive tests exist with {len(test_methods)} test methods")
    
    def test_template_variables_usage(self):
        """Test that cookiecutter variables are used correctly."""
        template_files = []
        
        # Find all files that might contain template variables
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith(('.py', '.yml', '.yaml', '.txt', '.md', '.json')):
                    template_files.append(os.path.join(root, file))
        
        variable_issues = []
        
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for common template variable patterns
                    if '{{ cookiecutter.' in content:
                        # Check for proper variable usage
                        import re
                        
                        # Find all cookiecutter variables
                        variables = re.findall(r'\{\{\s*cookiecutter\.(\w+)\s*\}\}', content)
                        
                        # Check that used variables are defined in cookiecutter.json
                        with open(os.path.join(self.template_dir, 'cookiecutter.json'), 'r') as config_file:
                            config = json.load(config_file)
                            
                            for var in variables:
                                if var not in config:
                                    relative_path = os.path.relpath(template_file, self.template_dir)
                                    variable_issues.append(f"{relative_path}: Undefined variable 'cookiecutter.{var}'")
                        
                        # Check for malformed template syntax
                        malformed = re.findall(r'\{\{[^}]*\}\}', content)
                        for match in malformed:
                            if not re.match(r'\{\{\s*cookiecutter\.\w+.*\}\}', match):
                                if 'cookiecutter.' in match:  # Only flag cookiecutter-related syntax
                                    relative_path = os.path.relpath(template_file, self.template_dir)
                                    variable_issues.append(f"{relative_path}: Malformed template syntax '{match}'")
                        
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        
        assert not variable_issues, f"Template variable issues: {variable_issues}"
        print(f"✓ Template variables are correctly used in {len(template_files)} files")

    def run_all_tests(self):
        """Run all validation tests."""
        print("Running cookiecutter template validation tests...\n")
        
        test_methods = [
            self.test_cookiecutter_json_validity,
            self.test_essential_files_exist,
            self.test_django_structure_exists,
            self.test_accounts_app_structure,
            self.test_python_files_syntax,
            self.test_requirements_files_content,
            self.test_docker_files_content,
            self.test_oauth2_implementation,
            self.test_api_structure_complete,
            self.test_comprehensive_tests_exist,
            self.test_template_variables_usage
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                test_method()
                passed += 1
            except AssertionError as e:
                print(f"✗ {test_method.__name__}: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ {test_method.__name__}: Unexpected error: {e}")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"Test Results: {passed} passed, {failed} failed")
        print(f"{'='*50}")
        
        return failed == 0


if __name__ == "__main__":
    validator = TestTemplateStructure()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)
