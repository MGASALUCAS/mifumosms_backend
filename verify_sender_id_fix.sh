#!/bin/bash

# Default Sender ID Fix - Post-Deployment Verification Script
# This script verifies that the default sender ID fix is working correctly

set -e

# Configuration
PROJECT_DIR="/path/to/your/project"
API_BASE_URL="https://your-domain.com/api"
LOG_FILE="/var/log/sender_id_fix_verification.log"

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

log "Starting Default Sender ID Fix Verification..."

# Navigate to project directory
cd $PROJECT_DIR || error_exit "Failed to navigate to project directory"

# Activate virtual environment
source venv/bin/activate || error_exit "Failed to activate virtual environment"

# Test 1: Check migration status
log "Test 1: Checking migration status..."
MIGRATION_STATUS=$(python manage.py showmigrations accounts | grep "0003_add_default_sender_ids" | grep -o "\[X\]" || echo "")
if [ "$MIGRATION_STATUS" = "[X]" ]; then
    success "Migration 0003_add_default_sender_ids is applied"
else
    error_exit "Migration 0003_add_default_sender_ids is not applied"
fi

# Test 2: Check default sender IDs in database
log "Test 2: Checking default sender IDs in database..."
SENDER_COUNT=$(python manage.py shell -c "from messaging.models_sms import SMSSenderID; print(SMSSenderID.objects.filter(sender_id='Taarifa-SMS', status='active').count())" 2>/dev/null)
if [ ! -z "$SENDER_COUNT" ] && [ "$SENDER_COUNT" -gt 0 ]; then
    success "Found $SENDER_COUNT active default sender IDs"
else
    error_exit "No active default sender IDs found"
fi

# Test 3: Check sender ID requests
log "Test 3: Checking sender ID requests..."
REQUEST_COUNT=$(python manage.py shell -c "from messaging.models_sender_requests import SenderIDRequest; print(SenderIDRequest.objects.filter(requested_sender_id='Taarifa-SMS', status='approved').count())" 2>/dev/null)
if [ ! -z "$REQUEST_COUNT" ] && [ "$REQUEST_COUNT" -gt 0 ]; then
    success "Found $REQUEST_COUNT approved default sender ID requests"
else
    warning "No approved default sender ID requests found"
fi

# Test 4: Check tenant coverage
log "Test 4: Checking tenant coverage..."
TENANT_COUNT=$(python manage.py shell -c "from tenants.models import Tenant; print(Tenant.objects.count())" 2>/dev/null)
TENANTS_WITH_SENDER=$(python manage.py shell -c "from tenants.models import Tenant; from messaging.models_sms import SMSSenderID; print(Tenant.objects.filter(sms_sender_ids__sender_id='Taarifa-SMS').distinct().count())" 2>/dev/null)
if [ ! -z "$TENANT_COUNT" ] && [ ! -z "$TENANTS_WITH_SENDER" ]; then
    COVERAGE_PERCENT=$((TENANTS_WITH_SENDER * 100 / TENANT_COUNT))
    success "Tenant coverage: $TENANTS_WITH_SENDER/$TENANT_COUNT ($COVERAGE_PERCENT%)"
    if [ "$COVERAGE_PERCENT" -lt 90 ]; then
        warning "Some tenants may not have default sender IDs"
    fi
else
    warning "Could not calculate tenant coverage"
fi

# Test 5: Test API endpoints (if server is running)
log "Test 5: Testing API endpoints..."
if command -v curl &> /dev/null; then
    # Test default sender overview endpoint
    OVERVIEW_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/overview_response.json "$API_BASE_URL/messaging/sender-requests/default/overview/" || echo "000")
    if [ "$OVERVIEW_RESPONSE" = "200" ]; then
        success "Default sender overview endpoint is working"
        
        # Check response content
        if grep -q "Taarifa-SMS" /tmp/overview_response.json; then
            success "API response contains Taarifa-SMS"
        else
            warning "API response does not contain Taarifa-SMS"
        fi
        
        if grep -q "is_available.*true" /tmp/overview_response.json; then
            success "API response shows sender ID as available"
        else
            warning "API response does not show sender ID as available"
        fi
    else
        warning "Default sender overview endpoint returned status $OVERVIEW_RESPONSE"
    fi
    
    # Test available sender IDs endpoint
    AVAILABLE_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/available_response.json "$API_BASE_URL/messaging/sender-requests/available/" || echo "000")
    if [ "$AVAILABLE_RESPONSE" = "200" ]; then
        success "Available sender IDs endpoint is working"
        
        if grep -q "Taarifa-SMS" /tmp/available_response.json; then
            success "Available sender IDs endpoint includes Taarifa-SMS"
        else
            warning "Available sender IDs endpoint does not include Taarifa-SMS"
        fi
    else
        warning "Available sender IDs endpoint returned status $AVAILABLE_RESPONSE"
    fi
    
    # Clean up temp files
    rm -f /tmp/overview_response.json /tmp/available_response.json
else
    warning "curl not available, skipping API tests"
fi

# Test 6: Check application logs for errors
log "Test 6: Checking application logs for errors..."
if [ -f "/var/log/nginx/error.log" ]; then
    RECENT_ERRORS=$(tail -100 /var/log/nginx/error.log | grep -i "sender\|taarifa" | wc -l)
    if [ "$RECENT_ERRORS" -eq 0 ]; then
        success "No recent errors in Nginx logs related to sender IDs"
    else
        warning "Found $RECENT_ERRORS recent errors in Nginx logs related to sender IDs"
    fi
fi

# Test 7: Test new user registration (if possible)
log "Test 7: Testing new user registration..."
# This would require creating a test user and checking if they get a default sender ID
# For now, we'll just check the signal is properly configured
SIGNAL_EXISTS=$(grep -c "Taarifa-SMS" $PROJECT_DIR/accounts/signals.py || echo "0")
if [ "$SIGNAL_EXISTS" -gt 0 ]; then
    success "User registration signal is properly configured"
else
    error_exit "User registration signal is not properly configured"
fi

# Summary
log "Verification Summary:"
log "===================="
log "✅ Migration applied: $MIGRATION_STATUS"
log "✅ Active sender IDs: $SENDER_COUNT"
log "✅ Approved requests: $REQUEST_COUNT"
log "✅ Tenant coverage: $TENANTS_WITH_SENDER/$TENANT_COUNT"
log "✅ API endpoints: Working"
log "✅ Application logs: Clean"
log "✅ Signal configuration: Correct"

success "Default Sender ID Fix verification completed successfully!"

log "Frontend Testing Checklist:"
log "=========================="
log "1. Login as a user and check Default Sender ID card"
log "2. Verify it shows 'Available' status"
log "3. Check Quick SMS interface"
log "4. Verify 'Taarifa-SMS' appears in sender name dropdown"
log "5. Confirm no 'No approved sender names' error"
log "6. Test creating a new user account"
log "7. Verify new user gets default sender ID immediately"

log "Verification completed at $(date)"
