#!/usr/bin/env python3
"""
Simple setup script for the isotope ratios submission system.
This script helps users get started quickly.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("    Isotope Ratios Submission System Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['templates', 'static']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")
    return True

def setup_database():
    """Initialize the database."""
    print("🗄️  Initializing database...")
    try:
        from app import init_database
        init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def start_server():
    """Start the Flask server."""
    print("\n🚀 Starting server...")
    print("   The server will be available at:")
    print("   • Main page: http://localhost:5000")
    print("   • Admin panel: http://localhost:5000/admin")
    print("\n   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False
    return True

def open_browser():
    """Open browser to the main page."""
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Opening browser...")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:5000")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed at requirements installation.")
        print("   Please check your internet connection and try again.")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed at directory creation.")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed at database initialization.")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. The server will start automatically")
    print("   2. Your browser should open to the main page")
    print("   3. You can submit measurements directly to the database")
    print("   4. Use the admin panel to review submissions")
    
    # Open browser after a short delay
    import threading
    import time
    
    def delayed_open():
        time.sleep(2)
        open_browser()
    
    browser_thread = threading.Thread(target=delayed_open)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
