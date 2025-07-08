#!/usr/bin/env python3
"""
Quick Template Validation

A simple validation script that tests the cookiecutter template
without requiring external dependencies.
"""

import os
import sys
import json
from pathlib import Path


def main():
    """Run quick validation tests."""
    print("Django OAuth2 Cookiecutter Template - Quick Validation")
    print("=" * 60)
    
    template_dir = os.path.dirname(os.path.abspath(__file__))
    errors = []
    
    # Test 1: Check cookiecutter.json exists and is valid
    print("1. Checking cookiecutter.json...")
    cookiecutter_path = os.path.join(template_dir, "cookiecutter.json")
    
    if not os.path.exists(cookiecutter_path):
        errors.append("cookiecutter.json is missing")
    else:
        try:
            with open(cookiecutter_path, 'r') as f:
                config = json.load(f)
                print(f"   ✓ Valid JSON with {len(config)} variables")
        except json.JSONDecodeError as e:
            errors.append(f"cookiecutter.json is invalid: {e}")
    
    # Test 2: Check essential project structure
    print("2. Checking essential project structure...")
    essential_paths = [
        "{{ cookiecutter.project_slug }}/manage.py",
        "{{ cookiecutter.project_slug }}/requirements/base.txt",
        "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/settings/base.py",
        "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/__init__.py",
        "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api.py",
        "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/api/__init__.py",
        "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/oauth2/__init__.py",
        "{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}/accounts/tests/test_api_package.py"
    ]
    
    missing_paths = []
    for path in essential_paths:
        full_path = os.path.join(template_dir, path)
        if not os.path.exists(full_path):
            missing_paths.append(path)
    
    if missing_paths:
        errors.append(f"Missing essential files: {missing_paths}")
    else:
        print(f"   ✓ All {len(essential_paths)} essential files exist")
    
    # Test 3: Check requirements files have content
    print("3. Checking requirements files...")
    req_files = [
        "{{ cookiecutter.project_slug }}/requirements/base.txt",
        "{{ cookiecutter.project_slug }}/requirements/local.txt", 
        "{{ cookiecutter.project_slug }}/requirements/production.txt"
    ]
    
    for req_file in req_files:
        req_path = os.path.join(template_dir, req_file)
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    errors.append(f"Requirements file is empty: {req_file}")
        else:
            errors.append(f"Requirements file missing: {req_file}")
    
    if not any("Requirements file" in error for error in errors):
        print(f"   ✓ All requirements files have content")
    
    # Test 4: Check Docker files
    print("4. Checking Docker configuration...")
    docker_files = [
        "{{ cookiecutter.project_slug }}/Dockerfile",
        "{{ cookiecutter.project_slug }}/docker-compose.yml"
    ]
    
    for docker_file in docker_files:
        docker_path = os.path.join(template_dir, docker_file)
        if not os.path.exists(docker_path):
            errors.append(f"Docker file missing: {docker_file}")
    
    if not any("Docker file" in error for error in errors):
        print(f"   ✓ Docker configuration files exist")
    
    # Test 5: Count Python files and check for obvious issues
    print("5. Checking Python files...")
    python_files = []
    template_files = 0
    
    for root, dirs, files in os.walk(os.path.join(template_dir, "{{ cookiecutter.project_slug }}")):
        for file in files:
            if file.endswith('.py'):
                python_files.append(file)
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if '{{ cookiecutter.' in content:
                        template_files += 1
    
    print(f"   ✓ Found {len(python_files)} Python files ({template_files} with template variables)")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ Validation FAILED with {len(errors)} errors:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        return False
    else:
        print("✅ Validation PASSED - Template structure looks good!")
        print("\nNext steps:")
        print("   - Run 'python validate_template.py' for comprehensive validation")
        print("   - Run 'python run_tests.py' for full test suite")
        print("   - Install cookiecutter and test generation: 'cookiecutter .'")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
