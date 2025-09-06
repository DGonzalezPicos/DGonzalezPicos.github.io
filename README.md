# Isotope Ratios Submission System

A web-based system for collecting and managing isotopic ratio measurements from astronomical observations.

## Features

- **User-friendly form**: Submit measurements with separate value and uncertainty fields
- **Custom categories**: Add custom object categories and instruments not in the predefined list
- **Admin panel**: Review and approve/reject submissions
- **Database storage**: SQLite database for persistent storage
- **Responsive design**: Works on desktop and mobile devices

## Quick Start

### Option 1: One-Click Setup (Recommended)

**Windows:**
```cmd
start.bat
```

**Mac/Linux:**
```bash
./start.sh
```

**Manual:**
```bash
python setup.py
```

This will automatically:
- Install all dependencies
- Initialize the database
- Start the server
- Open your browser

### Option 2: Manual Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server:**
   ```bash
   python start_server.py
   ```

3. **Access the Application:**
   - **Main page**: http://localhost:5000
   - **Admin panel**: http://localhost:5000/admin

## How It Works

### With Backend Server (Recommended)
- Form submissions go directly to the database
- Real-time status indicator shows server availability
- Admin panel for reviewing submissions
- Automatic data formatting and validation

### Without Backend Server (Fallback)
- Form submissions open your email client
- Pre-filled email with all form data
- Manual review process via email
- Still maintains all form functionality

## Form Fields

### Required Fields
- **Target Name**: Name of the astronomical object
- **Carbon Isotope Ratio Value**: ¹²C/¹³C ratio value
- **Reference**: Publication or data source

### Optional Fields
- **Category**: Object type (Super-Jupiter, Young Brown Dwarf, etc.)
- **Oxygen Isotope Ratio Value**: ¹⁶O/¹⁸O ratio value
- **Instrument**: Observing instrument
- **Notes**: Additional comments
- **Submitter Email**: For follow-up communication

### Uncertainty Handling
- **No uncertainty**: Leave uncertainty fields empty
- **Symmetric uncertainty**: Fill only the lower error field
- **Asymmetric uncertainty**: Fill both lower and upper error fields

## Database Schema

### Submissions Table
Stores all submitted measurements pending review.

### Approved Measurements Table
Stores approved measurements ready for integration into the main table.

## Exporting Data

To export approved measurements for integration:

```bash
python export_approved.py
```

This generates:
- `approved_measurements.csv`: CSV file with all approved data
- HTML table rows for manual integration into the main page

## Troubleshooting

### JSON Parsing Error
If you see "Unexpected token '<', "<!DOCTYPE "... is not valid JSON":
1. Make sure the Flask server is running
2. Check that you're accessing the correct URL (http://localhost:5000)
3. Verify the backend server started without errors

### Database Issues
- The database file (`isotope_submissions.db`) is created automatically
- Delete the file to reset the database if needed

## File Structure

```
├── app.py                 # Flask backend server
├── start_server.py        # Server startup script
├── export_approved.py     # Data export script
├── test_backend.py        # Backend testing script
├── requirements.txt       # Python dependencies
├── templates/
│   └── admin.html         # Admin panel template
├── isotope_ratios.html    # Main page with form
└── isotope_submissions.db # SQLite database (created automatically)
```