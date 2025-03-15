#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

class LettaMemoryManager:
    """
    Manages memory storage for Letta chatbot interactions
    """
    def __init__(self, memory_dir: str = None):
        """
        Initialize memory storage
        
        :param memory_dir: Custom memory storage directory
        """
        self.memory_dir = memory_dir or os.path.expanduser('~/.letta/memories')
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def store_memory(self, 
                     topic: str, 
                     content: Dict[str, Any], 
                     tags: List[str] = None) -> bool:
        """
        Store a memory entry in Letta's memory system
        
        :param topic: Topic of the memory
        :param content: Content to be stored
        :param tags: Optional tags for the memory
        :return: Whether memory was successfully stored
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().isoformat()
            safe_topic = ''.join(c if c.isalnum() or c in [' ', '_'] else '_' for c in topic).lower()
            filename = f"{safe_topic}_{timestamp}.json"
            filepath = os.path.join(self.memory_dir, filename)
            
            # Prepare memory entry
            memory_entry = {
                'entry_type': 'chatbot_interaction',
                'topic': topic,
                'timestamp': timestamp,
                'content': content,
                'tags': tags or []
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(memory_entry, f, indent=4)
            
            return True
        except Exception as e:
            logging.error(f"Memory storage error: {e}")
            return False

class GeminiChatbot:
    """
    Chatbot using Google Gemini API with Letta memory integration
    """
    def __init__(self, persona: str = "helpful assistant"):
        """
        Initialize chatbot with specific persona
        
        :param persona: Personality description for the chatbot
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Load environment variables
        load_dotenv(os.path.expanduser('~/.letta/env'))
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logging.error("Gemini API key not found")
            raise ValueError("GEMINI_API_KEY must be set")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash',
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024
            ),
            system_instruction=f"You are a {persona}. Provide helpful, engaging, and informative responses."
        )
        
        # Initialize memory manager
        self.memory_manager = LettaMemoryManager()
        
        # Conversation history
        self.conversation_history: List[tuple] = []
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate a response using Gemini and store the interaction in memory
        
        :param user_input: User's message
        :return: Chatbot's response
        """
        try:
            # Prepare conversation context
            chat_history = [
                {'role': role, 'parts': [msg]} 
                for role, msg in self.conversation_history
            ]
            
            # Generate response
            response = self.model.generate_content(
                contents=[
                    *chat_history,
                    {'role': 'user', 'parts': [user_input]}
                ]
            )
            
            # Extract response text
            response_text = response.text
            
            # Store interaction in memory
            self._store_interaction(user_input, response_text)
            
            # Update conversation history
            self.conversation_history.append(('user', user_input))
            self.conversation_history.append(('assistant', response_text))
            
            return response_text
        
        except Exception as e:
            logging.error(f"Response generation error: {e}")
            return "I'm sorry, but I encountered an error processing your request."
    
    def _store_interaction(self, user_input: str, response: str):
        """
        Store conversation interaction in Letta's memory
        
        :param user_input: User's message
        :param response: Chatbot's response
        """
        try:
            # Determine topic based on user input
            topic_generation = self.model.generate_content(
                f"Summarize the main topic of this conversation in 3-5 words: {user_input}"
            )
            topic = topic_generation.text.strip()
            
            # Prepare memory content
            memory_content = {
                'user_input': user_input,
                'assistant_response': response,
                'interaction_length': len(user_input) + len(response)
            }
            
            # Store in memory with tags
            self.memory_manager.store_memory(
                topic=topic or "General Conversation",
                content=memory_content,
                tags=['chatbot', 'interaction']
            )
        
        except Exception as e:
            logging.error(f"Memory storage error: {e}")
    
    def interactive_chat(self):
        """
        Run an interactive chat session
        """
        print("🤖 Gemini Chatbot (type 'exit' to quit)")
        print("======================================")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye! 👋")
                    break
                
                if user_input:
                    response = self.generate_response(user_input)
                    print(f"Chatbot: {response}\n")
            
            except KeyboardInterrupt:
                print("\nChat ended. Goodbye! 👋")
                break

def main():
    # Create chatbot with a specific persona
    chatbot = GeminiChatbot(persona="knowledgeable science communicator")
    
    # Run interactive chat
    chatbot.interactive_chat()

if __name__ == '__main__':
    main()
