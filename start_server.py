#!/usr/bin/env python3
"""
Startup script for the isotope ratios submission system.
This script initializes the database and starts the Flask server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        sys.exit(1)

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    directories = ['templates', 'static']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ Directories created")

def setup_database():
    """Initialize the database."""
    print("Initializing database...")
    try:
        from app import init_database
        init_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

def start_server():
    """Start the Flask server."""
    print("\n" + "="*50)
    print("Starting Isotope Ratios Submission System")
    print("="*50)
    print("Server will be available at:")
    print("  - Main page: http://localhost:5000")
    print("  - Admin panel: http://localhost:5000/admin")
    print("\nPress Ctrl+C to stop the server")
    print("="*50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main function."""
    print("Isotope Ratios Submission System Setup")
    print("="*40)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Create directories
    create_directories()
    
    # Setup database
    setup_database()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
