#!/usr/bin/env python3
"""
Flask submission server for isotope ratios measurements.
Runs on port 5000 specifically for handling form submissions.
Your main HTML site should continue running on port 8000.
"""

import sys
import os
import csv
import datetime
import json
import logging
from pathlib import Path

# Try to import Flask
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError as e:
    print("=" * 60)
    print("ERROR: Flask is required for the submission system")
    print("Your HTML site on port 8000 will continue to work fine.")
    print("")
    print("To enable submissions, install Flask:")
    print("  sudo dnf install python3-flask python3-flask-cors")
    print("  # or")
    print("  sudo apt install python3-flask python3-flask-cors")
    print("=" * 60)
    sys.exit(1)

# Try to import email modules (optional)
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    print("Warning: Email functionality not available (this is normal)")
    EMAIL_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
DATA_DIR = 'data'
SUBMISSIONS_CSV = os.path.join(DATA_DIR, 'pending_submissions.csv')
APPROVED_CSV = os.path.join(DATA_DIR, 'approved_measurements.csv')
CONFIG_FILE = 'server_config.json'

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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
    if not os.path.exists(SUBMISSIONS_CSV):
        with open(SUBMISSIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(SUBMISSION_HEADERS)
    
    if not os.path.exists(APPROVED_CSV):
        with open(APPROVED_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(APPROVED_HEADERS)


def generate_submission_id():
    """Generate a unique submission ID."""
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]


def load_config():
    """Load server configuration from JSON file."""
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
            logger.error(f"Error loading config: {e}")
    
    return default_config


def send_notification_email(submission_data, config):
    """Send notification email to admin about new submission."""
    if not config['email']['enabled']:
        logger.info("Email notifications disabled")
        return
        
    if not EMAIL_AVAILABLE:
        logger.info("Email functionality not available - skipping email notification")
        return
    
    try:
        msg = MimeMultipart()
        msg['From'] = config['email']['sender_email']
        msg['To'] = config['email']['admin_email']
        msg['Subject'] = f"New Isotope Ratio Measurement Submission: {submission_data['target_name']}"
        
        body = f"""
New measurement submission received for the isotope ratios database:

Submission ID: {submission_data['submission_id']}
Target Name: {submission_data['target_name']}
Category: {submission_data.get('category', 'Not specified')}
Carbon Ratio (¹²C/¹³C): {submission_data['carbon_ratio']}
Oxygen Ratio (¹⁶O/¹⁸O): {submission_data.get('oxygen_ratio', 'Not provided')}
Instrument: {submission_data.get('instrument', 'Not specified')}
Reference: {submission_data['reference']}
DOI: {submission_data.get('doi', 'Not provided')}
Notes: {submission_data.get('notes', 'None')}
Submitter Email: {submission_data.get('submitter_email', 'Not provided')}

Submitted on: {submission_data['timestamp']}

Please review this submission in the admin interface:
http://localhost:5000/admin.html
        """.strip()
        
        msg.attach(MimeText(body, 'plain'))
        
        server = smtplib.SMTP(config['email']['smtp_server'], config['email']['smtp_port'])
        server.starttls()
        server.login(config['email']['sender_email'], config['email']['sender_password'])
        text = msg.as_string()
        server.sendmail(config['email']['sender_email'], config['email']['admin_email'], text)
        server.quit()
        
        logger.info(f"Notification email sent for submission {submission_data['submission_id']} to {config['email']['admin_email']}")
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")


# Flask routes
@app.route('/')
def serve_index():
    """Serve the main HTML file."""
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('.', filename)


@app.route('/api/status', methods=['GET'])
def server_status():
    """Check if server is running."""
    return jsonify({
        "status": "running", 
        "timestamp": datetime.datetime.now().isoformat(),
        "port": 5000,
        "flask": True,
        "email_available": EMAIL_AVAILABLE
    })


@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get all pending submissions (for admin interface)."""
    try:
        submissions = []
        if os.path.exists(SUBMISSIONS_CSV):
            with open(SUBMISSIONS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                submissions = list(reader)
        
        return jsonify({"success": True, "submissions": submissions})
    except Exception as e:
        logger.error(f"Error retrieving submissions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/submit', methods=['POST'])
def submit_measurement():
    """Handle new measurement submissions."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['targetName', 'carbonRatio', 'reference']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False, 
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create submission record
        submission_id = generate_submission_id()
        timestamp = datetime.datetime.now().isoformat()
        
        submission_data = {
            'submission_id': submission_id,
            'timestamp': timestamp,
            'status': 'pending',
            'target_name': data['targetName'],
            'category': data.get('category', ''),
            'carbon_ratio': data['carbonRatio'],
            'oxygen_ratio': data.get('oxygenRatio', ''),
            'instrument': data.get('instrument', ''),
            'reference': data['reference'],
            'doi': data.get('doi', ''),
            'notes': data.get('notes', ''),
            'submitter_email': data.get('submitterEmail', '')
        }
        
        # Save to CSV
        with open(SUBMISSIONS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUBMISSION_HEADERS)
            writer.writerow(submission_data)
        
        # Send email notification
        config = load_config()
        try:
            send_notification_email(submission_data, config)
        except Exception as e:
            logger.warning(f"Could not send email notification: {e}")
        
        logger.info(f"New submission received: {submission_id} - {data['targetName']}")
        
        return jsonify({
            "success": True, 
            "submission_id": submission_id,
            "message": "Submission received successfully"
        })
        
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/approve/<submission_id>', methods=['POST'])
def approve_submission(submission_id):
    """Approve a pending submission."""
    try:
        # Read all submissions
        submissions = []
        with open(SUBMISSIONS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            submissions = list(reader)
        
        # Find the submission to approve
        approved_submission = None
        remaining_submissions = []
        
        for submission in submissions:
            if submission['submission_id'] == submission_id:
                approved_submission = submission
                submission['status'] = 'approved'
            remaining_submissions.append(submission)
        
        if not approved_submission:
            return jsonify({"success": False, "error": "Submission not found"}), 404
        
        # Update submissions CSV
        with open(SUBMISSIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUBMISSION_HEADERS)
            writer.writeheader()
            writer.writerows(remaining_submissions)
        
        # Add to approved measurements
        approved_data = {
            'target_name': approved_submission['target_name'],
            'category': approved_submission['category'],
            'carbon_ratio': approved_submission['carbon_ratio'],
            'oxygen_ratio': approved_submission['oxygen_ratio'],
            'instrument': approved_submission['instrument'],
            'reference': approved_submission['reference'],
            'doi': approved_submission['doi'],
            'notes': approved_submission['notes'],
            'date_added': datetime.datetime.now().isoformat()
        }
        
        with open(APPROVED_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=APPROVED_HEADERS)
            writer.writerow(approved_data)
        
        logger.info(f"Submission approved: {submission_id}")
        return jsonify({"success": True, "message": "Submission approved"})
        
    except Exception as e:
        logger.error(f"Error approving submission {submission_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/reject/<submission_id>', methods=['POST'])
def reject_submission(submission_id):
    """Reject a pending submission."""
    try:
        # Read all submissions
        submissions = []
        with open(SUBMISSIONS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            submissions = list(reader)
        
        # Find and update the submission
        found = False
        for submission in submissions:
            if submission['submission_id'] == submission_id:
                submission['status'] = 'rejected'
                found = True
                break
        
        if not found:
            return jsonify({"success": False, "error": "Submission not found"}), 404
        
        # Update CSV
        with open(SUBMISSIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUBMISSION_HEADERS)
            writer.writeheader()
            writer.writerows(submissions)
        
        logger.info(f"Submission rejected: {submission_id}")
        return jsonify({"success": True, "message": "Submission rejected"})
        
    except Exception as e:
        logger.error(f"Error rejecting submission {submission_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    # Change to the correct directory
    os.chdir('/home/picos/public_html')
    
    # Initialize CSV files
    initialize_csv_files()
    
    print("🚀 Starting Isotope Ratios Submission Server")
    print("=" * 50)
    print("📍 Submission server: http://localhost:5000")
    print("🌐 Admin panel: http://localhost:5000/admin.html")
    print("📊 API status: http://localhost:5000/api/status")
    print("")
    print("📝 Your main HTML site should continue running on port 8000")
    print("📧 Email warning (if shown) is normal and expected")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure port 5000 is not already in use")
        sys.exit(1)
