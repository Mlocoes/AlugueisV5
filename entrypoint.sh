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
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')

while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "Timeout waiting for database"
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
alembic upgrade head
log_info "Migrations completed"

# Create admin user if it doesn't exist
echo ""
echo "3. Ensuring admin user exists..."
python create_admin.py
log_info "Admin user check completed"

# Start the application
echo ""
echo "4. Starting application server..."
log_info "Server starting on ${HOST:-0.0.0.0}:${PORT:-8000}"
echo "========================================="
echo ""

# Execute the main command (passed as arguments to this script)
exec "$@"
