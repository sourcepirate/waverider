#!/usr/bin/env python3
"""
Test runner for the cookiecutter template.

This script runs various tests to validate the template structure
and can be used in CI/CD pipelines.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_basic_validation():
    """Run basic template validation."""
    print("Running basic template validation...")
    
    # Run the validation script
    result = subprocess.run([
        sys.executable, 
        os.path.join(os.path.dirname(__file__), "validate_template.py")
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Basic validation passed")
        print(result.stdout)
        return True
    else:
        print("✗ Basic validation failed")
        print(result.stdout)
        print(result.stderr)
        return False


def run_cookiecutter_generation_test():
    """Test actual cookiecutter generation if cookiecutter is available."""
    try:
        import cookiecutter
        from cookiecutter.main import cookiecutter as cc_main
        import tempfile
        import shutil
        
        print("Running cookiecutter generation test...")
        
        # Test context
        test_context = {
            "project_name": "Test Project",
            "project_slug": "test_project",
            "project_description": "Test project description",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "django_secret_key": "test-secret-key",
            "use_docker": "y",
            "postgresql_user": "testuser",
            "postgresql_password": "testpass",
            "postgresql_db": "testdb",
            "postgresql_port": "5432",
            "celery_broker_url": "redis://localhost:6379/0",
            "celery_result_backend": "redis://localhost:6379/1"
        }
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        template_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Generate project
            generated_project = cc_main(
                template_dir,
                no_input=True,
                extra_context=test_context,
                output_dir=temp_dir
            )
            
            # Verify generated project
            if os.path.exists(generated_project):
                print(f"✓ Project generated successfully at: {generated_project}")
                
                # Check key files exist
                key_files = [
                    "manage.py",
                    "requirements/base.txt",
                    "test_project/settings/base.py",
                    "test_project/accounts/api/__init__.py"
                ]
                
                all_exist = True
                for file_path in key_files:
                    full_path = os.path.join(generated_project, file_path)
                    if not os.path.exists(full_path):
                        print(f"✗ Missing file: {file_path}")
                        all_exist = False
                
                if all_exist:
                    print("✓ All key files exist in generated project")
                    return True
                else:
                    print("✗ Some key files missing in generated project")
                    return False
            else:
                print("✗ Generated project directory not found")
                return False
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except ImportError:
        print("⚠ Cookiecutter not installed, skipping generation test")
        return True
    except Exception as e:
        print(f"✗ Cookiecutter generation test failed: {e}")
        return False


def run_pytest_tests():
    """Run pytest tests if pytest is available."""
    try:
        import pytest
        
        print("Running pytest tests...")
        
        # Run pytest on the test file
        test_file = os.path.join(os.path.dirname(__file__), "test_cookiecutter.py")
        
        if os.path.exists(test_file):
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Pytest tests passed")
                return True
            else:
                print("✗ Pytest tests failed")
                print(result.stdout)
                print(result.stderr)
                return False
        else:
            print("⚠ Pytest test file not found")
            return True
            
    except ImportError:
        print("⚠ Pytest not installed, skipping pytest tests")
        return True
    except Exception as e:
        print(f"✗ Pytest tests failed: {e}")
        return False


def main():
    """Run all available tests."""
    print("Cookiecutter Template Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Validation", run_basic_validation),
        ("Cookiecutter Generation", run_cookiecutter_generation_test),
        ("Pytest Tests", run_pytest_tests),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nOverall: {passed} passed, {failed} failed")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
