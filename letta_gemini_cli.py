#!/usr/bin/env python3
"""
Letta-Gemini CLI
A complete command-line utility for managing all aspects of the Letta-Gemini integration.
"""

import os
import sys
import argparse
import json
import logging
import subprocess
import webbrowser
import time
import tempfile
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("letta_gemini_cli")

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.gemini_integration import GeminiAPI, create_letta_agent_config
from scripts.create_letta_gemini_agent import LettaAgentCreator

# Load environment variables
env_path = os.path.expanduser("~/.letta/env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f"Environment file not found at {env_path}")

class LettaGeminiCLI:
    """Main CLI class for managing Letta-Gemini integration"""
    
    def __init__(self, letta_url: str = "http://localhost:8283"):
        """Initialize the CLI with Letta server URL"""
        self.letta_url = letta_url
        self.scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
        self.docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
        
        # Initialize components as needed
        self._creator = None
        self._gemini = None
    
    @property
    def creator(self) -> LettaAgentCreator:
        """Lazy-loaded LettaAgentCreator"""
        if not self._creator:
            try:
                self._creator = LettaAgentCreator(letta_url=self.letta_url)
            except Exception as e:
                logger.error(f"Failed to initialize agent creator: {e}")
                raise
        return self._creator
    
    @property
    def gemini(self) -> GeminiAPI:
        """Lazy-loaded GeminiAPI"""
        if not self._gemini:
            try:
                self._gemini = GeminiAPI()
                logger.info(f"Successfully initialized Gemini API with model: {self._gemini.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {e}")
                raise
        return self._gemini
    
    def check_letta_status(self) -> bool:
        """Check if Letta server is running"""
        try:
            import requests
            response = requests.get(self.letta_url)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_gemini_status(self) -> bool:
        """Check if Gemini API is working"""
        try:
            self.gemini  # Initialize if needed
            return True
        except Exception:
            return False
    
    def run_uat_tests(self) -> bool:
        """Run the user acceptance tests for Gemini integration"""
        uat_script = os.path.join(self.scripts_dir, "run_gemini_integration_uat.py")
        
        if not os.path.exists(uat_script):
            logger.error(f"UAT script not found at: {uat_script}")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, uat_script],
                capture_output=True,
                text=True
            )
            
            # Print the output
            print(result.stdout)
            
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to run UAT tests: {e}")
            return False
    
    def create_agent(self, name: str, description: str, system_prompt: str) -> Dict[str, Any]:
        """Create a new agent in Letta"""
        try:
            result = self.creator.create_gemini_chat_agent(
                name=name,
                description=description,
                system_prompt=system_prompt
            )
            return result
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return {"success": False, "error": str(e)}
    
    def list_agents(self) -> Dict[str, Any]:
        """List all agents in Letta"""
        try:
            return self.creator.list_agents()
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_agent_config_file(self, name: str, description: str, system_prompt: str, output_path: Optional[str] = None) -> str:
        """Generate an agent configuration file for manual import"""
        
        # Create the agent configuration
        agent_config = create_letta_agent_config(
            name=name,
            description=description,
            system_prompt=system_prompt,
            gemini_model="gemini-2.0-flash",
            temperature=0.7,
            max_tokens=4096
        )
        
        # If no output path specified, create a temporary file
        if not output_path:
            fd, output_path = tempfile.mkstemp(suffix=".json", prefix=f"letta_agent_{name}_")
            os.close(fd)
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(agent_config, f, indent=2)
            
        logger.info(f"Agent configuration saved to: {output_path}")
        return output_path
    
    def open_letta_ade(self) -> None:
        """Open the Letta ADE in a web browser"""
        webbrowser.open(self.letta_url)
        logger.info(f"Opened Letta ADE in web browser: {self.letta_url}")
    
    def open_docs(self, doc_name: str) -> None:
        """Open a documentation file in the default viewer"""
        if not doc_name.endswith('.md'):
            doc_name += '.md'
            
        doc_path = os.path.join(self.docs_dir, doc_name)
        
        if not os.path.exists(doc_path):
            logger.error(f"Documentation not found: {doc_path}")
            return
        
        # On macOS, use 'open' command
        try:
            subprocess.run(['open', doc_path])
            logger.info(f"Opened documentation: {doc_path}")
        except Exception as e:
            logger.error(f"Failed to open documentation: {e}")
    
    def test_gemini_api(self, prompt: str) -> str:
        """Test the Gemini API with a prompt"""
        try:
            result = self.gemini.generate_response(prompt)
            if result.get("success"):
                return result.get("text", "No response text")
            else:
                return f"API Error: {result.get('error', 'Unknown error')}"
        except Exception as e:
            logger.error(f"Gemini API test error: {e}")
            return f"Error: {str(e)}"
    
    def start_dashboard(self, port: int = 8099) -> None:
        """Start the Letta Admin Dashboard"""
        dashboard_script = os.path.join(self.scripts_dir, "letta_admin_dashboard.py")
        
        if not os.path.exists(dashboard_script):
            logger.error(f"Dashboard script not found at: {dashboard_script}")
            return
        
        try:
            # Start the dashboard in the background
            process = subprocess.Popen(
                [sys.executable, dashboard_script, "--port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the server time to start
            time.sleep(2)
            
            # Open in browser
            dashboard_url = f"http://localhost:{port}"
            webbrowser.open(dashboard_url)
            
            logger.info(f"Dashboard started at {dashboard_url}")
            logger.info("Press Ctrl+C to stop the dashboard")
            
            # Keep the dashboard running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                process.terminate()
                logger.info("Dashboard stopped")
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")


def handle_status_command(cli: LettaGeminiCLI):
    """Handle the 'status' command"""
    letta_status = cli.check_letta_status()
    gemini_status = cli.check_gemini_status()
    
    print("\n=== Letta-Gemini Integration Status ===")
    print(f"Letta Server: {'✅ Online' if letta_status else '❌ Offline'}")
    print(f"Gemini API: {'✅ Working' if gemini_status else '❌ Not Working'}")
    print(f"Environment Variables: {'✅ Loaded' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
    print(f"Gemini API Key: {'✅ Configured' if os.getenv('GEMINI_API_KEY') else '❌ Not Found'}")
    
    # List agents
    result = cli.list_agents()
    agents = result.get("agents", []) if result.get("success") else []
    
    print(f"\nFound {len(agents)} agent(s) on the Letta server:")
    
    for agent in agents:
        print(f"  - {agent.get('name')} (ID: {agent.get('id')})")
    
    print("\nFor more details, run: python letta_gemini_cli.py dashboard")


def handle_dashboard_command(cli: LettaGeminiCLI, port: Optional[int]):
    """Handle the 'dashboard' command"""
    port = port or 8099
    cli.start_dashboard(port=port)


def handle_uat_command(cli: LettaGeminiCLI):
    """Handle the 'uat' command"""
    print("\n=== Running Gemini Integration UAT Tests ===")
    success = cli.run_uat_tests()
    
    if success:
        print("\n✅ UAT Tests PASSED")
    else:
        print("\n❌ UAT Tests FAILED")
        print("Check the logs above for details.")


def handle_create_agent_command(cli: LettaGeminiCLI, args):
    """Handle the 'create-agent' command"""
    
    # Interactive mode if no name provided
    if not args.name:
        print("\n=== Create a New Gemini-Powered Agent ===")
        name = input("Agent Name: ")
        description = input("Description: ")
        
        print("\nSystem prompt (instructions for the agent):")
        print("Type your prompt and press Enter, then Ctrl+D (Unix) or Ctrl+Z (Windows) to finish.")
        print("---")
        
        system_prompt_lines = []
        try:
            while True:
                line = input()
                system_prompt_lines.append(line)
        except EOFError:
            pass
        
        system_prompt = "\n".join(system_prompt_lines)
    else:
        name = args.name
        description = args.description or f"A Gemini-powered agent named {name}"
        system_prompt = args.system_prompt
    
    print(f"\nCreating agent: {name}")
    
    # First, try direct API creation
    result = cli.create_agent(
        name=name,
        description=description,
        system_prompt=system_prompt
    )
    
    if result.get("success"):
        print(f"✅ Successfully created agent: {name}")
        print(f"Agent ID: {result.get('agent', {}).get('id')}")
    else:
        print(f"❌ API-based agent creation failed.")
        print("Switching to hybrid approach...")
        
        # Generate config file
        config_file = cli.generate_agent_config_file(
            name=name,
            description=description,
            system_prompt=system_prompt
        )
        
        print("\n=== Manual Agent Creation Guide ===")
        print(f"1. Agent configuration saved to: {config_file}")
        print("2. Opening the Letta ADE in your browser...")
        cli.open_letta_ade()
        print("3. Please follow these steps:")
        
        # Show instructions from the guide
        print("""
- Sign in to your Letta ADE account
- Navigate to "Create New Agent" or "Agents > New Agent" 
- Configure your agent with these settings:
  * Name: {name}
  * Description: {description}
  * Agent Type: Conversational
  * Provider/Model: Google Gemini
  * Model Version: gemini-2.0-flash
  * Temperature: 0.7
  * Max Tokens: 4096
  * System Prompt: [paste the system prompt from the saved config file]
- Save and deploy your agent
        """.format(name=name, description=description))
        
        print("\nTIP: You can use the generated config file as a reference.")
        print("Once created, run 'letta_gemini_cli.py list-agents' to verify.")
        
        # Open documentation
        print("\nOpening the Gemini Agent Quick Guide for additional help...")
        cli.open_docs("gemini_agent_quick_guide")


def handle_list_agents_command(cli: LettaGeminiCLI):
    """Handle the 'list-agents' command"""
    print("\n=== Letta Agents ===")
    
    result = cli.list_agents()
    
    if not result.get("success"):
        print(f"❌ Failed to list agents: {result.get('error')}")
        print("Possible reasons:")
        print("- Letta server not running")
        print("- No agents created yet")
        print("- API endpoint might not be available (try creating agents via web UI)")
        print("\nTry opening the Letta ADE in your browser:")
        print(f"  {cli.letta_url}")
        return
    
    agents = result.get("agents", [])
    
    if not agents:
        print("No agents found in the Letta ADE.")
        print("Create your first agent with: python letta_gemini_cli.py create-agent")
        return
    
    print(f"Found {len(agents)} agent(s):")
    
    for agent in agents:
        print(f"\nID: {agent.get('id')}")
        print(f"Name: {agent.get('name')}")
        print(f"Description: {agent.get('description')}")
        print(f"Model: {agent.get('model_config', {}).get('model', 'Unknown')}")


def handle_docs_command(cli: LettaGeminiCLI, doc_name: Optional[str]):
    """Handle the 'docs' command"""
    if doc_name:
        cli.open_docs(doc_name)
        return
    
    # List available docs
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    
    if not os.path.exists(docs_dir):
        print("❌ Documentation directory not found.")
        return
    
    docs = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
    
    if not docs:
        print("No documentation found.")
        return
    
    print("\n=== Available Documentation ===")
    
    for i, doc in enumerate(docs, 1):
        doc_name = doc.replace('.md', '')
        print(f"{i}. {doc_name}")
    
    try:
        choice = int(input("\nEnter the number of the document to open (0 to cancel): "))
        if 1 <= choice <= len(docs):
            cli.open_docs(docs[choice-1])
    except (ValueError, IndexError):
        print("Invalid selection.")


def handle_test_gemini_command(cli: LettaGeminiCLI, prompt: Optional[str]):
    """Handle the 'test-gemini' command"""
    if not prompt:
        print("\n=== Test Gemini API ===")
        prompt = input("Enter your test prompt: ")
    
    print(f"\nPrompt: {prompt}")
    print("\nGenerating response...")
    
    response = cli.test_gemini_api(prompt)
    
    print("\nResponse:")
    print(response)


def handle_web_workflow_command(cli: LettaGeminiCLI):
    """Handle the 'web-workflow' command - guides through the web UI process"""
    print("\n=== Letta ADE Web Workflow ===")
    print("This assistant will help you create a Gemini agent using the Letta web interface.")
    
    # Open the web interface
    print("\nStep 1: Opening the Letta ADE in your browser...")
    cli.open_letta_ade()
    
    # Guide through the steps with verification checkpoints
    print("\nStep 2: Follow these steps in the web interface:")
    print("""
1. Sign in to your Letta ADE account
   → If this is your first time, you'll be prompted to create an admin account
   → Use simple credentials you can remember (e.g., admin/admin@example.com/secure_password)

2. Navigate to Agent Creation
   → From the dashboard, click "Create New Agent" or similar
   → If you don't see this option, look for "Agents" in the sidebar and then "New Agent"

3. Configure Basic Agent Settings
   → Name: GeminiAssistant
   → Description: A helpful AI assistant powered by Google Gemini
   → Agent Type: Conversational (or similar option)

4. Configure Model Settings
   → Provider/Model: Select Google Gemini (or similar option)
   → Model Version: gemini-2.0-flash
   → API Key: Your key should be automatically available from the environment variables
   → Temperature: 0.7 (balanced creativity/consistency)
   → Max Tokens: 4096 (or maximum allowed)
    """)
    
    # Ask if they want a template system prompt
    print("\nWould you like to use a template system prompt for your agent?")
    use_template = input("Enter 'y' for yes, any other key for no: ").lower() == 'y'
    
    if use_template:
        system_prompt = """You are GeminiAssistant, a helpful AI assistant powered by Google Gemini.
Your goal is to provide helpful, accurate, and concise responses.
Be conversational but professional in your tone.
Always provide the most relevant information to the user's query."""
        
        print("\nSystem Prompt Template:")
        print("---------------")
        print(system_prompt)
        print("---------------")
        
        # Save to a temporary file for easy copying
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(system_prompt)
            prompt_file = f.name
            
        print(f"\nThe template has been saved to: {prompt_file}")
        print("Copy and paste this into the 'System Prompt' field in the web interface.")
    
    # Continue with the remaining steps
    print("""
5. Define your System Prompt in the web interface
   → Paste the template or enter your custom instructions
   
6. Test Your Agent
   → Look for a "Test" or "Playground" section
   → Send a test message: "Hello, can you tell me what you can help me with?"
   → Verify the agent responds appropriately using the Gemini model

7. Save and Deploy
   → Save your agent configuration
   → Deploy or publish it to make it available for use
    """)
    
    # Wait for user to confirm they've completed the process
    input("\nPress Enter when you've completed all steps...")
    
    # Verify the agent was created
    print("\nVerifying agent creation...")
    result = cli.list_agents()
    agents = result.get("agents", []) if result.get("success") else []
    
    if agents:
        print("\n✅ Successfully found agents in Letta ADE:")
        for agent in agents:
            print(f"  - {agent.get('name')} (ID: {agent.get('id')})")
        print("\nYour Gemini-powered agent is ready to use!")
    else:
        print("\n❓ No agents found in Letta ADE.")
        print("Possible reasons:")
        print("- Agent creation is still in progress")
        print("- The API endpoint for listing agents might not be available")
        print("- There was an issue during agent creation")
        
        print("\nTry manually verifying in the web interface that your agent was created.")
    
    # Open the guide
    print("\nOpening the Gemini Agent Quick Guide for additional help...")
    cli.open_docs("gemini_agent_quick_guide")


def main():
    """Parse command line arguments and handle commands"""
    
    parser = argparse.ArgumentParser(description="Letta-Gemini CLI")
    
    parser.add_argument("--letta-url", default="http://localhost:8283",
                        help="URL of the Letta server (default: http://localhost:8283)")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check integration status")
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start the admin dashboard")
    dashboard_parser.add_argument("--port", type=int, help="Port to run the dashboard on")
    
    # UAT command
    uat_parser = subparsers.add_parser("uat", help="Run user acceptance tests")
    
    # Create agent command
    create_parser = subparsers.add_parser("create-agent", help="Create a new agent")
    create_parser.add_argument("--name", help="Agent name")
    create_parser.add_argument("--description", help="Agent description")
    create_parser.add_argument("--system-prompt", help="System prompt/instructions")
    
    # List agents command
    list_parser = subparsers.add_parser("list-agents", help="List all agents")
    
    # Docs command
    docs_parser = subparsers.add_parser("docs", help="View documentation")
    docs_parser.add_argument("doc_name", nargs="?", help="Name of documentation to view")
    
    # Test Gemini command
    test_gemini_parser = subparsers.add_parser("test-gemini", help="Test the Gemini API")
    test_gemini_parser.add_argument("prompt", nargs="?", help="Test prompt")
    
    # Web workflow command
    web_workflow_parser = subparsers.add_parser("web-workflow", 
                                            help="Interactive web-based workflow for agent creation")
    
    args = parser.parse_args()
    
    # Create CLI instance
    try:
        cli = LettaGeminiCLI(letta_url=args.letta_url)
    except Exception as e:
        logger.error(f"Failed to initialize CLI: {e}")
        return 1
    
    # Handle commands
    try:
        if args.command == "status":
            handle_status_command(cli)
        elif args.command == "dashboard":
            handle_dashboard_command(cli, args.port)
        elif args.command == "uat":
            handle_uat_command(cli)
        elif args.command == "create-agent":
            handle_create_agent_command(cli, args)
        elif args.command == "list-agents":
            handle_list_agents_command(cli)
        elif args.command == "docs":
            handle_docs_command(cli, args.doc_name)
        elif args.command == "test-gemini":
            handle_test_gemini_command(cli, args.prompt)
        elif args.command == "web-workflow":
            handle_web_workflow_command(cli)
        else:
            # Default to showing help
            parser.print_help()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
