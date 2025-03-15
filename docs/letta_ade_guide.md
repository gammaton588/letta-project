# Letta ADE Guide: Creating Agents with Google Gemini API

## Overview
This guide walks through creating intelligent agents using the Letta Agent Development Environment (ADE) with Google Gemini API integration.

## Prerequisites
- Letta server running on Docker
- Google Gemini API key configured in .env file
- Git setup complete

## Accessing the ADE Interface
1. Ensure your Letta server is running:
   ```bash
   ./scripts/check_letta.sh
   ```
   
2. Access the local ADE interface:
   - URL: http://localhost:8283
   - First-time setup: Create an admin account when prompted

## Creating Your First Gemini-Powered Agent

### Step 1: Navigate to Agent Creation
- In the ADE dashboard, click "Create New Agent"

### Step 2: Configure Basic Settings
- Name: "GeminiAssistant"
- Description: "Intelligent assistant powered by Google Gemini API"
- Agent Type: "Conversational"

### Step 3: Configure Model Settings
- Model: "Google Gemini"
- API Key: Will use the one from your environment variables
- Model Version: "gemini-2.0-flash"
- Temperature: 0.7
- Max Tokens: 4096

### Step 4: Define System Prompt
```
You are an intelligent assistant powered by Google Gemini. Your goal is to provide helpful, 
accurate, and concise responses to user queries while maintaining a conversational tone.
```

### Step 5: Add Tools (Optional)
- Web Search
- Image Analysis
- Calculator
- JSON Handler

### Step 6: Configure Memory Settings
- Enable conversation memory
- Set history length to 10 messages

### Step 7: Save and Deploy
- Click "Save Draft"
- Test the agent in the playground
- When satisfied, click "Deploy Agent"

## Agent Management
- Monitor agent usage in the Analytics section
- Update agent configurations as needed
- Create agent versions to track changes

## Advanced Configurations
- Create custom tools via the Tools section
- Use Memory Blocks for persistent knowledge
- Implement webhooks for external integrations

## Troubleshooting Common Issues
- If the agent isn't responding, check your API key
- For slow responses, consider adjusting the model parameters
- If connections fail, restart your Letta server

## Next Steps
- Experiment with different model parameters
- Explore multi-agent workflows
- Integrate with external data sources
