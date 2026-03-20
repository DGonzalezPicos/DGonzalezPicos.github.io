#!/usr/bin/env python3
"""
Minimal Isotope Ratios Submission Server
Bulletproof Flask server for handling isotope measurements submissions.
"""

import sys
import os
import csv
import datetime
import json
import logging
from pathlib import Path

# Required imports
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
except ImportError as e:
    print("ERROR: Flask required. Install with: pip install flask flask-cors")
    sys.exit(1)

# Optional email functionality
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Configuration
DATA_DIR = 'data'
SUBMISSIONS_CSV = os.path.join(DATA_DIR, 'pending_submissions.csv')
APPROVED_CSV = os.path.join(DATA_DIR, 'approved_measurements.csv')
CONFIG_FILE = 'server_config.json'
LOG_FILE = os.path.join(DATA_DIR, 'server.log')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# CSV headers
SUBMISSION_HEADERS = [
    'submission_id', 'timestamp', 'status', 'target_name', 'category',
    'carbon_ratio', 'oxygen_ratio', 'instrument', 'reference', 'doi',
    'notes', 'submitter_email'
]

APPROVED_HEADERS = [
    'target_name', 'category', 'carbon_ratio', 'oxygen_ratio', 
    'instrument', 'reference', 'doi', 'notes', 'date_added'
]


def initialize_csv_files():
    """Initialize CSV files with headers if they don't exist."""
    for csv_file, headers in [(SUBMISSIONS_CSV, SUBMISSION_HEADERS), (APPROVED_CSV, APPROVED_HEADERS)]:
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(headers)


def load_config():
    """Load server configuration."""
    default_config = {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "admin_email": "picos@strw.leidenuniv.nl"
        },
        "auto_approve": False
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            logger.warning(f"Error loading config: {e}. Using defaults.")
    
    return default_config


def send_notification_email(submission_data, config):
    """Send notification email about new submission."""
    if not EMAIL_AVAILABLE or not config['email']['enabled']:
        return
    
    try:
        # Create email content
        subject = f"New Isotope Ratio Submission: {submission_data['target_name']}"
        
        body = f"""
New isotope ratio measurement submission received:

Target: {submission_data['target_name']}
Category: {submission_data.get('category', 'Not specified')}
Carbon Ratio: {submission_data['carbon_ratio']}
Oxygen Ratio: {submission_data.get('oxygen_ratio', 'Not provided')}
Reference: {submission_data['reference']}
DOI: {submission_data.get('doi', 'Not provided')}
Instrument: {submission_data.get('instrument', 'Not specified')}
Notes: {submission_data.get('notes', 'None')}

Submission ID: {submission_data['submission_id']}
Timestamp: {submission_data['timestamp']}

Review at: http://localhost:5000/admin.html
"""
        
        # Send email
        msg = MimeText(body)
        msg['Subject'] = subject
        msg['From'] = config['email']['sender_email']
        msg['To'] = config['email']['admin_email']
        
        with smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port']) as server:
            server.starttls()
            server.login(config['email']['sender_email'], config['email']['sender_password'])
            server.send_message(msg)
            
        logger.info(f"Notification email sent for submission {submission_data['submission_id']}")
        
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")


