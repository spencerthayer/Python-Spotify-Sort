import shutil
import subprocess
import sys
import webbrowser

def create_poetry_env():
    """Create a Poetry virtual environment for the project."""
    print("Creating Poetry virtual environment...")
    subprocess.run(["poetry", "env", "use", "python3"], check=True)

def install_dependencies():
    """Install project dependencies using Poetry."""
    print("Installing dependencies...")
    subprocess.run(["poetry", "install"], check=True)

def run_script(script_path):
    """Run a Python script using Poetry."""
    print(f"Running {script_path}...")
    subprocess.run(["poetry", "run", "python3", script_path], check=True)

def main():
    create_poetry_env()
    install_dependencies()
    # Run the refactored scripts
    run_script("src/playlist_save.py")
    run_script("src/playlist_sort.py")
    run_script("src/playlist_reorder.py")

if __name__ == "__main__":
    main()
