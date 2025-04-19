import os
import subprocess
import sys

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

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

def main():
    """Initialize Git, install pre-commit hooks."""
    print("\nPost-generation script starting...")
    print(f"Working directory: {PROJECT_DIRECTORY}")

    steps_succeeded = True

    # 1. Initialize Git repository
    if not run_command("git init", "Initialize Git repository"):
        steps_succeeded = False

    # 2. Install pre-commit
    # Note: This installs pre-commit potentially outside a virtualenv.
    # The user should ensure pre-commit is available in their project's venv later.
    if not run_command(f"{sys.executable} -m pip install pre-commit", "Install pre-commit tool"):
        steps_succeeded = False
        print("--- Please install pre-commit manually ---", file=sys.stderr)

    # 3. Install Git hooks using pre-commit
    # Needs pre-commit installed first
    if steps_succeeded: # Only run if previous steps were okay
        if not run_command(f"{sys.executable} -m pre_commit install", "Install pre-commit Git hooks"):
            steps_succeeded = False
            print("--- Please run 'pre-commit install' manually ---", file=sys.stderr)

    # Optional: Add all files and make initial commit
    if steps_succeeded:
        print("\nAttempting initial Git commit...")
        if run_command("git add .", "Stage all files"):
            commit_msg = "Initial commit from cookiecutter template"
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
        print("Git initialized and pre-commit hooks installed.")
        print("Remember to create and activate a virtual environment for this project,")
        print("install requirements (`pip install -r requirements/local.txt`),")
        print("and ensure 'pre-commit' is available within that environment if needed.")
    else:
        print("ERROR: Post-generation script encountered errors.")
        print("Please check the output above for details and complete setup manually.")
        sys.exit(1) # Exit with error code

if __name__ == '__main__':
    main() 