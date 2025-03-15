#!/bin/bash

# Define colors for better visibility
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear
echo -e "${BOLD}🔍 LETTA SERVER MONITOR${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}❌ Docker is not running${NC}"
  echo -e "${YELLOW}ℹ️  Please start Docker Desktop first${NC}"
  exit 1
fi

echo -e "⏳ Checking Letta server status..."
echo ""

# Check if Docker container is running
CONTAINER_ID=$(docker ps -q --filter "ancestor=letta/letta:latest")

if [[ -z "$CONTAINER_ID" ]]; then
  echo -e "${RED}❌ Letta container is NOT running${NC}"
  echo ""
  echo -e "${YELLOW}💡 To start the Letta server, run:${NC}"
  echo -e "docker run \\
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \\
  -p 8283:8283 \\
  --env-file ~/.letta/env \\
  letta/letta:latest"
  exit 1
fi

# Get container status and extract startup time
CONTAINER_STATUS=$(docker ps --format "{{.Status}}" --filter "id=$CONTAINER_ID")
echo -e "${GREEN}✅ Container Status: $CONTAINER_STATUS${NC}"

# Show container logs (last 5 lines only)
echo ""
echo -e "${BOLD}📋 Recent Container Logs:${NC}"
echo -e "${BLUE}--------------------------------------${NC}"
docker logs $CONTAINER_ID --tail 5
echo -e "${BLUE}--------------------------------------${NC}"

# Check server access
echo ""
echo -e "${BOLD}🔄 Connection Test:${NC}"
curl -s -m 2 -o /dev/null -w "HTTP Status: %{http_code}" http://localhost:8283/ || echo "Connection failed"

# Show container details
echo ""
echo -e "${BOLD}📊 Server Details:${NC}"
echo -e "${BLUE}--------------------------------------${NC}"
echo -e "🏷️  Container ID: ${YELLOW}$CONTAINER_ID${NC}"
echo -e "🔌 Port Mapping: ${YELLOW}$(docker port $CONTAINER_ID 8283)${NC}"
echo -e "🌐 Server URL: ${YELLOW}http://localhost:8283${NC}"
echo -e "👾 ADE Interface: ${YELLOW}https://app.letta.com/development-servers/local/dashboard${NC}"
echo -e "${BLUE}======================================${NC}"

# Provide helpful commands
echo ""
echo -e "${BOLD}💡 Helpful Commands:${NC}"
echo -e "▶️  View logs: ${YELLOW}docker logs $CONTAINER_ID${NC}"
echo -e "⏹️  Stop server: ${YELLOW}docker stop $CONTAINER_ID${NC}"
echo -e "🔄 Restart server: ${YELLOW}docker restart $CONTAINER_ID${NC}"
