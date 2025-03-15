#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from dotenv import load_dotenv

class GeminiIntegrationSetup:
    def __init__(self):
        # Load environment variables
        load_dotenv(os.path.expanduser('~/.letta/env'))
        
        # Gemini API configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.letta_server_url = os.getenv('LETTA_SERVER_URL', 'http://localhost:8283')
        
    def verify_dependencies(self):
        """Verify required dependencies are installed."""
        dependencies = [
            'google-generativeai',
            'python-dotenv',
            'requests'
        ]
        
        for dep in dependencies:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', dep])
            except subprocess.CalledProcessError:
                print(f"Failed to install {dep}")
                return False
        return True
    
    def configure_gemini_api(self):
        """Configure Gemini API settings."""
        if not self.gemini_api_key:
            print("Error: GEMINI_API_KEY not found in environment")
            return False
        
        config = {
            'api_key': self.gemini_api_key,
            'default_model': 'gemini-2.0-flash',
            'models': {
                'chat': 'gemini-2.0-pro',
                'multimodal': 'gemini-1.5-pro'
            }
        }
        
        # Ensure Letta configuration directory exists
        os.makedirs(os.path.expanduser('~/.letta'), exist_ok=True)
        
        with open(os.path.expanduser('~/.letta/gemini_config.json'), 'w') as f:
            json.dump(config, f, indent=4)
        
        return True
    
    def create_sample_agent(self):
        """Create a sample Gemini-powered agent configuration."""
        sample_agent = {
            'name': 'GeminiAssistant',
            'description': 'A versatile AI assistant powered by Google Gemini',
            'type': 'chat',
            'system_prompt': """You are GeminiAssistant, a helpful and knowledgeable AI.
Your goal is to provide accurate, helpful, and engaging responses.
Be conversational, friendly, and professional.
If you don't know something, admit it rather than making up information.""",
            'model_config': {
                'model': 'gemini-2.0-flash',
                'temperature': 0.7,
                'max_tokens': 1024
            }
        }
        
        with open(os.path.expanduser('~/.letta/sample_agent.json'), 'w') as f:
            json.dump(sample_agent, f, indent=4)
        
        return True
    
    def run_setup(self):
        """Execute the full setup process."""
        print("Starting Gemini Integration Setup...")
        
        # Verify and install dependencies
        if not self.verify_dependencies():
            print("Dependency installation failed.")
            return False
        
        # Configure Gemini API
        if not self.configure_gemini_api():
            print("Gemini API configuration failed.")
            return False
        
        # Create sample agent
        if not self.create_sample_agent():
            print("Sample agent creation failed.")
            return False
        
        print("Gemini Integration Setup completed successfully!")
        return True

def main():
    setup = GeminiIntegrationSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
