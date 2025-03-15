#!/usr/bin/env python3
"""
Letta Agent Creator Tool
A tool for creating Gemini-powered agents in the Letta Agent Development Environment.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("letta_agent_creator")

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gemini_integration import create_letta_agent_config, GeminiAPI

class LettaAgentCreator:
    """Tool for creating and managing agents in the Letta ADE"""
    
    def __init__(self, letta_url: str = "http://localhost:8283"):
        """Initialize with Letta server URL"""
        self.letta_url = letta_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        
        # Test connection
        try:
            response = self.session.get(f"{self.letta_url}/")
            if response.status_code == 200:
                logger.info(f"Successfully connected to Letta server at {letta_url}")
            else:
                logger.warning(f"Letta server responded with status code {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Letta server: {e}")
            raise
    
    def login(self, username: str, password: str) -> bool:
        """Login to Letta ADE and get auth token"""
        try:
            response = self.session.post(
                f"{self.letta_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    logger.info(f"Successfully logged in as {username}")
                    return True
                else:
                    logger.error("Login succeeded but no token returned")
                    return False
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def create_gemini_chat_agent(
        self, 
        name: str, 
        description: str, 
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Create a new Gemini-powered chat agent"""
        
        # Generate agent configuration
        agent_config = create_letta_agent_config(
            name=name,
            description=description,
            system_prompt=system_prompt,
            gemini_model="gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Create the agent
        try:
            # Try different API endpoints since the exact path might vary
            endpoints = [
                f"{self.letta_url}/api/agent",
                f"{self.letta_url}/api/agents",
                f"{self.letta_url}/api/v1/agent",
                f"{self.letta_url}/api/v1/agents"
            ]
            
            success = False
            for endpoint in endpoints:
                response = self.session.post(endpoint, json=agent_config)
                if response.status_code in (200, 201):
                    agent_data = response.json()
                    logger.info(f"Successfully created agent: {name}")
                    return {
                        "success": True,
                        "agent": agent_data
                    }
            
            # If we get here, all endpoints failed
            logger.error(f"Failed to create agent. Tried multiple endpoints.")
            return {
                "success": False,
                "error": "Failed to create agent with all attempted API endpoints."
            }
                
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_agents(self) -> Dict[str, Any]:
        """List all agents in the Letta ADE"""
        try:
            # Try multiple possible endpoints
            endpoints = [
                f"{self.letta_url}/api/agents",
                f"{self.letta_url}/api/agent",
                f"{self.letta_url}/api/v1/agents",
                f"{self.letta_url}/api/v1/agent"
            ]
            
            for endpoint in endpoints:
                response = self.session.get(endpoint)
                if response.status_code == 200:
                    agents = response.json()
                    return {
                        "success": True,
                        "agents": agents
                    }
            
            # Gracefully handle case when no endpoints work
            logger.info("No agents found or agents endpoint not available")
            return {
                "success": True,
                "agents": []
            }
                
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Run the agent creator tool from command line"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a Gemini-powered agent in Letta ADE")
    
    parser.add_argument("--letta-url", default="http://localhost:8283",
                        help="URL of the Letta server (default: http://localhost:8283)")
    
    parser.add_argument("--name", required=True,
                        help="Name of the agent to create")
    
    parser.add_argument("--description", default="A Gemini-powered AI assistant",
                        help="Description of the agent")
    
    parser.add_argument("--system-prompt", required=True,
                        help="System prompt for the agent")
    
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature for response generation (0.0-1.0)")
    
    parser.add_argument("--max-tokens", type=int, default=4096,
                        help="Maximum tokens for response generation")
    
    parser.add_argument("--username", help="Letta ADE username (if login required)")
    parser.add_argument("--password", help="Letta ADE password (if login required)")
    
    args = parser.parse_args()
    
    # Create the agent
    creator = LettaAgentCreator(letta_url=args.letta_url)
    
    # Login if credentials provided
    if args.username and args.password:
        if not creator.login(args.username, args.password):
            logger.error("Login failed, cannot create agent")
            return 1
    
    # Create the agent
    result = creator.create_gemini_chat_agent(
        name=args.name,
        description=args.description,
        system_prompt=args.system_prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    if result.get("success"):
        logger.info(f"Successfully created agent: {args.name}")
        logger.info(f"Agent ID: {result.get('agent', {}).get('id')}")
        return 0
    else:
        logger.error(f"Failed to create agent: {result.get('error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
