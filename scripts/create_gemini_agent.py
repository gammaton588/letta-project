#!/usr/bin/env python3
"""
Script to create a simple Gemini-powered agent in Letta
"""

import requests
import json
import time
import sys

# Letta server URL
LETTA_URL = "http://localhost:8283"

# Admin credentials (for first-time setup)
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "LettaAdmin123!"
}

# Basic Gemini agent config
GEMINI_AGENT = {
    "name": "GeminiAssistant",
    "description": "AI assistant powered by Google Gemini",
    "model_config": {
        "provider": "gemini",
        "model": "gemini-2.0-flash",
        "temperature": 0.7,
        "max_tokens": 4096,
        "top_p": 0.9
    },
    "system_prompt": "You are GeminiAssistant, a helpful AI powered by Google Gemini. Answer questions accurately and concisely."
}

def check_server():
    """Check if Letta server is running"""
    try:
        response = requests.get(f"{LETTA_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Letta server is running")
            return True
        else:
            print(f"❌ Letta server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to Letta server: {e}")
        return False

def check_first_time_setup():
    """Check if this is first-time setup"""
    try:
        response = requests.get(f"{LETTA_URL}/api/setup/status")
        return response.json().get("needs_setup", False)
    except:
        return False

def create_admin_account():
    """Create the admin account for first-time setup"""
    try:
        print("🔧 Creating admin account...")
        response = requests.post(
            f"{LETTA_URL}/api/setup/admin",
            json=DEFAULT_ADMIN
        )
        if response.status_code == 200:
            print("✅ Admin account created successfully")
            return DEFAULT_ADMIN
        else:
            print(f"❌ Failed to create admin account: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating admin account: {e}")
        return None

def login(credentials):
    """Login to Letta and get auth token"""
    try:
        response = requests.post(
            f"{LETTA_URL}/api/auth/login",
            json={
                "username": credentials["username"],
                "password": credentials["password"]
            }
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def create_agent(token):
    """Create a Gemini-powered agent"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{LETTA_URL}/api/agents",
            json=GEMINI_AGENT,
            headers=headers
        )
        if response.status_code in [200, 201]:
            agent_id = response.json().get("id")
            print(f"✅ Agent created successfully (ID: {agent_id})")
            return agent_id
        else:
            print(f"❌ Failed to create agent: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

def main():
    """Main execution function"""
    print("🚀 Starting Letta Gemini Agent Setup")
    
    # Check server status
    if not check_server():
        print("❌ Letta server is not accessible. Please make sure it's running.")
        sys.exit(1)
    
    # Check if first-time setup is needed
    if check_first_time_setup():
        print("🔧 First-time setup required")
        credentials = create_admin_account()
        if not credentials:
            print("❌ Failed to complete first-time setup")
            sys.exit(1)
    else:
        credentials = DEFAULT_ADMIN
        print("✅ Letta server already set up")
    
    # Login
    token = login(credentials)
    if not token:
        print("❌ Failed to authenticate")
        sys.exit(1)
    
    # Create agent
    agent_id = create_agent(token)
    if not agent_id:
        print("❌ Failed to create Gemini agent")
        sys.exit(1)
    
    print("\n🎉 Setup Complete!")
    print(f"✅ Your Gemini agent has been created (ID: {agent_id})")
    print(f"✅ Access the ADE at: {LETTA_URL}")
    print(f"✅ Login with: {credentials['username']} / {credentials['password']}")
    print("\n💡 You can now use your Gemini-powered agent in conversations!")

if __name__ == "__main__":
    main()
