#!/usr/bin/env python3
"""
Production-Ready Letta Agents Creator

This script creates a set of production-ready Gemini-powered agents for the Letta ADE.
These agents are optimized for different use cases and demonstrate best practices.
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.create_letta_gemini_agent import LettaAgentCreator
from scripts.gemini_integration import create_letta_agent_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("production_agents")

# Load environment variables
load_dotenv(os.path.expanduser("~/.letta/env"))

def create_single_agent(name: str, description: str, system_prompt: str, username=None, password=None, letta_url="http://localhost:8283"):
    """Create a single Gemini-powered agent with the specified parameters"""
    
    # Initialize agent creator
    creator = LettaAgentCreator(letta_url=letta_url)
    
    # Login if credentials provided
    if username and password:
        if not creator.login(username, password):
            logger.error("Login failed, attempting to create agent without authentication.")
    
    logger.info(f"Creating agent: {name}")
    
    result = creator.create_gemini_chat_agent(
        name=name,
        description=description,
        system_prompt=system_prompt
    )
    
    if result["success"]:
        logger.info(f"✅ Successfully created: {name}")
        return {
            "name": name,
            "success": True,
            "agent_id": result["agent"].get("id", "Unknown")
        }
    else:
        logger.error(f"❌ Failed to create: {name}")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
        return {
            "name": name,
            "success": False,
            "error": result.get("error", "Unknown error")
        }

def create_production_agents(username=None, password=None, letta_url="http://localhost:8283"):
    """Create a set of production-ready agents in Letta"""
    
    # Initialize agent creator
    creator = LettaAgentCreator(letta_url=letta_url)
    
    # Login if credentials provided
    if username and password:
        if not creator.login(username, password):
            logger.error("Login failed, attempting to create agents without authentication.")
    
    # Agent 1: General Assistant
    general_assistant = {
        "name": "Gemini Assistant",
        "description": "A helpful, general-purpose AI assistant powered by Google Gemini",
        "system_prompt": """You are Gemini Assistant, a helpful AI assistant powered by Google Gemini.
Your goal is to provide helpful, accurate, and concise responses to user queries.
Be conversational but professional in your tone.
If you're not sure about an answer, acknowledge the limitations of your knowledge.
Always prioritize providing the most useful and relevant information to the user."""
    }
    
    # Agent 2: Code Expert
    code_expert = {
        "name": "Code Expert",
        "description": "Specialized programming assistant for software development",
        "system_prompt": """You are Code Expert, a specialized AI assistant focused on programming and software development.
Your strengths include:
- Explaining programming concepts clearly
- Providing code examples and solutions
- Debugging code issues
- Suggesting best practices and optimizations
- Recommending design patterns and architecture approaches

When providing code, ensure it is:
- Well-documented with comments
- Following best practices for the language/framework
- Easy to understand and maintain
- Properly formatted and indented
- Free of security vulnerabilities

For complex topics, break down your explanations into simple steps.
If asked about a language or framework you're not familiar with, acknowledge your limitations."""
    }
    
    # Agent 3: Creative Writer
    creative_writer = {
        "name": "Creative Writer",
        "description": "AI assistant for creative writing, storytelling, and content creation",
        "system_prompt": """You are Creative Writer, an AI assistant specialized in creative writing and content creation.
Your goal is to help users with:
- Developing story ideas and narratives
- Creating engaging characters and dialogue
- Crafting compelling blog posts and articles
- Generating creative content for various purposes
- Providing constructive feedback on writing

Your responses should be imaginative, inspiring, and tailored to the user's needs.
When appropriate, offer multiple options or perspectives to spark creativity.
Focus on being helpful and supportive of the user's creative process."""
    }
    
    # Create the agents
    agents = [general_assistant, code_expert, creative_writer]
    results = []
    
    for agent_config in agents:
        logger.info(f"Creating agent: {agent_config['name']}")
        
        result = creator.create_gemini_chat_agent(
            name=agent_config["name"],
            description=agent_config["description"],
            system_prompt=agent_config["system_prompt"]
        )
        
        if result["success"]:
            logger.info(f"✅ Successfully created: {agent_config['name']}")
            results.append({
                "name": agent_config["name"],
                "success": True,
                "agent_id": result["agent"].get("id", "Unknown")
            })
        else:
            logger.error(f"❌ Failed to create: {agent_config['name']}")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            results.append({
                "name": agent_config["name"],
                "success": False,
                "error": result.get("error", "Unknown error")
            })
    
    # Print summary
    logger.info("\n=== Agent Creation Summary ===")
    success_count = sum(1 for r in results if r["success"])
    logger.info(f"Total agents attempted: {len(agents)}")
    logger.info(f"Successfully created: {success_count}")
    logger.info(f"Failed: {len(agents) - success_count}")
    
    for result in results:
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        if result["success"]:
            logger.info(f"{status}: {result['name']} (ID: {result['agent_id']})")
        else:
            logger.info(f"{status}: {result['name']} - {result.get('error', 'Unknown error')}")
    
    return success_count > 0

def main():
    """Parse command line arguments and create agents"""
    
    parser = argparse.ArgumentParser(description="Create production-ready Gemini agents in Letta")
    
    parser.add_argument("--letta-url", default="http://localhost:8283",
                        help="URL of the Letta server (default: http://localhost:8283)")
    
    parser.add_argument("--username", 
                        help="Letta ADE username (optional)")
    
    parser.add_argument("--password",
                        help="Letta ADE password (optional)")
    
    # Add arguments for creating a single agent
    parser.add_argument("--name", 
                        help="Name of a single agent to create")
    
    parser.add_argument("--description",
                        help="Description of the agent")
    
    parser.add_argument("--system-prompt",
                        help="System prompt for the agent")
    
    args = parser.parse_args()
    
    # Determine whether to create a single agent or the default set
    if args.name and args.system_prompt:
        # Create a single custom agent
        description = args.description or f"A Gemini-powered AI assistant named {args.name}"
        result = create_single_agent(
            name=args.name,
            description=description,
            system_prompt=args.system_prompt,
            username=args.username,
            password=args.password,
            letta_url=args.letta_url
        )
        success = result["success"]
    else:
        # Create the default set of agents
        success = create_production_agents(
            username=args.username,
            password=args.password,
            letta_url=args.letta_url
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
