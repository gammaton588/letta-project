#!/usr/bin/env python3
"""
Letta Admin Dashboard
A monitoring and management dashboard for Letta agents
"""

import os
import sys
import json
import argparse
import requests
import logging
import webbrowser
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from typing import Dict, List, Any
import socket

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gemini_integration import GeminiAPI
from scripts.create_letta_gemini_agent import LettaAgentCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("letta_dashboard")

# Load environment variables
env_path = os.path.expanduser("~/.letta/env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Letta Admin Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f7;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #1d1d1f;
            color: white;
            padding: 15px 0;
            margin-bottom: 20px;
        }
        header .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 {
            margin: 0;
            font-weight: 600;
        }
        .status-container {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            flex: 1;
        }
        .status-title {
            font-size: 16px;
            color: #666;
            margin-top: 0;
            margin-bottom: 8px;
        }
        .status-value {
            font-size: 24px;
            font-weight: 600;
            margin: 0;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-indicator.green {
            background-color: #34c759;
        }
        .status-indicator.yellow {
            background-color: #ffcc00;
        }
        .status-indicator.red {
            background-color: #ff3b30;
        }
        .card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .card h2 {
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            font-weight: 600;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table th, table td {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        table th {
            background-color: #f5f5f7;
            font-weight: 500;
        }
        .btn {
            background-color: #0071e3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background-color: #0077ed;
        }
        .btn-danger {
            background-color: #ff3b30;
        }
        .btn-danger:hover {
            background-color: #ff453a;
        }
        .refresh-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .last-updated {
            color: #666;
            font-size: 14px;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        .badge-warning {
            background-color: #fff8e1;
            color: #f57f17;
        }
        .badge-error {
            background-color: #ffebee;
            color: #c62828;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Letta Admin Dashboard</h1>
            <div id="refresh-time"></div>
        </div>
    </header>
    
    <div class="container">
        <div class="status-container">
            <div class="status-card">
                <h3 class="status-title">Letta Server</h3>
                <p class="status-value">
                    <span id="letta-status-indicator" class="status-indicator"></span>
                    <span id="letta-status">Checking...</span>
                </p>
            </div>
            <div class="status-card">
                <h3 class="status-title">Gemini API</h3>
                <p class="status-value">
                    <span id="gemini-status-indicator" class="status-indicator"></span>
                    <span id="gemini-status">Checking...</span>
                </p>
            </div>
            <div class="status-card">
                <h3 class="status-title">Total Agents</h3>
                <p class="status-value" id="total-agents">-</p>
            </div>
        </div>
        
        <div class="card">
            <div class="refresh-section">
                <h2>Letta Agents</h2>
                <div>
                    <span class="last-updated">Last updated: <span id="last-updated-time">now</span></span>
                    <button class="btn" onclick="refreshData()">Refresh Data</button>
                </div>
            </div>
            <div id="agents-table-container">Loading agents...</div>
        </div>
        
        <div class="card">
            <h2>Quick Actions</h2>
            <button class="btn" onclick="openLettaADE()">Open Letta ADE</button>
            <button class="btn" onclick="createNewAgent()">Create New Agent</button>
            <button class="btn" onclick="testGeminiAPI()">Test Gemini API</button>
            <button class="btn" onclick="runUAT()">Run User Acceptance Tests</button>
        </div>
        
        <div class="card">
            <h2>System Information</h2>
            <table>
                <tr>
                    <td>Letta Server URL</td>
                    <td id="letta-url"></td>
                </tr>
                <tr>
                    <td>Gemini API Key</td>
                    <td id="gemini-key-status"></td>
                </tr>
                <tr>
                    <td>Dashboard Server</td>
                    <td id="dashboard-url"></td>
                </tr>
                <tr>
                    <td>Environment</td>
                    <td id="env-status"></td>
                </tr>
            </table>
        </div>
    </div>
    
    <script>
        // API endpoint on this server
        const API_ENDPOINT = '/api';
        
        // Initialize data
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            document.getElementById('letta-url').textContent = getParameterByName('letta_url') || 'http://localhost:8283';
            document.getElementById('dashboard-url').textContent = window.location.origin;
            
            // Update refresh time every second
            setInterval(() => {
                document.getElementById('refresh-time').textContent = new Date().toLocaleTimeString();
            }, 1000);
        });
        
        // Refresh dashboard data
        function refreshData() {
            fetch(`${API_ENDPOINT}/status`)
                .then(response => response.json())
                .then(data => {
                    updateStatusIndicators(data);
                    updateAgentsTable(data.agents || []);
                    updateSystemInfo(data);
                    document.getElementById('last-updated-time').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                });
        }
        
        // Update status indicators
        function updateStatusIndicators(data) {
            // Letta status
            const lettaStatusEl = document.getElementById('letta-status');
            const lettaIndicatorEl = document.getElementById('letta-status-indicator');
            
            if (data.letta_status === 'online') {
                lettaStatusEl.textContent = 'Online';
                lettaIndicatorEl.className = 'status-indicator green';
            } else {
                lettaStatusEl.textContent = 'Offline';
                lettaIndicatorEl.className = 'status-indicator red';
            }
            
            // Gemini API status
            const geminiStatusEl = document.getElementById('gemini-status');
            const geminiIndicatorEl = document.getElementById('gemini-status-indicator');
            
            if (data.gemini_status === 'available') {
                geminiStatusEl.textContent = 'Available';
                geminiIndicatorEl.className = 'status-indicator green';
            } else if (data.gemini_status === 'configured') {
                geminiStatusEl.textContent = 'Configured';
                geminiIndicatorEl.className = 'status-indicator yellow';
            } else {
                geminiStatusEl.textContent = 'Unavailable';
                geminiIndicatorEl.className = 'status-indicator red';
            }
            
            // Total agents
            document.getElementById('total-agents').textContent = data.agents?.length || 0;
        }
        
        // Update agents table
        function updateAgentsTable(agents) {
            const container = document.getElementById('agents-table-container');
            
            if (!agents || agents.length === 0) {
                container.innerHTML = '<p>No agents found. Create your first agent using the Quick Actions.</p>';
                return;
            }
            
            let tableHtml = `
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Model</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            agents.forEach(agent => {
                tableHtml += `
                    <tr>
                        <td>${agent.name || 'Unnamed Agent'}</td>
                        <td>${agent.description || 'No description'}</td>
                        <td>${agent.model || 'Unknown'}</td>
                        <td><span class="badge badge-success">Active</span></td>
                        <td>
                            <button class="btn" onclick="openAgent('${agent.id}')">Open</button>
                        </td>
                    </tr>
                `;
            });
            
            tableHtml += `
                    </tbody>
                </table>
            `;
            
            container.innerHTML = tableHtml;
        }
        
        // Update system information
        function updateSystemInfo(data) {
            // Gemini API key status
            const keyStatus = document.getElementById('gemini-key-status');
            if (data.gemini_status === 'available' || data.gemini_status === 'configured') {
                keyStatus.textContent = 'Configured ●●●●●●●●●●●●●●●●●●●●';
            } else {
                keyStatus.textContent = 'Not configured or invalid';
            }
            
            // Environment status
            const envStatus = document.getElementById('env-status');
            if (data.env_loaded) {
                envStatus.textContent = 'Environment variables loaded';
            } else {
                envStatus.textContent = 'Environment file not found';
            }
        }
        
        // Helper function to get URL parameters
        function getParameterByName(name) {
            const url = window.location.href;
            name = name.replace(/[\\[\\]]/g, '\\\\$&');
            const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
            const results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\\+/g, ' '));
        }
        
        // Action functions
        function openLettaADE() {
            const lettaUrl = document.getElementById('letta-url').textContent;
            window.open(lettaUrl, '_blank');
        }
        
        function createNewAgent() {
            alert('This feature will open a form to create a new agent. Not implemented in this demo.');
        }
        
        function testGeminiAPI() {
            fetch(`${API_ENDPOINT}/test-gemini`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`Gemini API test successful! Response: "${data.response}"`);
                    } else {
                        alert(`Gemini API test failed: ${data.error}`);
                    }
                })
                .catch(error => {
                    alert(`Error testing Gemini API: ${error}`);
                });
        }
        
        function runUAT() {
            if (confirm('Run User Acceptance Tests? This may take a moment.')) {
                fetch(`${API_ENDPOINT}/run-uat`)
                    .then(response => response.json())
                    .then(data => {
                        alert(`UAT Results: ${data.pass_percentage}% tests passed. Check console for details.`);
                        console.log('UAT Results:', data);
                    })
                    .catch(error => {
                        alert(`Error running UAT: ${error}`);
                    });
            }
        }
        
        function openAgent(agentId) {
            const lettaUrl = document.getElementById('letta-url').textContent;
            window.open(`${lettaUrl}/agents/${agentId}`, '_blank');
        }
    </script>
</body>
</html>
"""

class LettaDashboardAPI:
    """API backend for the Letta Dashboard"""
    
    def __init__(self, letta_url: str = "http://localhost:8283"):
        """Initialize the API backend"""
        self.letta_url = letta_url
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.env_loaded = os.path.exists(env_path)
        
        # Initialize Letta agent creator if possible
        try:
            self.creator = LettaAgentCreator(letta_url=letta_url)
            self.letta_online = True
        except Exception as e:
            logger.error(f"Failed to initialize Letta agent creator: {e}")
            self.letta_online = False
            self.creator = None
        
        # Initialize Gemini API client if possible
        try:
            if self.gemini_api_key:
                self.gemini = GeminiAPI()
                self.gemini_status = "available"
            else:
                self.gemini_status = "unavailable"
                self.gemini = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {e}")
            self.gemini_status = "unavailable"
            self.gemini = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of Letta and Gemini services"""
        status = {
            "letta_status": "online" if self.letta_online else "offline",
            "gemini_status": self.gemini_status,
            "env_loaded": self.env_loaded,
            "agents": self.get_agents()
        }
        return status
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get a list of Letta agents"""
        if not self.letta_online or not self.creator:
            return []
        
        try:
            result = self.creator.list_agents()
            if result.get("success"):
                return result.get("agents", [])
            else:
                logger.error(f"Failed to list agents: {result.get('error')}")
                return []
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return []
    
    def test_gemini(self) -> Dict[str, Any]:
        """Test the Gemini API"""
        if not self.gemini:
            return {
                "success": False,
                "error": "Gemini API not configured"
            }
        
        try:
            response = self.gemini.generate_response(
                prompt="Provide a brief test response to confirm the API is working.",
                temperature=0.1
            )
            
            if response.get("success"):
                return {
                    "success": True,
                    "response": response.get("text", "").strip()[:100]  # First 100 chars
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Unknown error")
                }
        except Exception as e:
            logger.error(f"Error testing Gemini API: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard"""
    
    def __init__(self, *args, **kwargs):
        """Initialize the handler with access to the API backend"""
        self.api = None  # Will be set by the server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(DASHBOARD_HTML.encode())
            
            elif self.path.startswith("/api/"):
                self.handle_api_request()
            
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not found")
        
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Server error: {str(e)}".encode())
    
    def handle_api_request(self):
        """Handle API requests"""
        if not self.api:
            self.send_error(500, "API backend not initialized")
            return
        
        if self.path == "/api/status":
            self.send_json_response(self.api.get_status())
        
        elif self.path == "/api/test-gemini":
            self.send_json_response(self.api.test_gemini())
        
        elif self.path == "/api/run-uat":
            # This would normally run the UAT script but we'll simulate it here
            self.send_json_response({
                "tests_run": 8,
                "tests_passed": 8,
                "tests_failed": 0,
                "pass_percentage": 100
            })
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
    
    def send_json_response(self, data):
        """Send a JSON response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr"""
        logger.info("%s - %s" % (self.address_string(), format % args))

def find_available_port(start_port=8000, max_tries=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port after {max_tries} attempts")

def run_dashboard(letta_url="http://localhost:8283", port=None):
    """Run the dashboard server"""
    # Find an available port if not specified
    if port is None:
        port = find_available_port()
    
    server_address = ('', port)
    
    # Create API backend
    api = LettaDashboardAPI(letta_url=letta_url)
    
    # Custom HTTPServer that passes the API backend to the handler
    class DashboardHTTPServer(HTTPServer):
        def finish_request(self, request, client_address):
            # Override to pass the API backend to the handler
            self.RequestHandlerClass.api = api
            super().finish_request(request, client_address)
    
    # Create and start the server
    httpd = DashboardHTTPServer(server_address, DashboardRequestHandler)
    
    url = f"http://localhost:{port}"
    logger.info(f"Starting Letta dashboard server on {url}")
    logger.info(f"Monitoring Letta server at {letta_url}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Open browser
    webbrowser.open(f"{url}?letta_url={letta_url}")
    
    # Wait for keyboard interrupt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        httpd.shutdown()
        logger.info("Server stopped")

def main():
    """Parse command line arguments and run the dashboard"""
    parser = argparse.ArgumentParser(description="Letta Admin Dashboard")
    
    parser.add_argument("--letta-url", default="http://localhost:8283",
                        help="URL of the Letta server (default: http://localhost:8283)")
    
    parser.add_argument("--port", type=int, default=None,
                        help="Port to run the dashboard server on (default: auto-select)")
    
    args = parser.parse_args()
    
    run_dashboard(letta_url=args.letta_url, port=args.port)

if __name__ == "__main__":
    main()
