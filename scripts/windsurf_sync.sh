#!/bin/bash
# Windsurf Cross-Device Synchronization Toolkit
# Designed for seamless development between Mac mini and MacBook Air

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[WINDSURF SYNC]${NC} $1"
}

# Error handling function
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Validate Git repository
validate_repo() {
    if [ ! -d .git ]; then
        error "Not a Git repository. Please initialize or clone first."
    fi
}

# Comprehensive synchronization workflow
sync_workflow() {
    clear
    echo -e "${YELLOW}🔄 Windsurf Cross-Device Synchronization${NC}"
    echo "-------------------------------------------"

    # 1. Validate repository
    validate_repo

    # 2. Stash any local changes
    log "Checking for local changes..."
    if [[ -n $(git status -s) ]]; then
        git stash save "Windsurf auto-stash: $(date '+%Y-%m-%d %H:%M:%S')"
        log "Local changes stashed temporarily"
    fi

    # 3. Fetch latest changes
    log "Fetching latest repository changes..."
    git fetch origin

    # 4. Pull latest changes
    log "Pulling latest changes from main branch..."
    git pull origin main

    # 5. Update submodules (if any)
    log "Updating submodules..."
    git submodule update --init --recursive

    # 6. Restore stashed changes if applicable
    if [[ -n $(git stash list) ]]; then
        log "Attempting to apply stashed changes..."
        git stash pop
    fi

    # 7. Run environment verification
    log "Verifying development environment..."
    python3 scripts/env_check.py

    # 8. Update dependencies
    log "Updating project dependencies..."
    if [ -f requirements.txt ]; then
        python3 -m pip install -r requirements.txt
    fi

    # 9. Run integration tests
    log "Running integration tests..."
    python3 -m pytest tests/

    echo -e "\n${GREEN}✅ Synchronization Complete!${NC}"
}

# Main execution
main() {
    case "$1" in
        "sync")
            sync_workflow
            ;;
        "status")
            python3 scripts/env_check.py
            ;;
        *)
            echo "Usage: $0 {sync|status}"
            exit 1
            ;;
    esac
}

main "$@"
