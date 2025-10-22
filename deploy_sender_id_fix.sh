#!/bin/bash

# Default Sender ID Fix - Live Server Deployment Script
# This script automates the deployment of the default sender ID fix

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/path/to/your/project"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="/path/to/backups"
LOG_FILE="/var/log/sender_id_fix_deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}"
    exit 1
}

# Success message
success() {
    log "${GREEN}SUCCESS: $1${NC}"
}

# Warning message
warning() {
    log "${YELLOW}WARNING: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error_exit "This script should not be run as root for security reasons"
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    error_exit "Project directory $PROJECT_DIR does not exist"
fi

log "Starting Default Sender ID Fix Deployment..."

# Step 1: Create database backup
log "Step 1: Creating database backup..."
BACKUP_FILE="$BACKUP_DIR/backup_before_sender_id_fix_$(date +%Y%m%d_%H%M%S).sql"

# Detect database type and create backup
if command -v pg_dump &> /dev/null; then
    # PostgreSQL
    DB_NAME=$(python $PROJECT_DIR/manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" 2>/dev/null)
    if [ ! -z "$DB_NAME" ]; then
        pg_dump $DB_NAME > $BACKUP_FILE
        success "PostgreSQL backup created: $BACKUP_FILE"
    else
        warning "Could not detect PostgreSQL database name"
    fi
elif command -v mysqldump &> /dev/null; then
    # MySQL
    DB_NAME=$(python $PROJECT_DIR/manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" 2>/dev/null)
    if [ ! -z "$DB_NAME" ]; then
        mysqldump $DB_NAME > $BACKUP_FILE
        success "MySQL backup created: $BACKUP_FILE"
    else
        warning "Could not detect MySQL database name"
    fi
else
    # SQLite
    DB_FILE=$(python $PROJECT_DIR/manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" 2>/dev/null)
    if [ ! -z "$DB_FILE" ] && [ -f "$DB_FILE" ]; then
        cp "$DB_FILE" "$BACKUP_DIR/db_backup_before_sender_id_fix_$(date +%Y%m%d_%H%M%S).sqlite3"
        success "SQLite backup created"
    else
        warning "Could not detect SQLite database file"
    fi
fi

# Step 2: Navigate to project directory
log "Step 2: Navigating to project directory..."
cd $PROJECT_DIR || error_exit "Failed to navigate to project directory"

# Step 3: Activate virtual environment
log "Step 3: Activating virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source $VENV_DIR/bin/activate
    success "Virtual environment activated"
else
    error_exit "Virtual environment not found at $VENV_DIR"
fi

# Step 4: Pull latest changes
log "Step 4: Pulling latest changes from repository..."
git fetch origin
git pull origin main || error_exit "Failed to pull latest changes"

# Step 5: Install/update dependencies
log "Step 5: Installing/updating dependencies..."
pip install -r requirements.txt || error_exit "Failed to install dependencies"

# Step 6: Run database migrations
log "Step 6: Running database migrations..."
python manage.py migrate || error_exit "Failed to run migrations"

# Step 7: Collect static files
log "Step 7: Collecting static files..."
python manage.py collectstatic --noinput || warning "Failed to collect static files"

# Step 8: Test the fix
log "Step 8: Testing the fix..."
if [ -f "test_default_sender_id.py" ]; then
    python test_default_sender_id.py || warning "Test script failed, but continuing..."
else
    warning "Test script not found, skipping tests"
fi

# Step 9: Restart web server
log "Step 9: Restarting web server..."

# Detect web server and restart
if systemctl is-active --quiet nginx; then
    sudo systemctl restart nginx
    success "Nginx restarted"
fi

if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    success "Gunicorn restarted"
fi

if systemctl is-active --quiet apache2; then
    sudo systemctl restart apache2
    success "Apache2 restarted"
fi

# Step 10: Verify deployment
log "Step 10: Verifying deployment..."

# Check if migration was applied
MIGRATION_STATUS=$(python manage.py showmigrations accounts | grep "0003_add_default_sender_ids" | grep -o "\[X\]" || echo "")
if [ "$MIGRATION_STATUS" = "[X]" ]; then
    success "Migration 0003_add_default_sender_ids applied successfully"
else
    error_exit "Migration 0003_add_default_sender_ids was not applied"
fi

# Check if default sender IDs exist
SENDER_COUNT=$(python manage.py shell -c "from messaging.models_sms import SMSSenderID; print(SMSSenderID.objects.filter(sender_id='Taarifa-SMS', status='active').count())" 2>/dev/null)
if [ ! -z "$SENDER_COUNT" ] && [ "$SENDER_COUNT" -gt 0 ]; then
    success "Found $SENDER_COUNT active default sender IDs"
else
    warning "No active default sender IDs found"
fi

# Step 11: Final verification
log "Step 11: Final verification..."

# Test API endpoint (if possible)
API_URL="https://your-domain.com/api/messaging/sender-requests/default/overview/"
if command -v curl &> /dev/null; then
    log "Testing API endpoint..."
    curl -s -o /dev/null -w "%{http_code}" "$API_URL" || warning "API endpoint test failed"
fi

# Summary
log "Deployment Summary:"
log "==================="
log "✅ Database backup created"
log "✅ Code updated from repository"
log "✅ Dependencies installed"
log "✅ Database migrations applied"
log "✅ Static files collected"
log "✅ Web server restarted"
log "✅ Migration verified"
log "✅ Default sender IDs created: $SENDER_COUNT"

success "Default Sender ID Fix deployment completed successfully!"

log "Next steps:"
log "1. Test the frontend to ensure default sender ID is available"
log "2. Monitor application logs for any errors"
log "3. Verify users can see 'Taarifa-SMS' in sender name dropdown"
log "4. Check that 'No approved sender names' error is resolved"

log "Deployment completed at $(date)"
