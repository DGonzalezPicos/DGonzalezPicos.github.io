#!/bin/bash
# Minimal cron health check for isotope server
# Runs daily to ensure server stays healthy

# Set environment for cron
export PATH="/usr/local/bin:/usr/bin:/bin"
export HOME="/home/picos"

# Change to script directory
cd "$(dirname "$0")" || exit 1

# Run health check using server manager
./server_manager.sh health
