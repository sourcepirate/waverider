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


def parse_observability(raw, include_sentry_flag):
    """Parse observability value into a set of normalized provider names.

    Supports: none, sentry, datadog, newrelic, opentelemetry, all
    Handles string, comma-separated, list, and tojson forms.
    Also respects legacy include_sentry flag.
    """
    valid = {"sentry", "datadog", "newrelic", "opentelemetry"}
    result = set()

    # legacy include_sentry
    if include_sentry_flag == "y":
        result.add("sentry")

    if raw is None:
        return result

    if isinstance(raw, (list, tuple)):
        parts = [str(x).strip().lower() for x in raw if str(x).strip()]
        if not parts:
            return result
        if "all" in parts:
            return valid
        if len(parts) == 1 and parts[0] == "none":
            return result
        for p in parts:
            if p in valid:
                result.add(p)
            elif p == "none":
                continue
        return result

    raw_str = str(raw).strip()
    if not raw_str or raw_str.lower() == "none":
        return result
    if raw_str.lower() == "all":
        return valid

    if raw_str.startswith("[") and raw_str.endswith("]"):
        try:
            import ast

            parsed = ast.literal_eval(raw_str)
            if isinstance(parsed, (list, tuple)):
                for x in parsed:
                    v = str(x).strip().lower()
                    if v in valid:
                        result.add(v)
                    elif v == "all":
                        return valid
                return result
        except Exception:
            pass
        raw_str = raw_str.strip("[]")

    parts = [p.strip().lower().strip("'\"") for p in raw_str.split(",")]
    expanded = []
    for p in parts:
        expanded.extend([x.strip() for x in p.split() if x.strip()])
    for p in expanded:
        if p in valid:
            result.add(p)
        elif p == "all":
            return valid
    return result


def parse_coding_agents(raw):
    """Parse coding_agents value into a set of normalized agent names.

    Supports:
    - string "all" -> all agents
    - string "none" / "" -> empty set
    - comma-separated string "claude,gemini,opencode,pi,copilot"
    - list representation "['claude', 'opencode']" (when passed via extra_context)
    - actual list (if templating preserves type, handled via tojson)
    """
    if raw is None:
        return set()
    # Direct list/tuple handling (when using tojson)
    if isinstance(raw, (list, tuple)):
        valid = {"claude", "gemini", "opencode", "pi", "copilot", "codex", "cursor", "aider"}
        parts = [str(x).strip().lower() for x in raw if str(x).strip()]
        if not parts or (len(parts) == 1 and parts[0] == "none"):
            return set()
        if "all" in parts:
            return {"claude", "gemini", "opencode", "pi", "copilot"}
        return {p for p in parts if p in valid}
    raw_str = str(raw).strip()
    if not raw_str or raw_str.lower() == "none":
        return set()
    if raw_str.lower() == "all":
        return {"claude", "gemini", "opencode", "pi", "copilot"}
    # Handle list-like string representation: "['claude', 'gemini']" or '["claude","gemini"]'
    if raw_str.startswith("[") and raw_str.endswith("]"):
        try:
            import ast
            parsed = ast.literal_eval(raw_str)
            if isinstance(parsed, (list, tuple)):
                return {str(x).strip().lower() for x in parsed if str(x).strip().lower() != "none"}
        except Exception:
            pass
        # fallback: strip brackets and split
        raw_str = raw_str.strip("[]")
    # Normal comma-separated
    parts = [p.strip().lower().strip("'\"") for p in raw_str.split(",")]
    # Also handle space-separated
    expanded = []
    for p in parts:
        expanded.extend([x.strip() for x in p.split() if x.strip()])
    # Filter valid agents
    valid = {"claude", "gemini", "opencode", "pi", "copilot", "codex", "cursor", "aider"}
    result = {p for p in expanded if p in valid}
    # If user typed "all" among comma list, expand to all
    if "all" in expanded:
        return {"claude", "gemini", "opencode", "pi", "copilot"}
    return result


