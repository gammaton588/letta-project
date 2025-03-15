#!/usr/bin/env python3
import os
import sys
import json
import re

class LettaEnvironmentConfigurator:
    def __init__(self):
        self.env_path = os.path.expanduser('~/.letta/env')
        self.current_env = self._load_current_env()
    
    def _load_current_env(self):
        """Load existing environment variables"""
        env_vars = {}
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        return env_vars
    
    def _validate_gemini_api_key(self, key):
        """Validate Google Gemini API key format"""
        # Basic validation for API key format
        pattern = r'^[A-Za-z0-9_-]{39,}$'
        return re.match(pattern, key) is not None
    
    def _validate_server_url(self, url):
        """Validate server URL format"""
        pattern = r'^https?://[a-zA-Z0-9.-]+(?::\d+)?$'
        return re.match(pattern, url) is not None
    
    def recommend_gemini_api_key(self):
        """Recommend ways to obtain a Gemini API key"""
        print("\n🔑 Gemini API Key Configuration Options:")
        print("1. Use existing API key from environment")
        print("2. Enter a new API key manually")
        print("3. Generate a new API key from Google AI Studio")
        print("4. Skip API key configuration")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                # Check existing key
                existing_key = self.current_env.get('GEMINI_API_KEY')
                if existing_key:
                    if self._validate_gemini_api_key(existing_key):
                        return existing_key
                    else:
                        print("❌ Existing key appears to be invalid.")
                else:
                    print("❌ No existing key found.")
            
            elif choice == '2':
                while True:
                    key = input("Enter your Gemini API key: ").strip()
                    if self._validate_gemini_api_key(key):
                        return key
                    else:
                        print("❌ Invalid API key format. Please try again.")
            
            elif choice == '3':
                print("\n🌐 To generate a new API key:")
                print("1. Visit https://makersuite.google.com/app/apikey")
                print("2. Click 'Create API Key'")
                print("3. Copy the generated key")
                input("Press Enter after copying your new API key...")
                continue
            
            elif choice == '4':
                return None
            
            else:
                print("Invalid choice. Please try again.")
    
    def recommend_server_url(self):
        """Recommend Letta server URL options"""
        print("\n🌐 Letta Server URL Configuration:")
        print("1. Use default localhost URL (http://localhost:8283)")
        print("2. Enter a custom server URL")
        print("3. Use existing URL from environment")
        print("4. Skip server URL configuration")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                return 'http://localhost:8283'
            
            elif choice == '2':
                while True:
                    url = input("Enter Letta server URL: ").strip()
                    if self._validate_server_url(url):
                        return url
                    else:
                        print("❌ Invalid URL format. Please try again.")
            
            elif choice == '3':
                existing_url = self.current_env.get('LETTA_SERVER_URL')
                if existing_url and self._validate_server_url(existing_url):
                    return existing_url
                else:
                    print("❌ No valid existing URL found.")
            
            elif choice == '4':
                return None
            
            else:
                print("Invalid choice. Please try again.")
    
    def save_environment(self, gemini_key=None, server_url=None):
        """Save environment variables to configuration file"""
        # Ensure .letta directory exists
        os.makedirs(os.path.dirname(self.env_path), exist_ok=True)
        
        # Merge with existing environment
        if gemini_key:
            self.current_env['GEMINI_API_KEY'] = gemini_key
        if server_url:
            self.current_env['LETTA_SERVER_URL'] = server_url
        
        # Add a timestamp
        self.current_env['LETTA_TIMESTAMP'] = '2025-03-14T21:27:48-06:00'
        
        # Write to file
        with open(self.env_path, 'w') as f:
            for key, value in self.current_env.items():
                f.write(f"{key}={value}\n")
        
        print("\n✅ Environment configuration saved successfully!")
        print(f"Configuration file: {self.env_path}")
        
        # Display saved configuration
        print("\n🔍 Saved Configuration:")
        for key, value in self.current_env.items():
            print(f"{key}: {value}")
    
    def run_configuration(self):
        """Run full environment configuration process"""
        print("🛠️ Letta Environment Configurator 🛠️")
        print("====================================")
        
        # Configure Gemini API Key
        gemini_key = self.recommend_gemini_api_key()
        
        # Configure Server URL
        server_url = self.recommend_server_url()
        
        # Save configuration
        self.save_environment(gemini_key, server_url)

def main():
    configurator = LettaEnvironmentConfigurator()
    configurator.run_configuration()

if __name__ == '__main__':
    main()
