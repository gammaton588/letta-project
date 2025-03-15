#!/usr/bin/env python3
import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LettaMemoryManager:
    """
    Manages memory storage and retrieval for Letta server
    """
    def __init__(self, memory_dir: str = None):
        """
        Initialize memory storage
        
        :param memory_dir: Custom memory storage directory
        """
        self.memory_dir = memory_dir or os.path.expanduser('~/.letta/memories')
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def store_memory(self, 
                     content: Dict[str, Any], 
                     topic: Optional[str] = None,
                     tags: Optional[List[str]] = None) -> str:
        """
        Store a memory entry
        
        :param content: Memory content
        :param topic: Optional topic for the memory
        :param tags: Optional tags for the memory
        :return: Unique memory ID
        """
        try:
            # Generate unique memory ID
            memory_id = str(uuid.uuid4())
            
            # Prepare memory entry
            memory_entry = {
                'id': memory_id,
                'entry_type': 'user_memory',
                'topic': topic or 'Untitled Memory',
                'timestamp': datetime.now().isoformat(),
                'content': content,
                'tags': tags or []
            }
            
            # Generate filename
            safe_topic = ''.join(c if c.isalnum() or c in [' ', '_'] else '_' for c in memory_entry['topic']).lower()
            filename = f"{safe_topic}_{memory_id}.json"
            filepath = os.path.join(self.memory_dir, filename)
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(memory_entry, f, indent=4)
            
            logger.info(f"Memory stored: {memory_id}")
            return memory_id
        
        except Exception as e:
            logger.error(f"Memory storage error: {e}")
            raise
    
    def retrieve_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific memory by ID
        
        :param memory_id: Unique memory identifier
        :return: Memory content
        """
        try:
            # Search for file with matching memory ID
            for filename in os.listdir(self.memory_dir):
                if memory_id in filename:
                    filepath = os.path.join(self.memory_dir, filename)
                    with open(filepath, 'r') as f:
                        return json.load(f)
            
            raise FileNotFoundError(f"Memory {memory_id} not found")
        
        except Exception as e:
            logger.error(f"Memory retrieval error: {e}")
            raise
    
    def list_memories(self, 
                      tag: Optional[str] = None, 
                      topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List memories with optional filtering
        
        :param tag: Optional tag to filter memories
        :param topic: Optional topic to filter memories
        :return: List of memory metadata
        """
        memories = []
        try:
            for filename in os.listdir(self.memory_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.memory_dir, filename)
                    with open(filepath, 'r') as f:
                        memory = json.load(f)
                    
                    # Apply filters
                    if (not tag or tag in memory.get('tags', [])) and \
                       (not topic or topic.lower() in memory.get('topic', '').lower()):
                        memories.append(memory)
            
            # Sort memories by timestamp, most recent first
            memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return memories
        
        except Exception as e:
            logger.error(f"Memory listing error: {e}")
            raise

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize memory manager
memory_manager = LettaMemoryManager()

@app.route('/api/memories', methods=['POST'])
def create_memory():
    """
    API endpoint to create a new memory
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'content' not in data:
            return jsonify({"error": "Invalid memory content"}), 400
        
        # Store memory
        memory_id = memory_manager.store_memory(
            content=data['content'],
            topic=data.get('topic'),
            tags=data.get('tags')
        )
        
        return jsonify({
            "message": "Memory created successfully",
            "memory_id": memory_id
        }), 201
    
    except Exception as e:
        logger.error(f"Memory creation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memories', methods=['GET'])
def list_memories():
    """
    API endpoint to list memories
    """
    try:
        tag = request.args.get('tag')
        topic = request.args.get('topic')
        
        memories = memory_manager.list_memories(tag=tag, topic=topic)
        
        return jsonify(memories), 200
    
    except Exception as e:
        logger.error(f"Memory listing error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memories/<memory_id>', methods=['GET'])
def get_memory(memory_id):
    """
    API endpoint to retrieve a specific memory
    """
    try:
        memory = memory_manager.retrieve_memory(memory_id)
        return jsonify(memory), 200
    
    except FileNotFoundError:
        return jsonify({"error": "Memory not found"}), 404
    
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "memory_count": len(os.listdir(memory_manager.memory_dir))
    }), 200

def main():
    """
    Run the Letta server
    """
    # Load environment variables
    load_dotenv(os.path.expanduser('~/.letta/env'))
    
    # Get server configuration
    host = os.getenv('LETTA_HOST', '0.0.0.0')
    port = int(os.getenv('LETTA_PORT', 8283))
    
    logger.info(f"Starting Letta server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()
