#!/usr/bin/env python3
import os
import sys
import json
import logging
from typing import Dict, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

class VersatileGeminiAgent:
    """
    A versatile Gemini-powered agent for the Letta environment.
    Supports multiple interaction modes and advanced AI capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Gemini agent with configuration.
        
        :param config_path: Optional path to agent configuration JSON
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv(os.path.expanduser('~/.letta/env'))
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.error("Gemini API key not found in environment")
            raise ValueError("GEMINI_API_KEY must be set")
        
        genai.configure(api_key=api_key)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            self.config.get('model', 'gemini-2.0-flash'),
            generation_config=genai.types.GenerationConfig(
                temperature=self.config.get('temperature', 0.7),
                max_output_tokens=self.config.get('max_tokens', 1024)
            )
        )
        
        # Chat session (optional)
        self.chat_session = None
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load agent configuration from JSON file.
        
        :param config_path: Path to configuration file
        :return: Configuration dictionary
        """
        default_config = {
            'name': 'VersatileGeminiAgent',
            'description': 'Multipurpose AI agent powered by Google Gemini',
            'model': 'gemini-2.0-flash',
            'temperature': 0.7,
            'max_tokens': 1024,
            'system_prompt': """You are a versatile AI assistant designed to help users 
            with a wide range of tasks. Be helpful, precise, and adaptable. 
            Provide clear, concise, and accurate information."""
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except (IOError, json.JSONDecodeError) as e:
                self.logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def start_chat_session(self, system_prompt: Optional[str] = None):
        """
        Start a new chat session with optional system prompt.
        
        :param system_prompt: Custom system prompt for the chat
        """
        prompt = system_prompt or self.config.get('system_prompt')
        self.chat_session = self.model.start_chat(history=[])
        
        # Initial system message
        if prompt:
            self.chat_session.send_message(prompt)
    
    def generate_response(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a response using Gemini API.
        
        :param prompt: User's input prompt
        :param context: Optional context dictionary
        :return: Response dictionary
        """
        try:
            # Use chat session if available, otherwise use direct generation
            if self.chat_session:
                response = self.chat_session.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'text': response.text,
                'raw_response': response
            }
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyze an image using Gemini's multimodal capabilities.
        
        :param image_path: Path to the image file
        :param prompt: Description or question about the image
        :return: Analysis result dictionary
        """
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            response = self.model.generate_content([prompt, image])
            
            return {
                'success': True,
                'text': response.text,
                'raw_response': response
            }
        except ImportError:
            self.logger.error("Pillow library required for image analysis")
            return {
                'success': False,
                'error': "Pillow library not installed"
            }
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_config(self, output_path: str):
        """
        Export current agent configuration to a JSON file.
        
        :param output_path: Path to save the configuration
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Configuration exported to {output_path}")
        except Exception as e:
            self.logger.error(f"Configuration export failed: {e}")

def main():
    """
    Demonstration of VersatileGeminiAgent capabilities
    """
    # Create agent with default configuration
    agent = VersatileGeminiAgent()
    
    # Start a chat session
    agent.start_chat_session()
    
    # Generate a response
    response = agent.generate_response(
        "Explain the concept of AI agents in a way a 10-year-old would understand."
    )
    
    if response['success']:
        print("Agent Response:")
        print(response['text'])
    else:
        print("Error:", response.get('error', 'Unknown error'))

if __name__ == '__main__':
    main()
