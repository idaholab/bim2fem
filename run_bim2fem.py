"""
BIM2FEM Web Interface Launcher
Click this file to start the web interface!
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path


def check_python():
    if sys.version_info < (3, 8):
        print("Python 3.8+ is required!")
        input("Press Enter to exit...")
        sys.exit(1)


def setup_environment():
    """Create venv and install dependencies if needed."""
    venv_path = Path("venv")

    if not venv_path.exists():
        print("Setting up environment (first time only)...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])

    # Use venv pip
    if sys.platform == "win32":
        pip = venv_path / "Scripts" / "pip"
        python = venv_path / "Scripts" / "python"
    else:
        pip = venv_path / "bin" / "pip"
        python = venv_path / "bin" / "python"

    print("Installing/updating dependencies...")
    subprocess.run([str(pip), "install", "-q", "-r", "requirements.txt"])

    return python


def main():
    print("=" * 50)
    print("BIM2FEM Web Interface")
    print("=" * 50)

    check_python()
    python_exe = setup_environment()

    # Auto-open browser after short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")

    from threading import Thread

    Thread(target=open_browser, daemon=True).start()

    print("\nStarting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    # Run Flask app
    subprocess.run([str(python_exe), "web/app.py"])


if __name__ == "__main__":
    main()
