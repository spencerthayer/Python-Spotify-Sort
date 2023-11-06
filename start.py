import subprocess
import sys
import webbrowser

def install_poetry():
    """Install Poetry if it's not already installed."""
    print("Installing Poetry...")
    installer_url = "https://install.python-poetry.org"
    try:
        subprocess.run(["curl", "-sSL", installer_url, "|", "python", "-"], check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while installing Poetry:", e)
        sys.exit(1)

def check_poetry_installed():
    """Check if Poetry is installed."""
    result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        install_poetry()
    else:
        print("Poetry is already installed.")

def create_poetry_env():
    """Create a Poetry virtual environment for the project."""
    print("Creating Poetry virtual environment...")
    subprocess.run(["poetry", "env", "use", "python"], check=True)

def install_dependencies():
    """Install project dependencies using Poetry."""
    print("Installing dependencies...")
    subprocess.run(["poetry", "install"], check=True)

def run_script(script_path):
    """Run a Python script using Poetry."""
    print(f"Running {script_path}...")
    subprocess.run(["poetry", "run", "python", script_path], check=True)

def main():
    check_poetry_installed()
    create_poetry_env()
    install_dependencies()
    # Run the refactored scripts
    run_script("src/playlist_save.py")
    run_script("src/playlist_sort.py")
    run_script("src/playlist_reorder.py")

if __name__ == "__main__":
    main()
