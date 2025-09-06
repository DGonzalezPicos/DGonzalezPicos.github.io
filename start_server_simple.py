#!/usr/bin/env python3
"""
Simple HTTP server for the isotope ratios site.
Auto-detects Flask availability and provides appropriate functionality.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Try to import Flask
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    import csv
    import datetime
    import json
    import logging
    FLASK_AVAILABLE = True
    print("✅ Flask detected - full submission system available")
except ImportError:
    FLASK_AVAILABLE = False
    print("📧 Flask not available - using email fallback mode")

def start_simple_server():
    """Start a simple HTTP server for static files."""
    port = 8000
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory='/home/picos/public_html', **kwargs)
    
    print(f"🌐 Server starting on port {port}")
    print(f"   Main site: http://localhost:{port}/isotope_ratios.html")
    print(f"   Submission forms will use email fallback")
    print("   Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

def start_flask_server():
    """Start Flask server with full submission system."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    app = Flask(__name__)
    CORS(app)
    
    # Simple status endpoint
    @app.route('/api/status')
    def status():
        return jsonify({"status": "running", "flask": True})
    
    # Serve files
    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory('.', filename)
    
    print("🚀 Flask server starting...")
    print("   Main site: http://localhost:5000/isotope_ratios.html")
    print("   Admin panel: http://localhost:5000/admin.html")
    print("   Full submission system available")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    os.chdir('/home/picos/public_html')
    
    if FLASK_AVAILABLE:
        start_flask_server()
    else:
        start_simple_server()
