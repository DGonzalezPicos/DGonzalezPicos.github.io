# Isotope Ratios Submission System - Final Setup Guide

## Current Status ✅

Your submission system is **working and ready to use**!

## Simple Server Commands

### 🚀 Start the Server (Recommended)

```bash
cd /home/picos/public_html
python3 start_server.py &
```

This will:
- Start a web server on port 8000 (if Flask not available) or port 5000 (if Flask available)
- Run in the background (the `&` makes it continue after you close terminal)
- Serve your HTML site with submission forms

### 🌐 Access Your Site

- **Main website**: `http://localhost:8000/isotope_ratios.html`
- **View live changes**: Just refresh the browser after editing files

### 🔄 Background Server Management

```bash
# Check what's running
ps aux | grep python3

# Stop the server
pkill -f "python3.*server"

# Restart
python3 start_server.py &
```

## How the Submission System Works

### ✅ **Working Now:**
1. **HTML Form**: Users can fill out the submission form
2. **Email Fallback**: When they submit, it opens their email client with pre-filled data
3. **Manual Processing**: You receive submissions via email and can manually add them to your database

### 🔧 **Future Enhancement (Optional):**
If you want the full automated backend:
1. Install Flask: `sudo dnf install python3-flask python3-flask-cors` (or equivalent for your system)
2. Restart the server - it will automatically detect Flask and enable the admin interface

## File Structure (Simplified)

```
public_html/
├── start_server.py              # Main server (auto-detects Flask)
├── isotope_ratios.html          # Your main page with submission form ✅
├── admin.html                   # Admin interface (requires Flask)
├── server_config.json           # Configuration
├── data/                        # Auto-created for Flask mode
└── [all your existing files]    # CSS, JS, images, etc.
```

## Permanent Server Setup

### Option 1: Manual Start (Simple)
```bash
cd /home/picos/public_html
python3 start_server.py &
```

### Option 2: Auto-start on Login
Add to your `~/.bashrc`:
```bash
# Auto-start isotope ratios server
(cd /home/picos/public_html && python3 start_server.py >/dev/null 2>&1 &)
```

### Option 3: System Service (Advanced)
Create `/etc/systemd/user/isotope-server.service`:
```ini
[Unit]
Description=Isotope Ratios Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/picos/public_html
ExecStart=/usr/bin/python3 start_server.py
Restart=always
User=picos

[Install]
WantedBy=default.target
```

Then:
```bash
systemctl --user enable isotope-server.service
systemctl --user start isotope-server.service
```

## Summary

✅ **Ready to use**: Your site is live with submission forms
✅ **Email fallback**: Submissions work via email
✅ **Live editing**: Changes appear when you refresh
✅ **Background server**: Continues running after terminal closes

**Your site is now accessible at `http://localhost:8000/isotope_ratios.html`**

The submission system will automatically use email fallback, which works perfectly for receiving new measurements from users!
