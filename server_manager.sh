#!/bin/bash
# Minimal Isotope Server Manager
# Single script for all server operations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/isotope_server.py"
PYTHON_PATH="/net/lem/data2/picos/pRT3-env/bin/python"
PID_FILE="$SCRIPT_DIR/data/server.pid"
LOG_FILE="$SCRIPT_DIR/data/server.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}$(date '+%H:%M:%S')${NC} $1"
}

error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Ensure data directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check if Python path exists, fallback to system python
if [ ! -f "$PYTHON_PATH" ]; then
    warning "Conda environment not found, using system python3"
    PYTHON_PATH="python3"
fi

get_server_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "$pid"
            return 0
        else
            # PID file exists but process is dead, clean it up
            rm -f "$PID_FILE"
        fi
    fi
    
    # Try to find by process name
    pgrep -f "isotope_server.py" || true
}

is_server_responding() {
    curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/status" 2>/dev/null | grep -q "200" && return 0
    
    # Fallback to python if curl fails (like before due to SSL issues)
    python3 -c "
import urllib.request, sys
try:
    urllib.request.urlopen('http://localhost:5000/api/status', timeout=5)
except:
    sys.exit(1)
" >/dev/null 2>&1
}

start_server() {
    local pid=$(get_server_pid)
    if [ -n "$pid" ]; then
        if is_server_responding; then
            success "Server already running (PID: $pid)"
            return 0
        else
            warning "Server process found but not responding, restarting..."
            stop_server
        fi
    fi
    
    log "Starting isotope server..."
    
    cd "$SCRIPT_DIR"
    
    # Start server with double-fork for complete detachment
    setsid nohup "$PYTHON_PATH" "$SERVER_SCRIPT" >/dev/null 2>&1 &
    local server_pid=$!
    
    # Save PID
    echo "$server_pid" > "$PID_FILE"
    
    # Wait for server to start
    sleep 3
    
    # Verify server started
    if ps -p "$server_pid" > /dev/null 2>&1; then
        # Wait for server to respond
        local attempts=0
        while [ $attempts -lt 10 ]; do
            if is_server_responding; then
                success "Server started successfully (PID: $server_pid)"
                
                # Show process details
                local ppid=$(ps -o ppid= -p "$server_pid" 2>/dev/null | tr -d ' ')
                local tty=$(ps -o tty= -p "$server_pid" 2>/dev/null | tr -d ' ')
                
                echo "📊 Process: PID=$server_pid, PPID=$ppid, TTY=$tty"
                
                if [ "$ppid" = "1" ] && [ "$tty" = "?" ]; then
                    success "Server is immortal (survives SSH disconnection)"
                fi
                
                echo "🌐 URLs:"
                echo "   - API: http://localhost:5000"
                echo "   - Admin: http://localhost:5000/admin.html"
                echo "   - Status: http://localhost:5000/api/status"
                
                return 0
            fi
            sleep 1
            attempts=$((attempts + 1))
        done
        
        error "Server started but not responding"
        return 1
    else
        error "Server failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_server() {
    local pid=$(get_server_pid)
    
    if [ -z "$pid" ]; then
        warning "No server process found"
        return 0
    fi
    
    log "Stopping server (PID: $pid)..."
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local attempts=0
    while [ $attempts -lt 5 ] && ps -p "$pid" > /dev/null 2>&1; do
        sleep 1
        attempts=$((attempts + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        warning "Force killing server..."
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        success "Server stopped"
    else
        error "Failed to stop server"
        return 1
    fi
}

restart_server() {
    log "Restarting server..."
    stop_server
    sleep 2
    start_server
}

status_server() {
    local pid=$(get_server_pid)
    
    echo "🚀 Isotope Ratios Server Status"
    echo "==============================="
    
    if [ -n "$pid" ]; then
        success "Server is running (PID: $pid)"
        
        # Show process details
        echo "📊 Process Details:"
        ps -o pid,ppid,sid,tty,etime,cmd -p "$pid" 2>/dev/null || echo "   Process details unavailable"
        
        # Check if responding
        if is_server_responding; then
            success "Server is responding"
        else
            error "Server process exists but not responding"
        fi
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "📝 Recent Logs:"
            tail -5 "$LOG_FILE" | sed 's/^/   /'
        fi
    else
        error "Server is not running"
        return 1
    fi
    
    echo ""
    echo "🌐 URLs:"
    echo "   - API: http://localhost:5000"
    echo "   - Admin: http://localhost:5000/admin.html"
    echo "   - Status: http://localhost:5000/api/status"
}

logs_server() {
    if [ -f "$LOG_FILE" ]; then
        if [ "$1" = "-f" ]; then
            tail -f "$LOG_FILE"
        else
            tail -20 "$LOG_FILE"
        fi
    else
        error "No log file found at $LOG_FILE"
        return 1
    fi
}

health_check() {
    local pid=$(get_server_pid)
    
    # Silent check for cron
    if [ -n "$pid" ] && is_server_responding; then
        # Server is healthy
        echo "$(date '+%Y-%m-%d %H:%M:%S'): Server healthy (PID: $pid)" >> "$LOG_FILE"
        return 0
    else
        # Server needs restart
        echo "$(date '+%Y-%m-%d %H:%M:%S'): Server unhealthy, restarting..." >> "$LOG_FILE"
        restart_server >> "$LOG_FILE" 2>&1
        return $?
    fi
}

usage() {
    echo "Isotope Server Manager"
    echo "Usage: $0 {start|stop|restart|status|logs|health|help}"
    echo ""
    echo "Commands:"
    echo "  start    Start the server"
    echo "  stop     Stop the server"
    echo "  restart  Restart the server"
    echo "  status   Show server status"
    echo "  logs     Show recent logs (add -f to follow)"
    echo "  health   Health check (silent, for cron)"
    echo "  help     Show this help"
}

case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status_server
        ;;
    logs)
        logs_server "$2"
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: ${1:-}"
        echo ""
        usage
        exit 1
        ;;
esac
