#!/usr/bin/env python3
"""
Letta server status check and self-repair script with AI-powered diagnostics.
Monitors essential components and attempts to fix common issues automatically.
"""
import os
import sys
import json
import time
import asyncio
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from ai_diagnostics import AITroubleshooter

class LettaRepair:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.repair_log = []
        self.ai_troubleshooter = AITroubleshooter()
        
    def log_repair(self, component: str, action: str, success: bool):
        """Log repair attempts for auditing."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.repair_log.append({
            'timestamp': timestamp,
            'component': component,
            'action': action,
            'success': success
        })
        
    async def get_ai_recommendation(self, error: str) -> str:
        """Get AI-powered fix recommendation."""
        return self.ai_troubleshooter.get_quick_fix(error)
        
    def restart_docker_container(self) -> bool:
        """Restart the Letta Docker container."""
        try:
            subprocess.run(['docker-compose', 'restart', 'letta-server'], 
                         cwd=self.project_root, check=True, capture_output=True)
            time.sleep(5)  # Wait for container to fully start
            return True
        except Exception as e:
            print(f"Failed to restart Docker container: {e}")
            return False
            
    def start_docker_daemon(self) -> bool:
        """Start the Docker daemon if it's not running."""
        try:
            subprocess.run(['open', '-a', 'Docker'], check=True)
            time.sleep(10)  # Wait for Docker to start
            return True
        except Exception as e:
            print(f"Failed to start Docker: {e}")
            return False
            
    def fix_log_permissions(self, log_file: str) -> bool:
        """Fix log file permissions."""
        try:
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
            if not os.path.exists(log_file):
                open(log_file, 'a').close()
            os.chmod(log_file, 0o644)
            return True
        except Exception as e:
            print(f"Failed to fix log permissions: {e}")
            return False
            
    def reload_launch_agent(self) -> bool:
        """Reload the launch agent configuration."""
        try:
            plist_path = os.path.expanduser('~/Library/LaunchAgents/com.letta.server.plist')
            subprocess.run(['launchctl', 'unload', plist_path], capture_output=True)
            time.sleep(1)
            subprocess.run(['launchctl', 'load', plist_path], check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Failed to reload launch agent: {e}")
            return False

def get_recent_logs(lines: int = 50) -> str:
    """Get recent lines from the Letta server logs."""
    log_file = os.path.expanduser("~/Library/Logs/letta-server.log")
    error_log = os.path.expanduser("~/Library/Logs/letta-server.error.log")
    
    logs = []
    for file in [log_file, error_log]:
        try:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.readlines()
                    logs.extend(content[-lines:])
        except Exception as e:
            logs.append(f"Error reading {file}: {str(e)}")
    
    return "".join(logs)

def check_docker_status() -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Check if the Letta Docker container is running."""
    try:
        # First check if Docker daemon is running
        daemon_check = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if daemon_check.returncode != 0:
            return False, "Docker daemon status", "daemon_not_running", daemon_check.stderr
            
        result = subprocess.run(
            ['docker-compose', 'ps', '-q', 'letta-server'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        if not result.stdout.strip():
            return False, "Docker container status", "container_not_running", "Container not found"
        return True, "Docker container status", None, None
    except Exception as e:
        return False, f"Docker error: {str(e)}", "docker_error", str(e)

def check_server_health() -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Check if the Letta server health endpoint is responding."""
    try:
        response = requests.get('http://localhost:8284', timeout=5)
        if response.status_code != 200:
            return False, "Server health check", "unhealthy_response", f"Status code: {response.status_code}"
        return True, "Server health check", None, None
    except requests.exceptions.ConnectionError as e:
        return False, "Server health check", "connection_failed", str(e)
    except Exception as e:
        return False, f"Server health error: {str(e)}", "health_check_error", str(e)

def check_gemini_config() -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Check if Gemini API key is configured."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' not in content:
                return False, "Gemini API key configuration", "key_missing", "API key not found in .env"
            return True, "Gemini API key configuration", None, None
    except Exception as e:
        return False, f"Gemini config error: {str(e)}", "config_error", str(e)

def check_log_files() -> List[Tuple[bool, str, Optional[str], Optional[str]]]:
    """Check if log files exist and are writable."""
    log_files = [
        os.path.expanduser('~/Library/Logs/letta-server.log'),
        os.path.expanduser('~/Library/Logs/letta-server.error.log')
    ]
    results = []
    for log_file in log_files:
        exists = os.path.exists(log_file)
        writable = os.access(os.path.dirname(log_file), os.W_OK) if exists else False
        status = "OK" if exists and writable else "Missing or not writable"
        error_code = None if exists and writable else "log_file_error"
        error_details = None if exists and writable else f"File: {log_file}, Exists: {exists}, Writable: {writable}"
        results.append((exists and writable, f"Log file {os.path.basename(log_file)}: {status}", error_code, error_details))
    return results

def check_autostart() -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Check if the launch agent is properly configured."""
    plist_path = os.path.expanduser('~/Library/LaunchAgents/com.letta.server.plist')
    try:
        result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)
        is_loaded = 'com.letta.server' in result.stdout
        file_exists = os.path.exists(plist_path)
        if not file_exists:
            return False, "Auto-start configuration", "plist_missing", "Launch agent plist file not found"
        if not is_loaded:
            return False, "Auto-start configuration", "not_loaded", "Launch agent not loaded"
        return True, "Auto-start configuration", None, None
    except Exception as e:
        return False, f"Auto-start error: {str(e)}", "autostart_error", str(e)

async def main():
    print("\n=== Letta Server Status Check ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repairer = LettaRepair(project_root)
    
    # Run all checks
    checks = [
        check_docker_status(),
        check_server_health(),
        check_gemini_config(),
        check_autostart(),
        *check_log_files()
    ]
    
    # Prepare results for AI analysis
    check_results = []
    repairs_attempted = False
    all_passed = True
    
    for passed, message, error_code, error_details in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {message}")
        all_passed = all_passed and passed
        
        check_results.append({
            'passed': passed,
            'message': message,
            'error_code': error_code,
            'error_details': error_details
        })
        
        # Attempt repairs for failed checks
        if not passed and error_code:
            repairs_attempted = True
            print(f"  🔧 Attempting repair...")
            
            # Get AI recommendation first
            if error_details:
                ai_suggestion = await repairer.get_ai_recommendation(f"{message}: {error_details}")
                print(f"  🤖 AI Recommendation:\n{ai_suggestion}\n")
            
            if error_code == "daemon_not_running":
                success = repairer.start_docker_daemon()
                repairer.log_repair("Docker", "Start daemon", success)
                if success:
                    print("  ✅ Started Docker daemon")
                    
            elif error_code in ["container_not_running", "connection_failed", "unhealthy_response"]:
                success = repairer.restart_docker_container()
                repairer.log_repair("Docker", "Restart container", success)
                if success:
                    print("  ✅ Restarted Docker container")
                    
            elif error_code == "log_file_error":
                log_file = message.split(": ")[0].replace("Log file ", "")
                success = repairer.fix_log_permissions(os.path.expanduser(f"~/Library/Logs/{log_file}"))
                repairer.log_repair("Logs", f"Fix permissions for {log_file}", success)
                if success:
                    print("  ✅ Fixed log file permissions")
                    
            elif error_code in ["plist_missing", "not_loaded", "autostart_error"]:
                success = repairer.reload_launch_agent()
                repairer.log_repair("LaunchAgent", "Reload configuration", success)
                if success:
                    print("  ✅ Reloaded launch agent")
    
    # Get comprehensive AI analysis if there were any issues
    if not all_passed:
        print("\n=== AI Analysis ===")
        ai = AITroubleshooter()
        analysis = await ai.analyze_issues(
            check_results=check_results,
            recent_logs=get_recent_logs(),
            repair_history=repairer.repair_log if repairs_attempted else None
        )
        print(f"\n{analysis}")
    
    # Final status
    print(f"\nOverall Status: {'✅ All checks passed' if all_passed else '❌ Some checks failed'}")
    
    if repairs_attempted:
        print("\nRepair Log:")
        for entry in repairer.repair_log:
            status = "✅" if entry['success'] else "❌"
            print(f"{entry['timestamp']} - {status} {entry['component']}: {entry['action']}")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    asyncio.run(main())
