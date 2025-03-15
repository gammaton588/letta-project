#!/usr/bin/env python3
"""
Letta Server Manager
This script provides command-line tools for managing Letta server and Gemini agents.
"""

import os
import sys
import json
import argparse
import logging
import subprocess
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import uuid
import jwt
import google.generativeai as genai
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/Library/Logs/letta-server.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ConversationDatabase:
    def __init__(self, db_path: str = None):
        """
        Initialize SQLite database for storing conversations.
        
        Args:
            db_path: Path to SQLite database file. 
                     Defaults to ~/Library/Application Support/Letta/conversations.db
        """
        if not db_path:
            db_path = os.path.expanduser('~/Library/Application Support/Letta/conversations.db')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._create_tables()
        
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    conversation_data TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            conn.commit()
    
    def save_conversation(self, 
                          agent_id: str, 
                          platform: str, 
                          conversation_data: Dict, 
                          metadata: Optional[Dict] = None) -> str:
        """
        Save a conversation to the database.
        
        Args:
            agent_id: Unique identifier for the agent
            platform: Source platform (e.g., 'taskade', 'gemini')
            conversation_data: Conversation content
            metadata: Additional metadata about the conversation
        
        Returns:
            Unique conversation ID
        """
        conversation_id = str(uuid.uuid4())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations 
                    (id, agent_id, platform, conversation_data, metadata) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    conversation_id, 
                    agent_id, 
                    platform, 
                    json.dumps(conversation_data), 
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
            
            logger.info(f"Saved conversation {conversation_id} for agent {agent_id}")
            return conversation_id
        
        except sqlite3.Error as e:
            logger.error(f"Error saving conversation: {e}")
            raise
    
    def get_conversations(self, 
                          agent_id: Optional[str] = None, 
                          platform: Optional[str] = None, 
                          limit: int = 100) -> List[Dict]:
        """
        Retrieve conversations with optional filtering.
        
        Args:
            agent_id: Filter by specific agent
            platform: Filter by platform
            limit: Maximum number of conversations to return
        
        Returns:
            List of conversation records
        """
        query = "SELECT * FROM conversations"
        conditions = []
        params = []
        
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        
        if platform:
            conditions.append("platform = ?")
            params.append(platform)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [{
                    'id': row['id'],
                    'agent_id': row['agent_id'],
                    'platform': row['platform'],
                    'timestamp': row['timestamp'],
                    'conversation_data': json.loads(row['conversation_data']),
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                } for row in rows]
        
        except sqlite3.Error as e:
            logger.error(f"Error retrieving conversations: {e}")
            raise

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from multiple possible locations
env_locations = [
    ".env",  # Local environment file
    "configs/.env",  # Docker environment file
    os.path.expanduser("~/.letta/env")  # Global environment file
]

for env_path in env_locations:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")

# Default configurations
DEFAULT_LETTA_URL = "http://localhost:8284"  # Updated to match our Docker port

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class LettaServerManager:
    """Main class for managing Letta server and Gemini agents"""
    
    def __init__(self, letta_url: str = DEFAULT_LETTA_URL):
        """Initialize the manager with Letta server URL"""
        self.letta_url = letta_url
        self.api_url = f"{letta_url}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        self.conversation_db = ConversationDatabase()
    
    def check_server_status(self) -> bool:
        """Check if Letta server is running"""
        try:
            import requests
            response = requests.get(self.letta_url)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents in Letta"""
        try:
            import requests
            response = requests.get(f"{self.api_url}/agents", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list agents: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return []
    
    def create_agent(self, name: str, description: str, system_prompt: str, model_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new agent in Letta"""
        try:
            import requests
            agent_data = {
                "name": name,
                "description": description,
                "system_prompt": system_prompt,
                "model_config": model_config
            }
            response = requests.post(f"{self.api_url}/agents", headers=self.headers, json=agent_data)
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Failed to create agent: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return None
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from Letta"""
        try:
            import requests
            response = requests.delete(f"{self.api_url}/agents/{agent_id}", headers=self.headers)
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error deleting agent: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent from Letta"""
        try:
            import requests
            response = requests.get(f"{self.api_url}/agents/{agent_id}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get agent: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting agent: {e}")
            return None
    
    def save_conversation(self, 
                          agent_id: str, 
                          platform: str, 
                          conversation_data: Dict, 
                          metadata: Optional[Dict] = None) -> str:
        """
        Save a conversation to the database.
        
        Args:
            agent_id: Unique identifier for the agent
            platform: Source platform (e.g., 'taskade', 'gemini')
            conversation_data: Conversation content
            metadata: Additional metadata about the conversation
        
        Returns:
            Unique conversation ID
        """
        return self.conversation_db.save_conversation(agent_id, platform, conversation_data, metadata)
    
    def get_conversations(self, 
                          agent_id: Optional[str] = None, 
                          platform: Optional[str] = None, 
                          limit: int = 100) -> List[Dict]:
        """
        Retrieve conversations with optional filtering.
        
        Args:
            agent_id: Filter by specific agent
            platform: Filter by platform
            limit: Maximum number of conversations to return
        
        Returns:
            List of conversation records
        """
        return self.conversation_db.get_conversations(agent_id, platform, limit)

# Flask routes
@app.route("/")
def index():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Letta server is running"})

@app.route("/api/v1/agents", methods=["GET"])
def list_agents():
    """List all agents"""
    manager = LettaServerManager()
    return jsonify(manager.list_agents())

