# Security Endpoints Implementation

## Overview

This document describes the security endpoints that have been implemented to fix the 404 errors from the frontend.

## Implemented Endpoints

All security endpoints are now available under `/api/auth/security/`:

### 1. Security Summary
**Endpoint:** `GET /api/auth/security/summary/`

Returns security overview including:
- `two_factor_enabled`: Whether 2FA is enabled
- `active_sessions`: Count of active sessions
- `recent_events_count`: Count of recent security events
- `last_password_change`: Last time password was changed
- `security_score`: Security score (0-100)

**Example Response:**
```json
{
  "success": true,
  "data": {
    "two_factor_enabled": false,
    "active_sessions": 1,
    "recent_events_count": 0,
    "last_password_change": "2025-01-23T10:30:00.000Z",
    "security_score": 50
  }
}
```

### 2. Two-Factor Authentication Status
**Endpoint:** `GET /api/auth/security/2fa/status/`

Returns current 2FA status for the user.

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "mock-2fa-id",
    "is_enabled": false,
    "created_at": "2025-01-23T10:30:00.000Z",
    "updated_at": "2025-01-23T10:30:00.000Z",
    "qr_code_data": null,
    "backup_codes": null
  }
}
```

### 3. Active Sessions
**Endpoint:** `GET /api/auth/security/sessions/`

Returns list of active sessions for the user.

**Example Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "current-session-id",
      "session_key": "current-session-key",
      "ip_address": "127.0.0.1",
      "device_name": "Unknown",
      "location": "Unknown",
      "is_active": true,
      "created_at": "2025-01-23T10:30:00.000Z",
      "last_activity": "2025-01-23T10:30:00.000Z",
      "expires_at": "2025-01-30T10:30:00.000Z",
      "is_current": true,
      "device_info": {
        "browser": "Unknown",
        "os": "Unknown",
        "device_type": "Unknown"
      },
      "time_ago": "Just now"
    }
  ],
  "total_count": 1
}
```

### 4. Security Events
**Endpoint:** `GET /api/auth/security/events/`

Returns security events history.

**Example Response:**
```json
{
  "success": true,
  "events": [],
  "total_count": 0,
  "has_more": false
}
```

### 5. Change Password
**Endpoint:** `POST /api/auth/security/change-password/`

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### 6. 2FA Endpoints (Not Yet Implemented)
The following endpoints return `501 Not Implemented` for now:
- `POST /api/auth/security/2fa/enable/`
- `POST /api/auth/security/2fa/disable/`
- `POST /api/auth/security/2fa/verify/`

### 7. Session Management
- `POST /api/auth/security/sessions/{session_id}/terminate/` - Terminate a specific session
- `POST /api/auth/security/sessions/terminate-all-others/` - Terminate all other sessions

## Frontend Configuration Fix

### Issue: Double `/api/api/` in URLs

The frontend is calling URLs like:
```
http://127.0.0.1:8000/api/api/auth/security/summary/
```

Notice the double `/api/api/` prefix. This should be:
```
http://127.0.0.1:8000/api/auth/security/summary/
```

### Fix Required in Frontend

Update the API base URL configuration in your frontend:

**Before (WRONG):**
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/api';  // ❌ Double /api/api/
```

**After (CORRECT):**
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';  // ✅ Single /api/
```

Or if you want to use relative paths:
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';  // From the backend
// And in your frontend requests, use:
fetch(`${API_BASE_URL}/auth/security/summary/`)
```

### Frontend File to Update

Look for where the API base URL is configured. Common locations:
- `config.js` or `config.ts`
- `.env` file
- `constants.js` or `constants.ts`
- `api.js` or `api.ts`

Search for:
```javascript
// Look for something like:
const API_BASE_URL = '...'
const BASE_URL = '...'
const API_URL = '...'
```

## Authentication

All endpoints require JWT authentication:
```http
Authorization: Bearer <your_jwt_token>
```

## Backend Files Changed

1. **Created:** `accounts/security_views.py` - New security endpoints
2. **Updated:** `accounts/urls.py` - Added security endpoint routes

## Testing

Test the endpoints with curl or Postman:

```bash
# Security Summary
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/auth/security/summary/

# 2FA Status
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/auth/security/2fa/status/

# Active Sessions
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/auth/security/sessions/

# Security Events
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/auth/security/events/
```

## Next Steps

1. Update frontend API base URL to remove double `/api/api/`
2. Test all security endpoints
3. Consider implementing full 2FA functionality
4. Consider implementing SecurityEvent and UserSession models for real data

## Notes

- Current implementation returns mock data for sessions and events
- 2FA endpoints return `501 Not Implemented` as they require additional models and logic
- Security score calculation is basic and can be enhanced
- Future implementation should include:
  - Real SecurityEvent model tracking
  - Real UserSession model management
  - Full 2FA with QR codes and TOTP
  - Real session termination functionality

