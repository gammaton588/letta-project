#!/usr/bin/env python3
import os
import json
import sys
from datetime import datetime
from typing import Dict, List

class LettaMemoryInspector:
    def __init__(self, memory_dir: str = None):
        """
        Initialize Letta Memory Inspector
        
        :param memory_dir: Optional custom memory directory path
        """
        # Default memory directory
        self.memory_dir = memory_dir or os.path.expanduser('~/.letta/memories')
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def list_memory_files(self) -> List[str]:
        """
        List all memory files in the memory directory
        
        :return: List of memory file names
        """
        try:
            return [f for f in os.listdir(self.memory_dir) if f.endswith('.json')]
        except Exception as e:
            print(f"❌ Error listing memory files: {e}")
            return []
    
    def read_memory_file(self, filename: str) -> Dict:
        """
        Read and parse a single memory file
        
        :param filename: Name of the memory file to read
        :return: Parsed memory content
        """
        try:
            filepath = os.path.join(self.memory_dir, filename)
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error reading memory file {filename}: {e}")
            return {}
    
    def inspect_memories(self):
        """
        Comprehensively inspect and display all memories
        """
        print("🧠 Letta Memory Inspection 🧠")
        print("==============================")
        
        # List memory files
        memory_files = self.list_memory_files()
        
        if not memory_files:
            print("📭 No memories found in storage.")
            return
        
        print(f"📦 Total Memories: {len(memory_files)}\n")
        
        # Detailed memory inspection
        for idx, filename in enumerate(memory_files, 1):
            print(f"📄 Memory {idx}: {filename}")
            print("-" * 40)
            
            memory_content = self.read_memory_file(filename)
            
            # Extract and display key information
            topic = memory_content.get('topic', 'Unknown Topic')
            timestamp = memory_content.get('timestamp', 'No Timestamp')
            
            print(f"Topic: {topic}")
            print(f"Timestamp: {timestamp}")
            
            # Display content summary
            if 'content' in memory_content:
                content = memory_content['content']
                # Truncate long content
                summary = (content[:300] + '...') if len(content) > 300 else content
                print("Content Summary:")
                print(summary)
            
            print("\n")
    
    def search_memories(self, query: str = None):
        """
        Search memories based on optional query
        
        :param query: Optional search term
        """
        print("🔍 Memory Search")
        print("================")
        
        if query:
            print(f"Search Query: {query}\n")
        
        matching_memories = []
        
        # Iterate through memory files
        for filename in self.list_memory_files():
            memory_content = self.read_memory_file(filename)
            
            # If no query, or query matches topic or content
            if not query or (
                query.lower() in memory_content.get('topic', '').lower() or
                query.lower() in str(memory_content.get('content', '')).lower()
            ):
                matching_memories.append({
                    'filename': filename,
                    'topic': memory_content.get('topic', 'Unknown'),
                    'timestamp': memory_content.get('timestamp', 'No Timestamp')
                })
        
        # Display results
        if matching_memories:
            print(f"🔎 Found {len(matching_memories)} matching memories:\n")
            for memory in matching_memories:
                print(f"📄 {memory['topic']}")
                print(f"   File: {memory['filename']}")
                print(f"   Timestamp: {memory['timestamp']}\n")
        else:
            print("❌ No memories found matching the search query.")

def main():
    inspector = LettaMemoryInspector()
    
    # Check for command-line search query
    if len(sys.argv) > 1:
        inspector.search_memories(' '.join(sys.argv[1:]))
    else:
        inspector.inspect_memories()

if __name__ == '__main__':
    main()
