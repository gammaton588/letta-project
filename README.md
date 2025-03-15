# Letta Server with Gemini Integration

## Overview
A Docker-based Letta server implementation that integrates with Google's Gemini API for advanced natural language processing and agent development. This project focuses on the Agent Development Environment (ADE) capabilities of Letta.

## Features
- 🤖 Gemini-powered AI agents
- 🔒 Secure environment configuration
- 🐳 Docker-based deployment
- 🚀 Auto-start capability on system boot
- 📝 REST API for agent management
- 🔍 AI-powered monitoring and self-repair
- 🛠️ Autonomous troubleshooting

## Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Google Gemini API key

## Quick Start

### Environment Setup
1. Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key
```

2. Configure Docker environment in `configs/.env`:
```bash
LMSTUDIO_BASE_URL=http://localhost:1234/v1
GEMINI_MODEL=gemini-2.0-flash
LETTA_HOST=0.0.0.0
LETTA_PORT=8283
```

### Starting the Server
```bash
docker-compose up -d
```

The server will be available at `http://localhost:8284`

### Auto-start Configuration
The server is configured to start automatically on system boot using launchd:
- Launch Agent: `~/Library/LaunchAgents/com.letta.server.plist`
- Logs: 
  - `~/Library/Logs/letta-server.log`
  - `~/Library/Logs/letta-server.error.log`

## Monitoring & Self-Repair

The Letta server includes an AI-powered monitoring system that automatically checks server health and performs self-repair operations.

### Using the Monitor CLI

The `letta-monitor` command can be run from anywhere on your system:

```bash
# Check server status with AI diagnostics
letta-monitor status

# View monitoring logs
letta-monitor logs

# Force repair check
letta-monitor repair

# Start monitoring service
letta-monitor start

# Stop monitoring service
letta-monitor stop

# Show help
letta-monitor help
```

### Monitoring Features

- 🤖 AI-powered diagnostics using Gemini
- 🔄 Hourly automated health checks
- 🔧 Automatic repair of common issues
- 📊 Detailed repair history tracking
- 📝 Log rotation and management
- 🧠 Root cause analysis and prevention recommendations

### Monitoring Configuration
- Launch Agent: `~/Library/LaunchAgents/com.letta.monitor.plist`
- Logs:
  - `~/Library/Logs/letta-monitor.log`
  - `~/Library/Logs/letta-monitor.stdout.log`
  - `~/Library/Logs/letta-monitor.stderr.log`

## API Endpoints

### Health Check
```
GET http://localhost:8284/
Response: {"status": "ok", "message": "Letta server is running"}
```

### Agent Management
- List Agents:
  ```
  GET /api/v1/agents
  ```

- Create Agent:
  ```
  POST /api/v1/agents
  {
    "name": "string",
    "description": "string",
    "system_prompt": "string",
    "model_config": {
      "provider": "gemini",
      "model": "gemini-2.0-flash",
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }
  ```

- Get Agent:
  ```
  GET /api/v1/agents/{agent_id}
  ```

- Delete Agent:
  ```
  DELETE /api/v1/agents/{agent_id}
  ```

## CLI Usage
The server also provides a command-line interface:

```bash
# Check server status
python3 letta_server_manager.py status

# List all agents
python3 letta_server_manager.py list

# Create a new agent
python3 letta_server_manager.py create \
  --name "MyAgent" \
  --description "Description" \
  --system-prompt "System prompt" \
  --model gemini-2.0-flash
```

## Project Structure
```
letta-project/
├── configs/
│   ├── .env          # Docker environment configuration
│   └── env.template  # Template for environment setup
├── docs/
│   └── gemini_agent_quick_guide.md
├── letta_server/     # Server implementation
├── scripts/
│   ├── ai_diagnostics.py      # AI-powered diagnostics
│   ├── check_letta_status.py  # Server status check
│   ├── letta-monitor          # Global CLI tool
│   └── monitor_letta.sh       # Monitoring wrapper
├── .env             # Local environment file (not in VCS)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Security Notes
- API keys are stored in local environment files
- Environment variables are properly isolated in Docker
- Sensitive data is never committed to version control
- Use HTTPS in production environments

## Troubleshooting
1. Check server status with AI diagnostics:
   ```bash
   letta-monitor status
   ```

2. View Docker logs:
   ```bash
   docker-compose logs letta-server
   ```

3. Manage auto-start service:
   ```bash
   # Stop service
   launchctl unload ~/Library/LaunchAgents/com.letta.server.plist
   
   # Start service
   launchctl load ~/Library/LaunchAgents/com.letta.server.plist
   ```

4. Run AI-powered repair:
   ```bash
   letta-monitor repair
   ```

## Dependencies
- Flask==2.3.2
- Flask-CORS==4.0.0
- python-dotenv==1.0.0
- gunicorn==20.1.0
- google-generativeai==0.3.1
- requests==2.31.0
- uuid==1.30
