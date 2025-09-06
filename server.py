#!/usr/bin/env python3
"""
Isotope Ratios Submission Server
Production-ready Flask server with daemon capabilities
"""

import sys
import os
import signal
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the Flask app from start_server
try:
    from start_server import app, initialize_csv_files, logger
except ImportError as e:
    if "flask" in str(e).lower():
        print("Flask is not installed. The server requires Flask to run.")
        print("Since pip has SSL issues in your environment, let's use the system directly.")
        print("")
        print("Please run the server directly instead:")
        print("  python3 start_server.py")
        print("")
        print("The server will handle the Flask import more gracefully.")
    else:
        print(f"Error importing Flask app: {e}")
        print("Make sure start_server.py is in the same directory")
    sys.exit(1)

# Configuration
PID_FILE = Path(__file__).parent / "server.pid"
LOG_FILE = Path(__file__).parent / "server.log"
PORT = 5000
HOST = "0.0.0.0"


def is_server_running():
    """Check if server is already running."""
    if not PID_FILE.exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Process doesn't exist or PID file is corrupted
        PID_FILE.unlink(missing_ok=True)
        return False


def write_pid():
    """Write current process PID to file."""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def remove_pid():
    """Remove PID file."""
    PID_FILE.unlink(missing_ok=True)


def signal_handler(signum, frame):
    """Handle termination signals."""
    logger.info("Received termination signal, shutting down gracefully...")
    remove_pid()
    sys.exit(0)


def start_server(background=False):
    """Start the Flask server."""
    if is_server_running():
        print("Server is already running!")
        print(f"To stop it, run: {sys.argv[0]} stop")
        return False
    
    # Initialize CSV files
    initialize_csv_files()
    
    if background:
        # Fork to background
        if os.fork() > 0:
            print("Server started in background")
            print(f"- Main site: http://localhost:{PORT}/isotope_ratios.html")
            print(f"- Admin panel: http://localhost:{PORT}/admin")
            print(f"- PID file: {PID_FILE}")
            print(f"- Log file: {LOG_FILE}")
            print(f"To stop: {sys.argv[0]} stop")
            return True
        
        # Child process
        os.setsid()  # Create new session
        
        # Redirect stdout/stderr to log file
        with open(LOG_FILE, 'a') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Write PID file
    write_pid()
    
    try:
        if not background:
            print("Starting Isotope Ratios Submission Server...")
            print("=" * 50)
            print(f"- Main site: http://localhost:{PORT}/isotope_ratios.html")
            print(f"- Admin panel: http://localhost:{PORT}/admin")
            print("")
            print("Note: Email warning is normal and expected.")
            print("Press Ctrl+C to stop the server")
            print("")
        
        # Run Flask app
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    
    except Exception as e:
        logger.error(f"Server error: {e}")
        remove_pid()
        sys.exit(1)
    finally:
        remove_pid()


def stop_server():
    """Stop the running server."""
    if not is_server_running():
        print("Server is not running")
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        print(f"Stopping server (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        
        # Wait a moment and check if it stopped
        import time
        time.sleep(2)
        
        if not is_server_running():
            print("Server stopped successfully")
            return True
        else:
            print("Server didn't stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)
            remove_pid()
            print("Server force-stopped")
            return True
    
    except Exception as e:
        print(f"Error stopping server: {e}")
        remove_pid()
        return False


def server_status():
    """Check and display server status."""
    if is_server_running():
        with open(PID_FILE, 'r') as f:
            pid = f.read().strip()
        
        print("✅ Server is running")
        print(f"   PID: {pid}")
        print(f"   Main site: http://localhost:{PORT}/isotope_ratios.html")
        print(f"   Admin panel: http://localhost:{PORT}/admin")
        
        if LOG_FILE.exists():
            print(f"   Log file: {LOG_FILE}")
    else:
        print("❌ Server is not running")
        print(f"   To start: {sys.argv[0]} start [--background]")


def show_logs():
    """Show recent server logs."""
    if not LOG_FILE.exists():
        print("No log file found")
        return
    
    print("Recent server logs:")
    print("-" * 40)
    
    try:
        # Show last 50 lines
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                print(line.rstrip())
    except Exception as e:
        print(f"Error reading log file: {e}")


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description="Isotope Ratios Submission Server")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the server')
    start_parser.add_argument('--background', '-d', action='store_true',
                             help='Run server in background (daemon mode)')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop the server')
    
    # Status command
    subparsers.add_parser('status', help='Show server status')
    
    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart the server')
    restart_parser.add_argument('--background', '-d', action='store_true',
                               help='Run server in background (daemon mode)')
    
    # Logs command
    subparsers.add_parser('logs', help='Show recent server logs')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'start':
        start_server(background=args.background)
    
    elif args.command == 'stop':
        stop_server()
    
    elif args.command == 'status':
        server_status()
    
    elif args.command == 'restart':
        if is_server_running():
            stop_server()
            import time
            time.sleep(1)
        start_server(background=args.background)
    
    elif args.command == 'logs':
        show_logs()


if __name__ == '__main__':
    main()
