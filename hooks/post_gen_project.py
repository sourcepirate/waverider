import os
import subprocess
import sys
import secrets # Import the secrets module
import string # Import string for character sets

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)
# Placeholder used in cookiecutter.json and potentially copied into files
SECRET_KEY_PLACEHOLDER = "!!! DONT FORGET TO REPLACE THIS !!!_!! DO NOT USE IN PRODUCTION !!"

def remove_file(filepath):
    """Removes a file if it exists."""
    try:
        os.remove(os.path.join(PROJECT_DIRECTORY, filepath))
        print(f"Removed file: {filepath}")
    except FileNotFoundError:
        print(f"File not found, skipping removal: {filepath}")
    except Exception as e:
        print(f"Error removing file {filepath}: {e}", file=sys.stderr)

def run_command(command, description):
    """Runs a command and prints success/failure."""
    print(f"Running: {description}...")
    try:
        # Use shell=True cautiously, needed here for commands like 'pip' potentially
        # Consider specifying full paths if running without shell=True is desired
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
        # print(process.stdout) # Uncomment for more verbose output
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR running '{description}' !!!", file=sys.stderr)
        print(f"Command: {e.cmd}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        print(f"Stdout:\n{e.stdout}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"!!! UNEXPECTED ERROR running '{description}' !!!", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        return False

def generate_secret_key(length=50):
    """Generates a secure random string for the SECRET_KEY."""
    print("Generating secure Django SECRET_KEY...")
    # Use characters recommended by Django documentation + common symbols
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    key = ''.join(secrets.choice(chars) for _ in range(length))
    print("SECRET_KEY generated.")
    return key

def replace_in_file(filepath, old_string, new_string):
    """Replaces all occurrences of old_string with new_string in a file."""
    full_path = os.path.join(PROJECT_DIRECTORY, filepath)
    try:
        with open(full_path, 'r') as f:
            content = f.read()

        if old_string not in content:
            print(f"Placeholder '{old_string}' not found in {filepath}, skipping replacement.")
            return True # Not an error if placeholder isn't there

        new_content = content.replace(old_string, new_string)

        with open(full_path, 'w') as f:
            f.write(new_content)
        print(f"Replaced placeholder in: {filepath}")
        return True
    except FileNotFoundError:
        print(f"File not found, skipping replacement: {filepath}")
        return True # Not an error if file doesn't exist (e.g., conditional files)
    except Exception as e:
        print(f"!!! ERROR replacing placeholder in {filepath}: {e} !!!", file=sys.stderr)
        return False

def main():
    """Initialize Git, generate secret key, install pre-commit hooks."""
    print("\nPost-generation script starting...")
    print(f"Working directory: {PROJECT_DIRECTORY}")

    steps_succeeded = True
    project_slug = "{{ cookiecutter.project_slug }}" # Get slug for file paths

    # 1. Generate SECRET_KEY
    new_secret_key = generate_secret_key()

    # 2. Replace placeholder in settings files and others
    files_to_update = [
        f"{project_slug}/settings/base.py",
        f"{project_slug}/settings/local.py", # Check if placeholder is used here
        f"{project_slug}/settings/production.py",
        ".env.example", # Update the example file too
        "docker-compose.yml", # Used as default env var here
    ]
    print("\nReplacing SECRET_KEY placeholder...")
    for filepath in files_to_update:
        if not replace_in_file(filepath, SECRET_KEY_PLACEHOLDER, new_secret_key):
            steps_succeeded = False
            print(f"--- Failed to update SECRET_KEY in {filepath} ---", file=sys.stderr)
            # Decide if this failure should halt the whole script
            # For now, we continue but track the failure

    # 3. Initialize Git repository
    if not run_command("git init", "Initialize Git repository"):
        steps_succeeded = False

    # 4. Install pre-commit
    if steps_succeeded: # Only continue if previous steps were okay
        if not run_command(f"{sys.executable} -m pip install pre-commit", "Install pre-commit tool"):
            steps_succeeded = False
            print("--- Please install pre-commit manually ---", file=sys.stderr)

    # 5. Install Git hooks using pre-commit
    if steps_succeeded:
        if not run_command(f"{sys.executable} -m pre_commit install", "Install pre-commit Git hooks"):
            steps_succeeded = False
            print("--- Please run 'pre-commit install' manually ---", file=sys.stderr)

    # 6. Optional: Add all files and make initial commit
    if steps_succeeded:
        print("\nAttempting initial Git commit...")
        if run_command("git add .", "Stage all files"):
            commit_msg = "Initial commit from cookiecutter template"
            # Avoid committing sensitive key directly if possible, though it's needed for base settings
            if run_command(f'git commit -m "{commit_msg}"', "Create initial commit"):
                print("Successfully created initial commit.")
            else:
                print("--- Failed to create initial commit. Please commit manually. ---")
                steps_succeeded = False
        else:
            print("--- Failed to stage files. Please stage and commit manually. ---")
            steps_succeeded = False

    print("\n----------------------")
    if steps_succeeded:
        print("SUCCESS: Post-generation script finished.")
        print("SECRET_KEY generated and replaced.")
        print("Git initialized and pre-commit hooks installed.")
        print("Remember to create and activate a virtual environment for this project,")
        print("install requirements (`pip install -r requirements/local.txt`),")
        print("and ensure 'pre-commit' is available within that environment if needed.")
        print("\nIMPORTANT: Treat your `.env` file (once created from `.env.example`)")
        print("and the SECRET_KEY within it as confidential.")
    else:
        print("ERROR: Post-generation script encountered errors.")
        print("Please check the output above for details and complete setup manually.")
        sys.exit(1) # Exit with error code

if __name__ == '__main__':
    main() 