#!/bin/bash
# Development Synchronization Script

set -e

# Ensure script is run from project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[SYNC]${NC} $1"
}

# Error handling function
error() {
    echo -e "${YELLOW}[ERROR]${NC} $1"
    exit 1
}

# Validate Git repository
validate_git_repo() {
    if [ ! -d .git ]; then
        error "Not a Git repository. Please initialize or clone first."
    fi
}

# Pull latest changes
sync_repository() {
    log "Synchronizing Git repository..."
    git fetch origin
    git pull origin main
}

# Set up Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    # Check if venv exists, create if not
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Create environment file from template
setup_environment() {
    log "Configuring environment..."
    
    if [ ! -f .env ]; then
        if [ -f configs/env.template ]; then
            cp configs/env.template .env
            log "Created .env from template"
        else
            error "No .env template found"
        fi
    fi
}

# Docker environment setup
setup_docker() {
    log "Checking Docker configuration..."
    
    if command -v docker &> /dev/null; then
        docker-compose pull
        docker-compose build
    else
        error "Docker not installed. Please install Docker Desktop."
    fi
}

# Main synchronization workflow
main() {
    validate_git_repo
    sync_repository
    setup_python_env
    setup_environment
    setup_docker

    log "Synchronization complete! 🚀"
}

# Run main function
main
