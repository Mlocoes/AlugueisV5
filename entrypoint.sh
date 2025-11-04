#!/bin/bash
# Entrypoint script for AlugueisV5
# This script runs on container startup and ensures proper initialization

set -e  # Exit on error

echo "🚀 AlugueisV5 - Starting application..."
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Wait for database to be ready
echo "1. Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

# Extract database connection info from DATABASE_URL
# Format: postgresql://user:password@host:port/database
# Using Python to parse URL reliably to handle special characters in passwords
DB_INFO=$(python3 << 'PYTHON_SCRIPT'
import sys
import os
from urllib.parse import urlparse

try:
    database_url = os.environ.get('DATABASE_URL', '')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)
    
    parsed = urlparse(database_url)
    username = parsed.username or ''
    hostname = parsed.hostname or ''
    port = parsed.port or 5432
    
    if not hostname or not username:
        print("ERROR: Invalid DATABASE_URL format", file=sys.stderr)
        sys.exit(1)
    
    print(f"{username} {hostname} {port}")
except Exception as e:
    print(f"ERROR: Failed to parse DATABASE_URL: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)

# Check if Python script succeeded
if [ $? -ne 0 ]; then
    log_error "Failed to parse DATABASE_URL. Please check the format."
    log_error "Expected format: postgresql://user:password@host:port/database"
    exit 1
fi

# Parse the output
read DB_USER DB_HOST DB_PORT <<< "$DB_INFO"

# Validate parsed values
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ]; then
    log_error "Failed to parse DATABASE_URL. Please check the format."
    log_error "Expected format: postgresql://user:password@host:port/database"
    exit 1
fi

log_info "Database connection: $DB_USER@$DB_HOST:$DB_PORT"

# Wait for PostgreSQL to be ready
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "Timeout waiting for database at $DB_HOST:$DB_PORT"
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
log_info "Database is ready"

# Run database migrations
echo ""
echo "2. Running database migrations..."
if alembic upgrade head; then
    log_info "Migrations completed successfully"
else
    log_error "Failed to run database migrations"
    log_error "Check the alembic configuration and database connection"
    exit 1
fi

# Create admin user if it doesn't exist
echo ""
echo "3. Ensuring admin user exists..."
if python create_admin.py; then
    log_info "Admin user check completed"
else
    log_error "Failed to create or verify admin user"
    log_error "Check create_admin.py and database connection"
    exit 1
fi

# Start the application
echo ""
echo "4. Starting application server..."
log_info "Server starting on ${HOST:-0.0.0.0}:${PORT:-8000}"
echo "========================================="
echo ""

# Execute the main command (passed as arguments to this script)
exec "$@"
