import os
import subprocess
import sys
import secrets
import string
import yaml

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)
SECRET_KEY_PLACEHOLDER = "!!! DONT FORGET TO REPLACE THIS !!!_!! DO NOT USE IN PRODUCTION !!"


def remove_file(filepath):
    full_path = os.path.join(PROJECT_DIRECTORY, filepath)
    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            print(f"Removed file: {filepath}")
        elif os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
            print(f"Removed directory: {filepath}")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error removing {filepath}: {e}", file=sys.stderr)


def run_command(command, description):
    print(f"Running: {description}...")
    try:
        process = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_DIRECTORY
        )
        print(f"Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR running '{description}' !!!", file=sys.stderr)
        print(f"Command: {e.cmd}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"!!! UNEXPECTED ERROR running '{description}' !!!", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        return False


def generate_secret_key(length=50):
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(chars) for _ in range(length))


def replace_in_file(filepath, old_string, new_string):
    full_path = os.path.join(PROJECT_DIRECTORY, filepath)
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        if old_string not in content:
            return True
        new_content = content.replace(old_string, new_string)
        with open(full_path, 'w') as f:
            f.write(new_content)
        print(f"Replaced placeholder in: {filepath}")
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"!!! ERROR replacing placeholder in {filepath}: {e} !!!", file=sys.stderr)
        return False


def remove_docker_compose_services(services_to_remove, compose_file):
    """Remove services from docker-compose.yml."""
    full_path = os.path.join(PROJECT_DIRECTORY, compose_file)
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        # Parse as YAML, remove services, write back
        data = yaml.safe_load(content)
        for service in services_to_remove:
            if service in data.get('services', {}):
                del data['services'][service]
                print(f"Removed '{service}' service from docker-compose.yml")
        with open(full_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"Error updating docker-compose.yml: {e}", file=sys.stderr)
        return False


def main():
    print("\nPost-generation script starting...")
    print(f"Working directory: {PROJECT_DIRECTORY}")

    steps_succeeded = True
    project_slug = "{{ cookiecutter.project_slug }}"
    ci_provider = "{{ cookiecutter.ci_provider }}"
    use_celery = "{{ cookiecutter.use_celery }}"
    include_oauth2 = "{{ cookiecutter.include_oauth2 }}"

    # 1. Generate SECRET_KEY
    new_secret_key = generate_secret_key()

    files_to_update = [
        f"{project_slug}/settings/base.py",
        f"{project_slug}/settings/local.py",
        f"{project_slug}/settings/production.py",
        ".env.example",
        "docker-compose.yml",
    ]
    print("\nReplacing SECRET_KEY placeholder...")
    for filepath in files_to_update:
        if not replace_in_file(filepath, SECRET_KEY_PLACEHOLDER, new_secret_key):
            steps_succeeded = False

    # 2. Remove CI files based on selection
    print("\nConfiguring CI/CD...")
    if ci_provider != "github":
        remove_file(".github/workflows/django-ci.yml")
    if ci_provider != "gitlab":
        remove_file(".gitlab-ci.yml")

    # 3. Remove Celery if not needed
    if use_celery == "n":
        print("\nRemoving Celery configuration...")
        remove_file(f"{project_slug}/celery.py")
        remove_docker_compose_services(["celeryworker", "celerybeat"], "docker-compose.yml")

    # 4. Remove OAuth2 if not needed
    if include_oauth2 == "n":
        print("\nRemoving OAuth2 configuration...")
        remove_file(".env.oauth2.example")
        remove_file(f"{project_slug}/accounts/oauth2")
        remove_file(f"{project_slug}/accounts/api/oauth2.py")

    # 5. Initialize Git repository
    if not run_command("git init", "Initialize Git repository"):
        steps_succeeded = False

    # 6. Install dependencies with uv
    if steps_succeeded:
        if not run_command("uv sync", "Install dependencies with uv"):
            steps_succeeded = False
            print("--- Please run 'uv sync' manually ---", file=sys.stderr)

    # 7. Install pre-commit hooks
    if steps_succeeded:
        try:
            result = run_command("uv run pre-commit install", "Install pre-commit Git hooks")
            if not result:
                print("--- pre-commit install skipped (will be available after first 'uv sync') ---")
        except Exception:
            print("--- pre-commit install skipped (can be installed manually) ---")

    # 8. Initial commit
    if steps_succeeded:
        print("\nAttempting initial Git commit...")
        if run_command("git add .", "Stage all files"):
            commit_msg = "Initial commit from cookiecutter template"
            if run_command(f'git commit -m "{commit_msg}"', "Create initial commit"):
                print("Successfully created initial commit.")
            else:
                print("--- Failed to create initial commit. Please commit manually. ---")
        else:
            print("--- Failed to stage files. Please stage and commit manually. ---")

    print("\n----------------------")
    if steps_succeeded:
        print("SUCCESS: Post-generation script finished.")
        print("SECRET_KEY generated and replaced.")
        print("Git initialized and pre-commit hooks installed.")
        print("\nNext steps:")
        print("  1. Create .env from .env.example:")
        print("     cp .env.example .env")
        print("  2. Run database migrations:")
        if "{{ cookiecutter.use_docker }}" == "y":
            print("     docker compose up -d")
            print("     docker compose exec web python manage.py migrate")
        else:
            print("     python manage.py migrate")
    else:
        print("ERROR: Post-generation script encountered errors.")
        print("Please check the output above and complete setup manually.")
        sys.exit(1)


if __name__ == '__main__':
    main()
