#!/usr/bin/env python3
"""
Test script for Google Gemini API integration
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys

# Load environment variables from .letta/env
load_dotenv('/Users/myaiserver/.letta/env')

# Get API key from environment
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
    sys.exit(1)

print("🔑 API key found in environment")

# Configure the Gemini API
genai.configure(api_key=api_key)

# List available models
try:
    print("\n📋 Available Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    sys.exit(1)

# Test with a simple prompt
try:
    print("\n🧪 Testing API with a simple prompt:")
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hello! Please respond with a short greeting.")
    
    print("\n✅ Response from Gemini API:")
    print("-" * 50)
    print(response.text)
    print("-" * 50)
    print("\n✅ Google Gemini API integration is working!")
except Exception as e:
    print(f"❌ Error generating content: {e}")
    sys.exit(1)