@app.route("/api/v1/agents", methods=["POST"])
def create_agent():
    """Create a new agent"""
    data = request.json
    manager = LettaServerManager()
    result = manager.create_agent(
        name=data["name"],
        description=data["description"],
        system_prompt=data["system_prompt"],
        model_config=data["model_config"]
    )
    if result:
        return jsonify(result), 201
    return jsonify({"error": "Failed to create agent"}), 400

@app.route("/api/v1/agents/<agent_id>", methods=["GET"])
def get_agent(agent_id):
    """Get an agent by ID"""
    manager = LettaServerManager()
    result = manager.get_agent(agent_id)
    if result:
        return jsonify(result)
    return jsonify({"error": "Agent not found"}), 404

@app.route("/api/v1/agents/<agent_id>", methods=["DELETE"])
def delete_agent(agent_id):
    """Delete an agent by ID"""
    manager = LettaServerManager()
    if manager.delete_agent(agent_id):
        return "", 204
    return jsonify({"error": "Failed to delete agent"}), 400

@app.route("/api/v1/conversations", methods=["POST"])
def save_conversation():
    """Save a conversation"""
    data = request.json
    manager = LettaServerManager()
    conversation_id = manager.save_conversation(
        agent_id=data["agent_id"],
        platform=data["platform"],
        conversation_data=data["conversation_data"],
        metadata=data.get("metadata")
    )
    if conversation_id:
        return jsonify({"conversation_id": conversation_id}), 201
    return jsonify({"error": "Failed to save conversation"}), 400

@app.route("/api/v1/conversations", methods=["GET"])
def get_conversations():
    """Get conversations"""
    manager = LettaServerManager()
    agent_id = request.args.get("agent_id")
    platform = request.args.get("platform")
    limit = int(request.args.get("limit", 100))
    conversations = manager.get_conversations(agent_id, platform, limit)
    return jsonify(conversations)

def main():
    parser = argparse.ArgumentParser(description="Letta Server Manager")
    parser.add_argument("--letta-url", default=DEFAULT_LETTA_URL, help="Letta server URL")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check server status")

    # List agents command
    list_parser = subparsers.add_parser("list", help="List all agents")

    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create a new agent")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--description", required=True, help="Agent description")
    create_parser.add_argument("--system-prompt", required=True, help="Agent system prompt")
    create_parser.add_argument("--model", default="gemini-2.0-flash", help="Model name")
    create_parser.add_argument("--temperature", type=float, default=0.7, help="Model temperature")
    create_parser.add_argument("--max-tokens", type=int, default=4096, help="Model max tokens")

    # Delete agent command
    delete_parser = subparsers.add_parser("delete", help="Delete an agent")
    delete_parser.add_argument("--id", required=True, help="Agent ID")

    # Get agent command
    get_parser = subparsers.add_parser("get", help="Get an agent")
    get_parser.add_argument("--id", required=True, help="Agent ID")

    # Save conversation command
    save_conversation_parser = subparsers.add_parser("save-conversation", help="Save a conversation")
    save_conversation_parser.add_argument("--agent-id", required=True, help="Agent ID")
    save_conversation_parser.add_argument("--platform", required=True, help="Platform")
    save_conversation_parser.add_argument("--conversation-data", required=True, help="Conversation data")

    # Get conversations command
    get_conversations_parser = subparsers.add_parser("get-conversations", help="Get conversations")
    get_conversations_parser.add_argument("--agent-id", help="Agent ID")
    get_conversations_parser.add_argument("--platform", help="Platform")
    get_conversations_parser.add_argument("--limit", type=int, default=100, help="Limit")

    args = parser.parse_args()
    manager = LettaServerManager(letta_url=args.letta_url)

    if args.command == "status":
        if manager.check_server_status():
            print("Letta server is running")
        else:
            print("Letta server is not running")

    elif args.command == "list":
        agents = manager.list_agents()
        if agents:
            print("Agents:")
            for agent in agents:
                print(f"  - {agent['name']} (ID: {agent['id']})")
        else:
            print("No agents found")

    elif args.command == "create":
        model_config = {
            "provider": "gemini",
            "model": args.model,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens
        }
        agent = manager.create_agent(args.name, args.description, args.system_prompt, model_config)
        if agent:
            print(f"Agent created: {agent['name']} (ID: {agent['id']})")
        else:
            print("Failed to create agent")

    elif args.command == "delete":
        if manager.delete_agent(args.id):
            print("Agent deleted")
        else:
            print("Failed to delete agent")

    elif args.command == "get":
        agent = manager.get_agent(args.id)
        if agent:
            print(f"Agent: {agent['name']} (ID: {agent['id']})\n{agent}")
        else:
            print("Agent not found")

    elif args.command == "save-conversation":
        conversation_id = manager.save_conversation(
            agent_id=args.agent_id,
            platform=args.platform,
            conversation_data=json.loads(args.conversation_data)
        )
        if conversation_id:
            print(f"Conversation saved: {conversation_id}")
        else:
            print("Failed to save conversation")

    elif args.command == "get-conversations":
        conversations = manager.get_conversations(
            agent_id=args.agent_id,
            platform=args.platform,
            limit=args.limit
        )
        if conversations:
            print("Conversations:")
            for conversation in conversations:
                print(f"  - {conversation['id']}")
        else:
            print("No conversations found")

if __name__ == "__main__":
    if os.environ.get("FLASK_APP"):
        # Running as a web server
        port = int(os.environ.get("LETTA_PORT", 8283))
        app.run(host="0.0.0.0", port=port)
    else:
        # Running as a CLI tool
        main()
