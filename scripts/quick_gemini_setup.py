#!/usr/bin/env python3
"""
Quick Gemini Agent Setup Script
A helper script to quickly set up and verify your Gemini agent in Letta.
This script provides a guided experience following the steps in gemini_agent_quick_guide.md.
"""

import os
import sys
import time
import json
import tempfile
import webbrowser
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gemini_integration import GeminiAPI, create_letta_agent_config

# Load environment variables
env_path = os.path.expanduser("~/.letta/env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Default configurations
DEFAULT_LETTA_URL = "http://localhost:8283"
DEFAULT_AGENT_NAME = "GeminiAssistant"
DEFAULT_AGENT_DESCRIPTION = "A helpful AI assistant powered by Google Gemini"
DEFAULT_SYSTEM_PROMPT = """You are GeminiAssistant, a helpful AI assistant powered by Google Gemini.
Your goal is to provide helpful, accurate, and concise responses.
Be conversational but professional in your tone.
Always provide the most relevant information to the user's query."""

def check_prerequisites():
    """Check if prerequisites are met"""
    print("\n=== Checking Prerequisites ===")
    
    # Check Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ Gemini API key not found in environment variables.")
        print("Please add GEMINI_API_KEY to your ~/.letta/env file.")
        return False
    else:
        print("✅ Gemini API key found.")
    
    # Test Gemini API
    try:
        api = GeminiAPI()
        result = api.generate_response("Hello, this is a test.")
        if result.get("success"):
            print(f"✅ Gemini API is working correctly with model: {api.model}")
        else:
            print(f"❌ Gemini API test failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Failed to initialize Gemini API: {e}")
        return False
    
    # Check Letta server
    import requests
    try:
        response = requests.get(DEFAULT_LETTA_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Letta server is running at: {DEFAULT_LETTA_URL}")
        else:
            print(f"❌ Letta server returned status code: {response.status_code}")
            return False
    except requests.RequestException:
        print(f"❌ Letta server not reachable at: {DEFAULT_LETTA_URL}")
        print("Make sure your Docker container is running.")
        return False
    
    return True

def create_agent_config_file(
    name=DEFAULT_AGENT_NAME,
    description=DEFAULT_AGENT_DESCRIPTION,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
    temperature=0.7,
    max_tokens=4096
):
    """Create and save an agent configuration file"""
    
    # Generate configuration
    config = create_letta_agent_config(
        name=name,
        description=description,
        system_prompt=system_prompt,
        gemini_model="gemini-2.0-flash",
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Save to file
    fd, config_path = tempfile.mkstemp(suffix=".json", prefix=f"letta_agent_{name}_")
    os.close(fd)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path

def guide_user_through_web_workflow(config_path):
    """Guide the user through the web interface workflow"""
    print("\n=== Guided Web Interface Workflow ===")
    
    # Open Letta ADE in browser
    print(f"1. Opening Letta ADE in your browser: {DEFAULT_LETTA_URL}")
    webbrowser.open(DEFAULT_LETTA_URL)
    time.sleep(1)
    
    print("\n2. Follow these steps in the web interface:")
    print("""
   a. Sign in to your Letta ADE account
      → If this is your first time, you'll be prompted to create an admin account
      → Use simple credentials you can remember (e.g., admin/admin@example.com/LettaAdmin123!)

   b. Navigate to Agent Creation
      → From the dashboard, click "Create New Agent" or similar
      → If you don't see this option, look for "Agents" in the sidebar and then "New Agent"

   c. Configure Basic Agent Settings
      → Name: GeminiAssistant
      → Description: A helpful AI assistant powered by Google Gemini
      → Agent Type: Conversational (or similar option)

   d. Configure Model Settings
      → Provider/Model: Select Google Gemini (or similar option)
      → Model Version: gemini-2.0-flash
      → API Key: Your key should be automatically available from the environment variables
      → Temperature: 0.7 (balanced creativity/consistency)
      → Max Tokens: 4096 (or maximum allowed)
    """)
    
    # Extract and display system prompt from config
    with open(config_path, 'r') as f:
        config = json.load(f)
        system_prompt = config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    
    print("3. Use this system prompt:")
    print("---------------")
    print(system_prompt)
    print("---------------")
    
    # Save system prompt to a separate file for easy copying
    prompt_path = os.path.join(os.path.dirname(config_path), "system_prompt.txt")
    with open(prompt_path, 'w') as f:
        f.write(system_prompt)
    
    print(f"\nSystem prompt saved to: {prompt_path}")
    print("Copy and paste this into the 'System Prompt' field in the web interface.")
    
    # Suggest test message
    print("\n4. After creating your agent, test it with this message:")
    print('   "Hello, can you tell me what you can help me with?"')
    print("\n5. Finally, save and deploy your agent.")
    
    # Open documentation for reference
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    guide_path = os.path.join(docs_dir, "gemini_agent_quick_guide.md")
    
    if os.path.exists(guide_path):
        print("\nOpening the Gemini Agent Quick Guide for additional help...")
        try:
            # Use 'open' command on macOS
            subprocess.run(['open', guide_path])
        except Exception:
            print(f"Quick guide available at: {guide_path}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Quick Gemini Agent Setup")
    parser.add_argument("--name", default=DEFAULT_AGENT_NAME, help="Agent name")
    parser.add_argument("--description", default=DEFAULT_AGENT_DESCRIPTION, help="Agent description")
    parser.add_argument("--temperature", type=float, default=0.7, help="Agent temperature (0.0-1.0)")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Max tokens for responses")
    parser.add_argument("--custom-prompt", action="store_true", help="Use a custom system prompt")
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Please resolve the issues above before continuing.")
        return 1
    
    # Optionally get custom system prompt
    if args.custom_prompt:
        print("\n=== Custom System Prompt ===")
        print("Enter your system prompt instructions (Ctrl+D when finished):")
        prompt_lines = []
        try:
            while True:
                line = input()
                prompt_lines.append(line)
        except EOFError:
            pass
        system_prompt = "\n".join(prompt_lines)
    else:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    # Create agent configuration file
    config_path = create_agent_config_file(
        name=args.name,
        description=args.description,
        system_prompt=system_prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    print(f"\n✅ Agent configuration saved to: {config_path}")
    
    # Guide through web workflow
    guide_user_through_web_workflow(config_path)
    
    print("\n🎉 You're all set! Follow the steps in your browser to complete the process.")
    print("Once your agent is created, you can interact with it in the Letta ADE.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
