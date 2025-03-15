#!/usr/bin/env python3
"""
Taskade Conversation Integration Script

Retrieves conversations from Taskade and stores them in the Letta server.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from letta_server_manager import LettaServerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/Library/Logs/taskade_integration.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TaskadeIntegration:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Taskade integration.
        
        Args:
            token: Taskade API token. If not provided, will try to read from .env
        """
        # Try to load token from environment or .env file
        if not token:
            token = self._load_taskade_token()
        
        if not token:
            raise ValueError("No Taskade API token found. Please set TASKADE_API_TOKEN.")
        
        self.token = token
        self.base_url = "https://api.taskade.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Initialize Letta server manager
        self.letta_manager = LettaServerManager()
    
    def _load_taskade_token(self) -> Optional[str]:
        """
        Load Taskade API token from environment or .env file.
        
        Returns:
            API token or None if not found
        """
        # Check environment variable first
        token = os.environ.get('TASKADE_API_TOKEN')
        
        if not token:
            # Try to load from .env file
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('TASKADE_API_TOKEN='):
                            token = line.strip().split('=')[1].strip("'").strip('"')
                            break
            except FileNotFoundError:
                logger.warning("No .env file found")
        
        return token
    
    def get_workspace_agents(self) -> List[Dict]:
        """
        Retrieve list of agents in the workspace.
        
        Returns:
            List of agent dictionaries
        """
        try:
            response = requests.get(
                f"{self.base_url}/agents", 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('agents', [])
        except requests.RequestException as e:
            logger.error(f"Error retrieving workspace agents: {e}")
            return []
    
    def get_agent_conversations(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """
        Retrieve conversations for a specific agent.
        
        Args:
            agent_id: Unique identifier for the agent
            limit: Maximum number of conversations to retrieve
        
        Returns:
            List of conversation dictionaries
        """
        try:
            response = requests.get(
                f"{self.base_url}/agents/{agent_id}/conversations",
                headers=self.headers,
                params={'limit': limit}
            )
            response.raise_for_status()
            return response.json().get('conversations', [])
        except requests.RequestException as e:
            logger.error(f"Error retrieving conversations for agent {agent_id}: {e}")
            return []
    
    def sync_agent_conversations(self, agent_id: str):
        """
        Synchronize conversations for a specific agent to Letta server.
        
        Args:
            agent_id: Unique identifier for the agent
        
        Returns:
            Number of conversations synced
        """
        conversations = self.get_agent_conversations(agent_id)
        synced_count = 0
        
        for conversation in conversations:
            try:
                # Save conversation to Letta server
                conversation_id = self.letta_manager.save_conversation(
                    agent_id=agent_id,
                    platform='taskade',
                    conversation_data=conversation,
                    metadata={
                        'source': 'taskade_integration',
                        'sync_timestamp': datetime.now().isoformat()
                    }
                )
                synced_count += 1
                logger.info(f"Synced conversation {conversation_id} for agent {agent_id}")
            except Exception as e:
                logger.error(f"Failed to sync conversation for agent {agent_id}: {e}")
        
        return synced_count
    
    def sync_all_agents(self):
        """
        Synchronize conversations for all agents in the workspace.
        
        Returns:
            Dictionary of sync results per agent
        """
        agents = self.get_workspace_agents()
        sync_results = {}
        
        for agent in agents:
            agent_id = agent.get('id')
            if agent_id:
                sync_count = self.sync_agent_conversations(agent_id)
                sync_results[agent_id] = sync_count
        
        return sync_results

def main():
    """
    Main function to run Taskade integration from command line.
    Supports different modes of operation.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Taskade Conversation Integration")
    parser.add_argument(
        "--mode", 
        choices=['all', 'agent'], 
        default='all', 
        help="Sync mode: 'all' for all agents, 'agent' for specific agent"
    )
    parser.add_argument(
        "--agent-id", 
        help="Agent ID when mode is 'agent'"
    )
    
    args = parser.parse_args()
    
    try:
        integration = TaskadeIntegration()
        
        if args.mode == 'all':
            results = integration.sync_all_agents()
            print("Sync Results:")
            for agent_id, count in results.items():
                print(f"  Agent {agent_id}: {count} conversations synced")
        
        elif args.mode == 'agent' and args.agent_id:
            count = integration.sync_agent_conversations(args.agent_id)
            print(f"Synced {count} conversations for agent {args.agent_id}")
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
