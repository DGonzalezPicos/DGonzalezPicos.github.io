#!/usr/bin/env python3
"""
Flask backend for isotope ratios measurement submission system.
Handles form submissions, data storage, and admin management.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import json
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Database configuration
DATABASE = 'isotope_submissions.db'

def init_database() -> None:
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_name TEXT NOT NULL,
            category TEXT,
            carbon_ratio TEXT NOT NULL,
            oxygen_ratio TEXT,
            instrument TEXT,
            reference TEXT NOT NULL,
            notes TEXT,
            submitter_email TEXT,
            status TEXT DEFAULT 'pending',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewer_notes TEXT
        )
    ''')
    
    # Create approved measurements table (for integration with main table)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approved_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER,
            target_name TEXT NOT NULL,
            category TEXT,
            carbon_ratio TEXT NOT NULL,
            oxygen_ratio TEXT,
            instrument TEXT,
            reference TEXT NOT NULL,
            notes TEXT,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (submission_id) REFERENCES submissions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Serve the main isotope ratios page."""
    return app.send_static_file('isotope_ratios.html')

@app.route('/api/submit', methods=['POST'])
def submit_measurement():
    """Handle form submission from frontend."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['targetName', 'carbonRatio', 'reference']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Insert submission into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions 
            (target_name, category, carbon_ratio, oxygen_ratio, instrument, 
             reference, notes, submitter_email, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (
            data['targetName'],
            data.get('category', ''),
            data['carbonRatio'],
            data.get('oxygenRatio', ''),
            data.get('instrument', ''),
            data['reference'],
            data.get('notes', ''),
            data.get('submitterEmail', '')
        ))
        
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"New submission received: ID {submission_id}, Target: {data['targetName']}")
        
        return jsonify({
            'success': True,
            'message': 'Measurement submitted successfully! It will be reviewed before being added to the database.',
            'submission_id': submission_id
        })
        
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your submission'
        }), 500

@app.route('/api/submissions')
def get_submissions():
    """Get all submissions for admin review."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM submissions 
            ORDER BY submitted_at DESC
        ''')
        
        submissions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'submissions': submissions
        })
        
    except Exception as e:
        logger.error(f"Error fetching submissions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch submissions'
        }), 500

@app.route('/api/approve/<int:submission_id>', methods=['POST'])
def approve_submission(submission_id: int):
    """Approve a submission and add to approved measurements."""
    try:
        data = request.get_json()
        reviewer_notes = data.get('reviewer_notes', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get submission details
        cursor.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
        submission = cursor.fetchone()
        
        if not submission:
            return jsonify({
                'success': False,
                'error': 'Submission not found'
            }), 404
        
        # Add to approved measurements
        cursor.execute('''
            INSERT INTO approved_measurements 
            (submission_id, target_name, category, carbon_ratio, oxygen_ratio, 
             instrument, reference, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            submission_id,
            submission['target_name'],
            submission['category'],
            submission['carbon_ratio'],
            submission['oxygen_ratio'],
            submission['instrument'],
            submission['reference'],
            submission['notes']
        ))
        
        # Update submission status
        cursor.execute('''
            UPDATE submissions 
            SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP, reviewer_notes = ?
            WHERE id = ?
        ''', (reviewer_notes, submission_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Submission {submission_id} approved")
        
        return jsonify({
            'success': True,
            'message': 'Submission approved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error approving submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to approve submission'
        }), 500

@app.route('/api/reject/<int:submission_id>', methods=['POST'])
def reject_submission(submission_id: int):
    """Reject a submission."""
    try:
        data = request.get_json()
        reviewer_notes = data.get('reviewer_notes', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE submissions 
            SET status = 'rejected', reviewed_at = CURRENT_TIMESTAMP, reviewer_notes = ?
            WHERE id = ?
        ''', (reviewer_notes, submission_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Submission {submission_id} rejected")
        
        return jsonify({
            'success': True,
            'message': 'Submission rejected'
        })
        
    except Exception as e:
        logger.error(f"Error rejecting submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to reject submission'
        }), 500

@app.route('/api/approved')
def get_approved_measurements():
    """Get all approved measurements for CSV export."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM approved_measurements 
            ORDER BY approved_at DESC
        ''')
        
        measurements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'measurements': measurements
        })
        
    except Exception as e:
        logger.error(f"Error fetching approved measurements: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch approved measurements'
        }), 500

@app.route('/admin')
def admin_panel():
    """Admin panel for reviewing submissions."""
    return render_template('admin.html')

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
