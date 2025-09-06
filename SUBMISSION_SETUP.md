# Isotope Ratios Submission System Setup

This document explains how to set up and use the measurement submission system for the isotope ratios database.

## Overview

The submission system consists of:
- **Frontend**: HTML form in `isotope_ratios.html` for users to submit measurements
- **Backend**: Flask server (`start_server.py`) to handle submissions and store data
- **Admin Interface**: Web interface (`admin.html`) to review and approve submissions
- **Data Storage**: CSV files for pending and approved measurements

## Quick Start

### Interactive Mode (stops when you close terminal):
```bash
./server.py start
```

### Background Mode (permanent server):
```bash
./server.py start --background
```

### Server Management:
```bash
./server.py status     # Check if server is running
./server.py stop       # Stop the server
./server.py restart    # Restart the server
./server.py logs       # View recent logs
```

### Access Your Site:
- **Main site**: `http://localhost:5000/isotope_ratios.html`
- **Admin panel**: `http://localhost:5000/admin`

**Note**: You may see a warning about email functionality - this is normal and expected. The submission system works perfectly without email notifications.

## File Structure

```
public_html/
├── server.py                    # Main server management script ⭐
├── start_server.py              # Flask backend (used by server.py)
├── start_submission_server.sh   # Quick start wrapper
├── server_config.json           # Server configuration
├── isotope_ratios.html          # Main database page with submission form
├── admin.html                  # Admin interface for reviewing submissions
├── SUBMISSION_SETUP.md         # This setup guide
└── data/                       # Created automatically
    ├── pending_submissions.csv     # Submissions awaiting review
    ├── approved_measurements.csv   # Approved measurements
    ├── server.pid                  # Process ID (when running in background)
    └── server.log                  # Server logs (when running in background)
```

## Detailed Setup

### 1. Backend Server Configuration

The server can be configured by editing `server_config.json`:

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "admin_email": "picos@strw.leidenuniv.nl"
  },
  "auto_approve": false
}
```

**Email Configuration (Optional)**:
- Set `"enabled": true` to receive email notifications for new submissions
- For Gmail, use an App Password instead of your regular password
- The admin will receive an email for each new submission

**Auto-approval**:
- Set `"auto_approve": true` to automatically approve all submissions (not recommended for production)

### 2. Starting the Server

#### For Development/Testing (Interactive Mode):
```bash
cd /home/picos/public_html
./server.py start
```
- Server runs in foreground
- Shows real-time logs
- Stops when you close terminal or press Ctrl+C

#### For Production (Background Mode):
```bash
cd /home/picos/public_html
./server.py start --background
```
- Server runs in background as daemon
- Continues running after you log out
- Logs written to `data/server.log`
- Process ID stored in `data/server.pid`

#### Server Management Commands:
```bash
./server.py status     # Check if server is running
./server.py stop       # Stop the background server
./server.py restart    # Restart the server
./server.py restart --background  # Restart in background mode
./server.py logs       # View recent server logs
```

The server runs on `http://localhost:5000`:
- **Main site**: `http://localhost:5000/isotope_ratios.html`
- **Admin interface**: `http://localhost:5000/admin`

#### Auto-Start on System Boot (Optional):
To make the server start automatically when your system boots:

1. Add to your shell profile (`.bashrc`, `.profile`, etc.):
   ```bash
   # Auto-start isotope ratios server
   if ! /home/picos/public_html/server.py status >/dev/null 2>&1; then
       /home/picos/public_html/server.py start --background
   fi
   ```

2. Or create a cron job:
   ```bash
   # Edit crontab
   crontab -e
   
   # Add this line to start server on reboot
   @reboot /home/picos/public_html/server.py start --background
   ```

### 3. Submission Workflow

#### For Users:
1. Visit the isotope ratios page
2. Click "Submit a Measurement" button
3. Fill out the form with:
   - **Required**: Target Name, Carbon Isotope Ratio, Reference
   - **Optional**: Category, Oxygen Isotope Ratio, Instrument, DOI, Notes, Email
4. Submit the form

#### For Administrators:
1. Access the admin panel at `/admin`
2. Review pending submissions
3. Approve or reject each submission
4. Approved submissions are automatically added to the database

### 4. Data Storage

**Pending Submissions** (`data/pending_submissions.csv`):
- Contains all submitted measurements awaiting review
- Fields: submission_id, timestamp, status, target_name, category, carbon_ratio, oxygen_ratio, instrument, reference, doi, notes, submitter_email

**Approved Measurements** (`data/approved_measurements.csv`):
- Contains approved measurements ready for integration into the main database
- Fields: target_name, category, carbon_ratio, oxygen_ratio, instrument, reference, doi, notes, date_added

## API Endpoints

The server provides the following API endpoints:

- `GET /api/status` - Check server status
- `GET /api/submissions` - Get all submissions (admin)
- `POST /api/submit` - Submit new measurement
- `POST /api/approve/<submission_id>` - Approve a submission
- `POST /api/reject/<submission_id>` - Reject a submission

## Fallback Mode

If the backend server is not running, the submission form automatically falls back to email mode:
- Creates a pre-filled email with the submission details
- Opens the user's default email client
- Sends the submission to the admin email address

## Security Considerations

1. **Admin Interface**: Currently accessible to anyone who knows the URL. Consider adding authentication for production use.

2. **Email Credentials**: Store email passwords securely. Use app-specific passwords for Gmail.

3. **Data Validation**: The server performs basic validation, but additional checks may be needed.

4. **CORS**: The server allows cross-origin requests. Restrict this in production if needed.

## Troubleshooting

### Server Won't Start
- Check if port 5000 is already in use: `lsof -i :5000`
- Install missing dependencies: `pip install -r requirements.txt`

### Submissions Not Working
- Check if the server is running: visit `http://localhost:5000/api/status`
- Check browser console for JavaScript errors
- Verify the form is sending data to the correct endpoint

### Email Notifications Not Working
- **Email Warning Message**: If you see "Warning: Email functionality not available", this is normal in some Python environments. The submission system works perfectly without email notifications.
- Verify email configuration in `server_config.json` if you want to enable notifications
- Check server logs for email-related errors
- Ensure the sender email has proper authentication (app passwords for Gmail)

### Admin Interface Not Loading Submissions
- Check if `data/pending_submissions.csv` exists and is readable
- Verify the server API endpoints are responding: `curl http://localhost:5000/api/submissions`

## Integration with Existing Database

To integrate approved measurements into your main isotope ratios table:

1. **Manual Integration**: 
   - Export approved measurements from `data/approved_measurements.csv`
   - Manually add entries to your main HTML table

2. **Automated Integration** (future enhancement):
   - Create a script to automatically update the HTML table
   - Generate new table rows from approved CSV data

## Next Steps

1. **Authentication**: Add login system for admin interface
2. **Database Integration**: Automate the process of adding approved measurements to the main table
3. **Enhanced Validation**: Add more sophisticated data validation
4. **Backup System**: Implement automatic backups of submission data
5. **Batch Operations**: Allow bulk approval/rejection of submissions

## Support

For issues or questions about the submission system, contact the developer or check the server logs for error details.
