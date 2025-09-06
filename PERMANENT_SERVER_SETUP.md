# Permanent Server Setup Guide

## Keep Port 5000 Database Server Running Permanently

This guide shows you how to keep your isotope ratios submission server running permanently on port 5000, even when you close VSCode, terminals, or log out (but keep the machine running).

## 🚀 Quick Start (Recommended)

### Method 1: Using the Permanent Server Script

```bash
# Start permanent server
./run_permanent_server.sh start

# Check status
./run_permanent_server.sh status

# View logs
./run_permanent_server.sh logs

# Stop server
./run_permanent_server.sh stop

# Restart server
./run_permanent_server.sh restart
```

This method uses `nohup` to keep the server running even after closing terminals.

## 🔧 Advanced Methods

### Method 2: Using systemd (Most Robust)

This method creates a system service that automatically starts on boot and restarts if it crashes.

#### Step 1: Install the service
```bash
# Copy service file to systemd directory
sudo cp isotope-submission.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service (start on boot)
sudo systemctl enable isotope-submission

# Start the service now
sudo systemctl start isotope-submission
```

#### Step 2: Manage the service
```bash
# Check status
sudo systemctl status isotope-submission

# View logs
sudo journalctl -u isotope-submission -f

# Stop service
sudo systemctl stop isotope-submission

# Restart service
sudo systemctl restart isotope-submission

# Disable auto-start
sudo systemctl disable isotope-submission
```

### Method 3: Using tmux/screen

If you prefer terminal-based solutions:

```bash
# Start a new tmux session
tmux new-session -d -s isotope-server

# Run the server in the session
tmux send-keys -t isotope-server "cd /home/picos/public_html && prt3 && python3 submission_server.py" Enter

# Detach (server keeps running)
tmux detach

# Later, reattach to check
tmux attach -t isotope-server

# Kill the session
tmux kill-session -t isotope-server
```

### Method 4: Using nohup directly

```bash
# Start server with nohup
cd /home/picos/public_html
nohup bash -c "prt3 && python3 submission_server.py" > data/nohup.log 2>&1 &

# Check if running
ps aux | grep submission_server

# Stop (find PID and kill)
pkill -f submission_server.py
```

## 📊 Server Status Commands

### Check if server is responding:
```bash
# Test API status
curl -s http://localhost:5000/api/status | python3 -m json.tool

# Test with Python
python3 -c "
import urllib.request
try:
    response = urllib.request.urlopen('http://localhost:5000/api/status')
    print('✅ Server is responding')
    print(response.read().decode())
except Exception as e:
    print('❌ Server not responding:', e)
"
```

### Monitor server processes:
```bash
# Find submission server process
ps aux | grep submission_server | grep -v grep

# Check port 5000 usage
lsof -i :5000

# Check network connections
netstat -tlnp | grep :5000
```

## 🔄 Auto-Start on System Boot

### Option A: Using systemd (Recommended)
Follow Method 2 above and enable the service:
```bash
sudo systemctl enable isotope-submission
```

### Option B: Using crontab
```bash
# Edit crontab
crontab -e

# Add this line to start server on reboot
@reboot /home/picos/public_html/run_permanent_server.sh start
```

### Option C: Using .bashrc (starts when you log in)
```bash
# Add to ~/.bashrc
echo '
# Auto-start isotope submission server
if ! pgrep -f "submission_server.py" > /dev/null; then
    /home/picos/public_html/run_permanent_server.sh start
fi
' >> ~/.bashrc
```

## 🛠️ Troubleshooting

### Server won't start:
1. **Check if port 5000 is already in use:**
   ```bash
   lsof -i :5000
   # If something else is using it, kill it or change the port
   ```

2. **Check Python environment:**
   ```bash
   # Make sure prt3 environment works
   prt3
   python3 -c "import flask; print('Flask available')"
   ```

3. **Check permissions:**
   ```bash
   # Make sure you can write to the directory
   touch /home/picos/public_html/test.txt && rm /home/picos/public_html/test.txt
   ```

### Server stops unexpectedly:
1. **Check logs:**
   ```bash
   ./run_permanent_server.sh logs
   # or
   tail -f data/server.log
   ```

2. **Check system resources:**
   ```bash
   # Check memory usage
   free -h
   
   # Check disk space
   df -h
   ```

3. **Check for crashes:**
   ```bash
   # System logs
   journalctl -xe
   
   # Check if process was killed
   dmesg | grep -i "killed process"
   ```

## 🔒 Security Considerations

1. **Firewall**: Make sure port 5000 is only accessible from localhost unless you need external access
2. **User permissions**: The server runs as your user account
3. **Log files**: Monitor log files for any suspicious activity
4. **Regular updates**: Keep your Python environment and dependencies updated

## 📱 Quick Status Check

Create an alias for quick status checks:
```bash
# Add to ~/.bashrc
echo 'alias isotope-status="/home/picos/public_html/run_permanent_server.sh status"' >> ~/.bashrc
source ~/.bashrc

# Now you can just run:
isotope-status
```

## 🎯 Recommended Setup

**For Development:**
- Use Method 1 (permanent server script)
- Easy to start/stop, good logging

**For Production:**
- Use Method 2 (systemd service)
- Automatic startup, automatic restart on crashes
- Better integration with system monitoring

## Summary

After setting up any of these methods, your isotope ratios submission server will:

✅ **Run permanently** on port 5000  
✅ **Survive terminal closures** and VSCode sessions  
✅ **Continue running** when you log out (but machine stays on)  
✅ **Automatically restart** if it crashes (systemd method)  
✅ **Start automatically** on system boot (if configured)  

Your isotope ratios database will be accessible 24/7 for submissions and admin management!
