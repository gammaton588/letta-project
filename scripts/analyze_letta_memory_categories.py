#!/usr/bin/env python3
import os
import json
import sys
from typing import Dict, List, Any

class LettaMemoryCategorizer:
    def __init__(self, memory_dir: str = None):
        """
        Initialize Letta Memory Categorizer
        
        :param memory_dir: Optional custom memory directory path
        """
        self.memory_dir = memory_dir or os.path.expanduser('~/.letta/memories')
        self.memories = self._load_memories()
    
    def _load_memories(self) -> List[Dict[str, Any]]:
        """
        Load all memory files
        
        :return: List of memory contents
        """
        memories = []
        for filename in os.listdir(self.memory_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.memory_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        memories.append(json.load(f))
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        return memories
    
    def analyze_categorization(self):
        """
        Analyze how memories are categorized
        """
        print("🧠 Letta Memory Categorization Analysis 🧠")
        print("=========================================")
        
        # Categorization methods
        categorization_methods = {
            'Entry Types': self._analyze_entry_types(),
            'Topics': self._analyze_topics(),
            'Tags': self._analyze_tags(),
            'Domains': self._analyze_domains()
        }
        
        # Display detailed categorization
        for method, details in categorization_methods.items():
            print(f"\n{method}:")
            print("-" * len(method))
            
            if isinstance(details, dict):
                for key, value in details.items():
                    print(f"{key}: {value}")
            else:
                print(details)
    
    def _analyze_entry_types(self) -> Dict[str, int]:
        """
        Analyze different entry types in memories
        
        :return: Dictionary of entry types and their counts
        """
        entry_types = {}
        for memory in self.memories:
            # Check for different possible entry type keys
            type_keys = ['entry_type', 'entryType', 'type']
            entry_type = next((memory.get(key, 'Unknown') for key in type_keys if key in memory), 'Unknown')
            
            entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
        
        return entry_types
    
    def _analyze_topics(self) -> Dict[str, int]:
        """
        Analyze topics of memories
        
        :return: Dictionary of topics and their counts
        """
        topics = {}
        for memory in self.memories:
            # Check for different possible topic keys
            topic_keys = ['topic', 'title', 'subject']
            topic = next((memory.get(key, 'Unknown') for key in topic_keys if key in memory), 'Unknown')
            
            topics[topic] = topics.get(topic, 0) + 1
        
        return topics
    
    def _analyze_tags(self) -> str:
        """
        Analyze tags associated with memories
        
        :return: String description of tags
        """
        all_tags = []
        for memory in self.memories:
            # Check for different possible tag keys
            tag_keys = ['tags', 'categories', 'labels']
            tags = next((memory.get(key, []) for key in tag_keys if key in memory), [])
            
            all_tags.extend(tags)
        
        # Count and sort tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort tags by frequency
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return "\n".join([f"{tag}: {count}" for tag, count in sorted_tags]) if sorted_tags else "No tags found"
    
    def _analyze_domains(self) -> Dict[str, int]:
        """
        Analyze domains of memories
        
        :return: Dictionary of domains and their counts
        """
        domains = {}
        for memory in self.memories:
            # Check for different possible domain keys
            domain_keys = ['domain', 'category', 'field']
            domain = next((memory.get(key, 'Unknown') for key in domain_keys if key in memory), 'Unknown')
            
            domains[domain] = domains.get(domain, 0) + 1
        
        return domains
    
    def generate_memory_report(self):
        """
        Generate a comprehensive memory categorization report
        """
        print("📊 Letta Memory Categorization Report 📊")
        print("======================================")
        
        # Total memories
        print(f"Total Memories: {len(self.memories)}")
        
        # Detailed analysis
        self.analyze_categorization()

def main():
    categorizer = LettaMemoryCategorizer()
    categorizer.generate_memory_report()

if __name__ == '__main__':
    main()
