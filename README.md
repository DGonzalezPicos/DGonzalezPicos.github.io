# Isotope Ratios Database - Minimal System

A bulletproof, minimal Flask server for isotope ratio measurements submission and management.

## 🎯 Core Files

### Essential (3 files only)
- **`isotope_server.py`** - Complete Flask server with all functionality
- **`server_manager.sh`** - Single script for all server operations
- **`cron_health_check.sh`** - Minimal cron health monitoring

### Configuration
- **`server_config.json`** - Email and server settings (optional)
- **`admin.html`** - Web interface for reviewing submissions

### Data
- **`data/`** - CSV files and logs (auto-created)

## 🚀 Usage

### Server Management
```bash
# Start server (immortal, survives SSH disconnection)
./server_manager.sh start

# Check status
./server_manager.sh status

# Restart server
./server_manager.sh restart

# Stop server
./server_manager.sh stop

# View logs
./server_manager.sh logs
```

### API Endpoints
- **Status:** `http://localhost:5000/api/status`
- **Submissions:** `http://localhost:5000/api/submissions`
- **Submit:** `http://localhost:5000/api/submit` (POST)
- **Admin:** `http://localhost:5000/admin.html`

### Frontend Integration
The server automatically handles CORS for `http://localhost:8000` and provides all necessary endpoints for the isotope_ratios.html page.

## 🔧 Automated Monitoring

Cron job runs daily at 22:10 to ensure server health:
```bash
10 22 * * * /home/picos/public_html/cron_health_check.sh
```

## 🛡️ Features

- **SSH Survival:** Server detaches completely (PPID=1, TTY=?)
- **Auto-restart:** Health check automatically restarts failed servers
- **CORS Enabled:** Works with web frontends
- **Email Notifications:** Optional email alerts for new submissions
- **CSV Storage:** Simple, reliable data persistence
- **Comprehensive Logging:** All operations logged
- **Zero Configuration:** Works out of the box

## 📊 System Requirements

- Python 3.6+
- Flask and flask-cors packages
- Linux/Unix environment

That's it! Minimal, efficient, bulletproof. 🚀