def read_submissions():
    """Read all submissions from CSV."""
    submissions = []
    if os.path.exists(SUBMISSIONS_CSV):
        try:
            with open(SUBMISSIONS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                submissions = list(reader)
        except Exception as e:
            logger.error(f"Error reading submissions: {e}")
    return submissions


def read_approved():
    """Read approved measurements from CSV."""
    approved = []
    if os.path.exists(APPROVED_CSV):
        try:
            with open(APPROVED_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                approved = list(reader)
        except Exception as e:
            logger.error(f"Error reading approved measurements: {e}")
    return approved


# Routes
@app.route('/')
def index():
    """Serve admin interface."""
    return send_from_directory('.', 'admin.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('.', filename)


@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint."""
    return jsonify({
        'status': 'running',
        'flask': True,
        'email_available': EMAIL_AVAILABLE,
        'port': 5000,
        'timestamp': datetime.datetime.now().isoformat()
    })


@app.route('/api/submissions', methods=['GET'])
def api_submissions():
    """Get all submissions."""
    try:
        submissions = read_submissions()
        approved = read_approved()
        return jsonify({
            'submissions': submissions,
            'approved': approved,
            'count': len(submissions),
            'approved_count': len(approved)
        })
    except Exception as e:
        logger.error(f"Error in submissions endpoint: {e}")
        return jsonify({'error': 'Failed to retrieve submissions'}), 500


@app.route('/api/submit', methods=['POST'])
def api_submit():
    """Submit new measurement."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['targetName', 'carbonRatio', 'reference']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create submission
        submission_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        submission_data = {
            'submission_id': submission_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'pending',
            'target_name': data['targetName'].strip(),
            'category': data.get('category', '').strip(),
            'carbon_ratio': data['carbonRatio'].strip(),
            'oxygen_ratio': data.get('oxygenRatio', '').strip(),
            'instrument': data.get('instrument', '').strip(),
            'reference': data['reference'].strip(),
            'doi': data.get('doi', '').strip(),
            'notes': data.get('notes', '').strip(),
            'submitter_email': data.get('submitterEmail', '').strip()
        }
        
        # Write to CSV
        with open(SUBMISSIONS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUBMISSION_HEADERS)
            writer.writerow(submission_data)
        
        logger.info(f"New submission received: {submission_id} for {submission_data['target_name']}")
        
        # Send notification email
        config = load_config()
        try:
            send_notification_email(submission_data, config)
        except Exception as e:
            logger.warning(f"Email notification failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Submission received successfully',
            'submission_id': submission_id
        })
        
    except Exception as e:
        logger.error(f"Error in submit endpoint: {e}")
        return jsonify({'error': 'Failed to process submission'}), 500


@app.route('/api/approve/<submission_id>', methods=['POST'])
def api_approve(submission_id):
    """Approve a submission."""
    try:
        submissions = read_submissions()
        submission = next((s for s in submissions if s['submission_id'] == submission_id), None)
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        # Add to approved measurements
        approved_data = {
            'target_name': submission['target_name'],
            'category': submission['category'],
            'carbon_ratio': submission['carbon_ratio'],
            'oxygen_ratio': submission['oxygen_ratio'],
            'instrument': submission['instrument'],
            'reference': submission['reference'],
            'doi': submission['doi'],
            'notes': submission['notes'],
            'date_added': datetime.datetime.now().isoformat()
        }
        
        with open(APPROVED_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=APPROVED_HEADERS)
            writer.writerow(approved_data)
        
        # Update submission status
        for s in submissions:
            if s['submission_id'] == submission_id:
                s['status'] = 'approved'
        
        # Rewrite submissions CSV
        with open(SUBMISSIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUBMISSION_HEADERS)
            writer.writeheader()
            writer.writerows(submissions)
        
        logger.info(f"Submission approved: {submission_id}")
        return jsonify({'success': True, 'message': 'Submission approved'})
        
    except Exception as e:
        logger.error(f"Error approving submission: {e}")
        return jsonify({'error': 'Failed to approve submission'}), 500


@app.route('/api/reject/<submission_id>', methods=['POST'])
def api_reject(submission_id):
    """Reject a submission."""
    try:
        submissions = read_submissions()
        
        # Update submission status
        updated = False
        for s in submissions:
            if s['submission_id'] == submission_id:
                s['status'] = 'rejected'
                updated = True
                break
        
        if not updated:
            return jsonify({'error': 'Submission not found'}), 404
        
        # Rewrite submissions CSV
        with open(SUBMISSIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUBMISSION_HEADERS)
            writer.writeheader()
            writer.writerows(submissions)
        
        logger.info(f"Submission rejected: {submission_id}")
        return jsonify({'success': True, 'message': 'Submission rejected'})
        
    except Exception as e:
        logger.error(f"Error rejecting submission: {e}")
        return jsonify({'error': 'Failed to reject submission'}), 500


def main():
    """Main server function."""
    print("🚀 Starting Isotope Ratios Submission Server")
    print("=" * 50)
    print(f"📍 API Server: http://localhost:5000")
    print(f"🌐 Admin Panel: http://localhost:5000/admin.html")
    print(f"📊 API Status: http://localhost:5000/api/status")
    print(f"📝 Log File: {LOG_FILE}")
    print("=" * 50)
    
    # Initialize CSV files
    initialize_csv_files()
    
    # Start server
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
