#!/usr/bin/env python3
"""
Create Gemini Agent via Letta API
This script creates a Gemini agent directly using the Letta API endpoints.
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gemini_integration import GeminiAPI, create_letta_agent_config

# Load environment variables
env_path = os.path.expanduser("~/.letta/env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Default configurations
DEFAULT_LETTA_URL = "http://localhost:8283"
DEFAULT_CONFIG_PATH = "/var/folders/dx/mg3zn87d7v180d9knyk2mx8r0000gn/T/letta_agent_GeminiAssistant_qgzm0_cs.json"

class LettaAPIClient:
    """Client for interacting with Letta API"""
    
    def __init__(self, base_url=DEFAULT_LETTA_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_agent(self, config):
        """Create a new agent using various API endpoint patterns"""
        
        # Try different API endpoint patterns
        endpoints = [
            "/api/agents",
            "/api/v1/agents",
            "/agents",
            "/api/agent",
            "/api/v1/agent"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"Trying endpoint: {url}")
                
                response = self.session.post(
                    url,
                    json=config,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code in (200, 201):
                    return {"success": True, "data": response.json(), "endpoint": endpoint}
                else:
                    print(f"  Status: {response.status_code}")
                    try:
                        print(f"  Response: {response.json()}")
                    except:
                        print(f"  Response: {response.text[:100]}")
            except Exception as e:
                print(f"  Error: {str(e)}")
        
        return {"success": False, "error": "Failed to create agent with all attempted API endpoints."}
    
    def list_agents(self):
        """List all agents"""
        
        # Try different API endpoint patterns
        endpoints = [
            "/api/agents",
            "/api/v1/agents",
            "/agents",
            "/api/agent",
            "/api/v1/agent"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"Trying endpoint: {url}")
                
                response = self.session.get(
                    url,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json(), "endpoint": endpoint}
                else:
                    print(f"  Status: {response.status_code}")
                    try:
                        print(f"  Response: {response.json()}")
                    except:
                        print(f"  Response: {response.text[:100]}")
            except Exception as e:
                print(f"  Error: {str(e)}")
        
        return {"success": False, "error": "Failed to list agents with all attempted API endpoints."}

def main():
    parser = argparse.ArgumentParser(description="Create Gemini Agent via Letta API")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to agent configuration file")
    parser.add_argument("--letta-url", default=DEFAULT_LETTA_URL, help="Letta server URL")
    parser.add_argument("--list", action="store_true", help="List existing agents")
    
    args = parser.parse_args()
    
    # Initialize Letta API client
    client = LettaAPIClient(base_url=args.letta_url)
    
    # List agents if requested
    if args.list:
        print("\n=== Listing Agents ===")
        result = client.list_agents()
        
        if result["success"]:
            print(f"\n✅ Successfully retrieved agents using endpoint: {result['endpoint']}")
            agents = result["data"]
            print(f"Found {len(agents)} agents:")
            for i, agent in enumerate(agents):
                print(f"{i+1}. {agent.get('name', 'Unknown')} - {agent.get('id', 'No ID')}")
        else:
            print(f"\n❌ Failed to list agents: {result.get('error')}")
        
        return 0
    
    # Create agent
    print("\n=== Creating Gemini Agent ===")
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
            print(f"Loaded configuration for agent: {config.get('name')}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return 1
    
    # Create agent
    result = client.create_agent(config)
    
    if result["success"]:
        print(f"\n✅ Successfully created agent using endpoint: {result['endpoint']}")
        agent_data = result["data"]
        print(f"Agent ID: {agent_data.get('id')}")
        print(f"Agent Name: {agent_data.get('name')}")
        print("\n🎉 Your Gemini agent has been created successfully!")
        print(f"You can access it at: {args.letta_url}")
    else:
        print(f"\n❌ Failed to create agent: {result.get('error')}")
        print("\nTrying alternative approach with Docker command...")
        
        # Try alternative approach using Docker exec
        try:
            import subprocess
            
            # Convert config to escaped JSON string
            config_str = json.dumps(config).replace('"', '\\"')
            
            # Create Docker command
            docker_cmd = f'docker exec letta-server bash -c "echo \'{config_str}\' > /tmp/agent_config.json && cd /app && python -c \"from letta.server.api.agents import create_agent; import json; with open(\'/tmp/agent_config.json\') as f: config = json.load(f); print(create_agent(config))\""'
            
            print(f"Running Docker command...")
            result = subprocess.run(docker_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("\n✅ Successfully created agent using Docker exec approach!")
                print(f"Output: {result.stdout}")
                print("\n🎉 Your Gemini agent has been created successfully!")
                print(f"You can access it at: {args.letta_url}")
            else:
                print(f"\n❌ Failed to create agent using Docker exec: {result.stderr}")
        except Exception as e:
            print(f"\n❌ Failed to create agent using alternative approach: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
