#!/usr/bin/env python3
"""
Environment Verification and Tracking Script

Provides comprehensive system and development environment information.
"""

import os
import platform
import socket
import uuid
import json
from datetime import datetime

def get_system_info():
    """Collect detailed system information."""
    return {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "machine_id": str(uuid.getnode()),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine()
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation()
        },
        "user": {
            "name": os.getlogin(),
            "home_dir": os.path.expanduser('~')
        },
        "development": {
            "project_root": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "active_branch": get_git_branch()
        }
    }

def get_git_branch():
    """Retrieve current Git branch."""
    try:
        import subprocess
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ).decode().strip()
        return branch
    except Exception:
        return "unknown"

def log_environment():
    """Log environment information to a tracking file."""
    info = get_system_info()
    log_file = os.path.expanduser('~/Library/Logs/windsurf_env_tracking.json')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Read existing logs or create new
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    # Add current environment
    logs.append(info)
    
    # Keep only last 50 entries
    logs = logs[-50:]
    
    # Write updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return info

def display_environment():
    """Display current environment information."""
    info = get_system_info()
    print("\n🖥️  Windsurf Development Environment 🖥️")
    print("=" * 40)
    print(f"Hostname: {info['hostname']}")
    print(f"Operating System: {info['os']['system']} {info['os']['release']}")
    print(f"Current User: {info['user']['name']}")
    print(f"Project Branch: {info['development']['active_branch']}")
    print(f"Timestamp: {info['timestamp']}")
    print("=" * 40)

def main():
    """Main execution point."""
    log_environment()
    display_environment()

if __name__ == '__main__':
    main()
