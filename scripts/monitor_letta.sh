#!/bin/bash

# Set path to project directory
PROJECT_DIR="/Users/myaiserver/Projects/letta-project"
LOG_DIR="$HOME/Library/Logs"
MONITOR_LOG="$LOG_DIR/letta-monitor.log"
MAX_LOG_SIZE=$((10 * 1024 * 1024))  # 10MB

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Rotate log if too large
if [ -f "$MONITOR_LOG" ] && [ $(stat -f%z "$MONITOR_LOG") -gt $MAX_LOG_SIZE ]; then
    mv "$MONITOR_LOG" "$MONITOR_LOG.old"
fi

# Run the monitor script and log output
cd "$PROJECT_DIR" && {
    echo "=== Monitor Run: $(date) ===" >> "$MONITOR_LOG"
    python3 scripts/check_letta_status.py 2>&1 | tee -a "$MONITOR_LOG"
    echo "=== End Run ===" >> "$MONITOR_LOG"
    echo "" >> "$MONITOR_LOG"
}
