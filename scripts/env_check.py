#!/usr/bin/env python3
"""
Cross-Device Development Environment Tracking

Comprehensive system and development environment information manager.
Optimized for Mac mini and MacBook Air synchronization.
"""

import os
import platform
import socket
import uuid
import json
import subprocess
from datetime import datetime
from typing import Dict, Any

class DeviceEnvironment:
    def __init__(self):
        """Initialize device-specific tracking."""
        self.devices = {
            'mac_mini': {
                'hostname': 'mac-mini-m1',
                'primary_user': 'myaiserver',
                'chip': 'Apple M1'
            },
            'macbook_air': {
                'hostname': 'macbook-air-m1',
                'primary_user': 'user',
                'chip': 'Apple M1'
            }
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information."""
        current_hostname = socket.gethostname().lower()
        
        # Determine current device
        current_device = next(
            (device for device, info in self.devices.items() 
             if info['hostname'].lower() in current_hostname), 
            'unknown'
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "device": {
                "name": current_device,
                "hostname": current_hostname,
                "machine_id": str(uuid.getnode())
            },
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine()
            },
            "hardware": {
                "processor": platform.processor(),
                "architecture": platform.architecture()[0]
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
                "active_branch": self.get_git_branch()
            }
        }
    
    def get_git_branch(self) -> str:
        """Retrieve current Git branch with error handling."""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                cwd=project_root
            ).decode().strip()
            return branch
        except Exception as e:
            return f"unknown (Error: {str(e)})"
    
    def log_environment(self) -> Dict[str, Any]:
        """Log environment information with advanced tracking."""
        info = self.get_system_info()
        log_file = os.path.expanduser('~/Library/Logs/windsurf_device_sync.json')
        
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
        
        # Keep only last 100 entries
        logs = logs[-100:]
        
        # Write updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return info
    
    def display_environment(self) -> None:
        """Display current environment information with device-specific details."""
        info = self.get_system_info()
        
        print("\n🖥️  Windsurf Cross-Device Environment 🖥️")
        print("=" * 50)
        print(f"Device: {info['device']['name'].replace('_', ' ').title()}")
        print(f"Hostname: {info['device']['hostname']}")
        print(f"Operating System: {info['os']['system']} {info['os']['release']}")
        print(f"Processor: {info['hardware']['processor']} ({info['hardware']['architecture']})")
        print(f"Current User: {info['user']['name']}")
        print(f"Project Branch: {info['development']['active_branch']}")
        print(f"Timestamp: {info['timestamp']}")
        print("=" * 50)
    
    def sync_project(self) -> None:
        """
        Synchronize project across devices using Git and environment tracking.
        Provides recommendations for maintaining consistency.
        """
        try:
            # Fetch latest changes
            subprocess.run(["git", "fetch", "origin"], check=True)
            
            # Check for divergence
            status = subprocess.check_output(
                ["git", "status", "-sb"], 
                universal_newlines=True
            )
            
            print("\n🔄 Project Synchronization Status:")
            print("-" * 40)
            print(status)
            
            # Recommend actions
            if "behind" in status:
                print("\n⚠️  Recommendation: Pull latest changes")
                print("   Run: git pull origin main")
            
            if "ahead" in status:
                print("\n⚠️  Recommendation: Push your changes")
                print("   Run: git push origin main")
        
        except subprocess.CalledProcessError as e:
            print(f"Sync error: {e}")

def main():
    """Main execution point for environment tracking."""
    env_tracker = DeviceEnvironment()
    env_tracker.log_environment()
    env_tracker.display_environment()
    env_tracker.sync_project()

if __name__ == '__main__':
    main()
