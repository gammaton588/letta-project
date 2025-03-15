# Letta-Gemini Integration Guide

This guide explains how to use the integration between Google Gemini API and Letta's Agent Development Environment (ADE) that we've created.

## Overview

We've built two powerful components:

1. **Gemini Integration Library** (`gemini_integration.py`): A comprehensive Python library that provides a clean interface to the Google Gemini API.
2. **Letta Agent Creator** (`create_letta_gemini_agent.py`): A command-line utility to automate the creation of Gemini-powered agents in Letta.

## Prerequisites

- Letta server running on Docker (verified at http://localhost:8283)
- Google Gemini API key configured in the Letta environment
- Python 3.9+ with required packages installed:
  ```
  python3 -m pip install -q -U google-generativeai python-dotenv requests
  ```

## Using the Gemini Integration Library

The `gemini_integration.py` library provides multiple ways to interact with the Gemini API:

### Basic Usage

```python
from scripts.gemini_integration import GeminiAPI

# Initialize the API
api = GeminiAPI()  # Automatically uses GEMINI_API_KEY from environment

# Generate a simple response
response = api.generate_response(
    prompt="What are the key features of Docker?",
    system_prompt="You are a helpful assistant that specializes in DevOps topics."
)

print(response["text"])  # Display the response text
```

### Multi-Turn Conversations

```python
# Create a chat session
chat = api.create_chat_session(
    system_prompt="You are a programming tutor specialized in Python."
)

# First message
response1 = chat.send_message("What is object-oriented programming?")
print(response1["text"])

# Follow-up message (maintains conversation context)
response2 = chat.send_message("Can you give an example in Python?")
print(response2["text"])
```

### Image Analysis

```python
# Analyze an image (requires gemini-1.5-pro model)
analysis = api.analyze_image(
    prompt="Describe what you see in this image",
    image_path="/path/to/your/image.jpg"
)

print(analysis["text"])
```

## Creating Letta Agents

The `create_letta_gemini_agent.py` script allows you to quickly create and manage Gemini-powered agents in your Letta ADE.

### Command-Line Usage

#### List All Agents

```bash
python3 /Users/myaiserver/Projects/letta-project/scripts/create_letta_gemini_agent.py \
  --username your_username \
  --password your_password \
  list
```

#### Create a General Chat Agent

```bash
python3 /Users/myaiserver/Projects/letta-project/scripts/create_letta_gemini_agent.py \
  --username your_username \
  --password your_password \
  create-chat \
  --name "Friendly Assistant" \
  --description "A helpful, conversational AI assistant" \
  --system-prompt "You are a friendly and helpful AI assistant. Your goal is to provide clear, concise, and accurate information to users in a conversational manner."
```

#### Create an Expert Agent

```bash
python3 /Users/myaiserver/Projects/letta-project/scripts/create_letta_gemini_agent.py \
  --username your_username \
  --password your_password \
  create-expert \
  --name "Python Coach" \
  --description "Expert programming assistant for Python" \
  --expertise "Python programming" \
  --system-prompt "You are Python Coach, an expert in Python programming. Help users understand Python concepts, debug code, and learn best practices for Python development."
```

## Programmatic Agent Creation

You can also use the library programmatically in your own Python scripts:

```python
from scripts.create_letta_gemini_agent import LettaAgentCreator

# Initialize the creator
creator = LettaAgentCreator(letta_url="http://localhost:8283")

# Optional: Login if required
creator.login(username="your_username", password="your_password")

# Create a general chat agent
result = creator.create_gemini_chat_agent(
    name="Data Science Assistant",
    description="AI assistant specialized in data science topics",
    system_prompt="You are a data science specialist. Help users understand concepts in data analysis, machine learning, and statistics."
)

if result["success"]:
    print(f"Created agent with ID: {result['agent'].get('id')}")
else:
    print(f"Error: {result.get('error')}")
```

## Recommended Agent Templates

### General-Purpose Assistant

```python
creator.create_gemini_chat_agent(
    name="Gemini Assistant",
    description="A versatile, helpful AI assistant",
    system_prompt="""You are Gemini Assistant, a helpful and versatile AI.
Your goal is to provide accurate, helpful, and engaging responses.
Be conversational and friendly while maintaining professionalism.
If you don't know something, admit it rather than making up information."""
)
```

### Technical Expert

```python
creator.create_gemini_expert_agent(
    name="Tech Expert",
    description="Specialist in technology and programming",
    expertise="technology and programming",
    system_prompt="""You are Tech Expert, a specialist in technology and programming.
Provide detailed and accurate information about programming languages, software development, 
hardware, networking, and other technical topics.
Include code examples when relevant, and explain concepts in a clear, accessible way."""
)
```

### Creative Writer

```python
creator.create_gemini_chat_agent(
    name="Creative Writer",
    description="AI assistant for creative writing assistance",
    system_prompt="""You are Creative Writer, an AI assistant specialized in creative writing.
Help users with story ideas, character development, plot structure, and writing techniques.
Provide constructive feedback on writing samples and suggest improvements.
Be imaginative and inspirational while providing practical writing advice."""
)
```

## Advanced Configuration

The Gemini integration supports advanced configuration options:

- **Model Selection**: Choose between `gemini-2.0-flash` (faster), `gemini-2.0-pro` (more powerful), or `gemini-1.5-pro` (for multimodal capabilities)
- **Temperature**: Control the randomness/creativity (0.0-1.0)
- **Max Output Tokens**: Limit the length of responses
- **Top-p/Top-k**: Fine-tune the response generation process

## Troubleshooting

If you encounter issues:

1. **API Key Issues**: Ensure your Gemini API key is correctly set in `~/.letta/env`
2. **Connection Problems**: Verify the Letta server is running at the expected URL
3. **Model Errors**: Check that you're using valid model names and parameters
4. **Authentication Errors**: Confirm your Letta username and password are correct

## Next Steps

1. **Experiment with different models**: Try different Gemini models to find the best fit for your use case
2. **Customize system prompts**: Refine your system prompts to get more targeted responses
3. **Integrate with other tools**: Combine your Gemini-powered agents with other systems
4. **Monitor performance**: Keep an eye on API usage and agent performance

---

For more information on the Google Gemini API, visit: https://ai.google.dev/api?lang=python
