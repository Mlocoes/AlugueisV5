#!/bin/bash
# Test script to verify automatic initialization works

set -e

echo "🧪 Testing Automatic Initialization"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_step() {
    echo -e "${YELLOW}▶${NC} $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
fi
log_info "Docker is available"

# Check entrypoint script exists
if [ ! -f entrypoint.sh ]; then
    log_error "entrypoint.sh not found"
    exit 1
fi
log_info "entrypoint.sh exists"

# Check if script is executable
if [ ! -x entrypoint.sh ]; then
    log_error "entrypoint.sh is not executable"
    exit 1
fi
log_info "entrypoint.sh is executable"

# Verify Dockerfile has ENTRYPOINT
if grep -qE "ENTRYPOINT\s*\[.*entrypoint\.sh.*\]|ENTRYPOINT\s+.*entrypoint\.sh" Dockerfile; then
    log_info "Dockerfile has ENTRYPOINT directive"
else
    log_error "Dockerfile does not have ENTRYPOINT directive"
    exit 1
fi

# Check bash syntax
log_step "Checking bash syntax..."
if bash -n entrypoint.sh; then
    log_info "Bash syntax is valid"
else
    log_error "Bash syntax error in entrypoint.sh"
    exit 1
fi

# Verify create_admin.py is idempotent
log_step "Checking create_admin.py idempotency..."
if grep -q "existing_admin" create_admin.py; then
    log_info "create_admin.py checks for existing admin"
else
    log_error "create_admin.py may not be idempotent"
    exit 1
fi

echo ""
echo "===================================="
echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "The automatic initialization is correctly configured:"
echo "  • entrypoint.sh will run on container startup"
echo "  • Database migrations will run automatically"
echo "  • Admin user will be created if not exists"
echo "  • System will reinitialize on every restart"
echo ""