def main():
    print("\nPost-generation script starting...")
    print(f"Working directory: {PROJECT_DIRECTORY}")

    steps_succeeded = True
    project_slug = "{{ cookiecutter.project_slug }}"
    ci_provider = "{{ cookiecutter.ci_provider }}"
    use_celery = "{{ cookiecutter.use_celery }}"
    include_oauth2 = "{{ cookiecutter.include_oauth2 }}"
    include_sentry = "{{ cookiecutter.include_sentry }}"
    observability_raw = {{ cookiecutter.observability | tojson }}
    coding_agents_raw = {{ cookiecutter.coding_agents | tojson }}

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

    # 4b. Configure observability
    print("\nConfiguring observability...")
    observability = parse_observability(observability_raw, include_sentry)
    print(f"Selected observability: {sorted(observability) if observability else 'none'} (raw: {observability_raw!r}, include_sentry: {include_sentry})")

    # Remove unselected observability files
    observability_files = {
        "sentry": [f"{project_slug}/observability/sentry.py"],
        "datadog": [f"{project_slug}/observability/datadog.py"],
        "newrelic": [f"{project_slug}/observability/newrelic.py", "newrelic.ini"],
        "opentelemetry": [
            f"{project_slug}/observability/otel.py",
            "otel-collector-config.yaml",
        ],
    }
    # If no provider selected, remove entire observability package if empty
    if not observability:
        print("No observability selected -> removing observability package")
        remove_file(f"{project_slug}/observability")
        remove_file("newrelic.ini")
        remove_file("otel-collector-config.yaml")
    else:
        for provider, files in observability_files.items():
            if provider not in observability:
                for f in files:
                    remove_file(f)
        # If observability dir exists but only __init__.py remains, keep it
        # Clean up empty observability dir check
        obs_dir = os.path.join(PROJECT_DIRECTORY, f"{project_slug}/observability")
        if os.path.isdir(obs_dir):
            remaining = [x for x in os.listdir(obs_dir) if not x.startswith("__pycache__")]
            if not remaining or remaining == ["__init__.py"]:
                # Keep __init__.py even if single provider, it is lightweight
                pass
        print(f"Kept observability providers: {sorted(observability)}")

    # 4c. Configure coding agents
    print("\nConfiguring coding agents...")
    coding_agents = parse_coding_agents(coding_agents_raw)
    print(f"Selected coding agents: {sorted(coding_agents) if coding_agents else 'none'} (raw: {coding_agents_raw!r})")

    # Mapping of agent -> files/dirs to keep
    agent_files = {
        "claude": ["CLAUDE.md", ".claude"],
        "gemini": ["GEMINI.md", ".gemini"],
        "opencode": ["opencode.json"],
        "pi": [".pi"],
        "copilot": [".github/copilot-instructions.md"],
    }
    # AGENTS.md is canonical for all agents (opencode, pi, copilot, codex, etc.)
    # Keep it if any agent selected, else remove
    if not coding_agents:
        print("No coding agents selected -> removing all agent files")
        remove_file("AGENTS.md")
        for files in agent_files.values():
            for f in files:
                remove_file(f)
    else:
        # Remove files for unselected agents
        for agent, files in agent_files.items():
            if agent not in coding_agents:
                for f in files:
                    remove_file(f)
        # AGENTS.md is shared - keep if any agent selected, already handled
        print(f"Kept coding agent files for: {sorted(coding_agents)}")
        # Ensure .github directory remains if copilot instructions removed but workflows exist
        # (remove_file handles missing gracefully)

    # 5. Initialize Git repository
    if not run_command("git init", "Initialize Git repository"):
        steps_succeeded = False

    # 6. Install dependencies with uv
    print("\nInstalling dependencies with uv...")
    if not run_command("uv sync", "Install dependencies with uv"):
        print("--- uv sync failed. Run 'uv sync' manually later. ---", file=sys.stderr)

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
