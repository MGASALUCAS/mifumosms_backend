# API Key Endpoint 404 Fix

## Issue
The frontend is getting a 404 error when trying to POST to:
```
https://mifumosms.servehttp.com/api/auth/keys/create/
```

## Root Cause
The endpoint IS correctly registered in the code but the production server needs to be restarted to pick up the changes.

## Solution

### Step 1: Verify the Endpoint Exists

The endpoint is registered at:
- **Path**: `/api/auth/keys/create/`
- **Method**: `POST`
- **Function**: `accounts.settings_api.create_api_key`
- **Authentication**: Required (JWT Bearer token)

### Step 2: Deploy to Production Server

SSH into your production server and run:

```bash
# SSH into the server
ssh user@mifumosms.servehttp.com

# Navigate to project directory
cd /path/to/mifumosms_backend

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Run migrations (if any)
python manage.py migrate

# Restart the server
# For systemd (gunicorn)
sudo systemctl restart gunicorn

# Or if using supervisor
sudo supervisorctl restart mifumo

# Or if manually running
pkill -f "gunicorn"
gunicorn mifumo.wsgi:application --bind 0.0.0.0:8000
```

### Step 3: Test the Endpoint

Test the endpoint using curl:

```bash
curl -X POST https://mifumosms.servehttp.com/api/auth/keys/create/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key_name": "Test API Key"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "API key created successfully",
  "data": {
    "id": "uuid-here",
    "key_name": "Test API Key",
    "api_key": "generated-key",
    "secret_key": "generated-secret",
    "permissions": ["read", "write"],
    "created_at": "2025-01-XX...",
    "expires_at": null
  }
}
```

## API Documentation

### Create API Key Endpoint

**URL**: `POST /api/auth/keys/create/`

**Headers**:
```json
{
  "Authorization": "Bearer <your_jwt_token>",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "key_name": "My API Key",
  "permissions": ["read", "write"],  // optional, default: ["read", "write"]
  "expires_at": "2025-12-31T23:59:59Z"  // optional
}
```

**Success Response** (201):
```json
{
  "success": true,
  "message": "API key created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "key_name": "My API Key",
    "api_key": "mf_live_abc123...",
    "secret_key": "mf_live_xyz789...",
    "permissions": ["read", "write"],
    "created_at": "2025-01-20T10:30:00.000Z",
    "expires_at": null
  }
}
```

**Error Response** (400):
```json
{
  "success": false,
  "message": "Key name is required",
  "error_code": "MISSING_KEY_NAME"
}
```

## Related Endpoints

- `GET /api/auth/settings/` - Get API settings including keys
- `POST /api/auth/keys/<key_id>/revoke/` - Revoke an API key
- `POST /api/auth/keys/<key_id>/regenerate/` - Regenerate API key credentials
- `GET /api/auth/usage/` - Get API usage statistics

## Implementation Details

The endpoint is implemented in:
- **File**: `accounts/settings_api.py`
- **Function**: `create_api_key()`
- **View**: `@api_view(['POST'])` with `@permission_classes([IsAuthenticated])`

The function:
1. Validates the key name
2. Gets or creates an API account for the user
3. Creates the API key with generated credentials
4. Returns the key details (including secret key - only shown once!)

## Frontend Integration

Update your frontend to use the correct endpoint:

```javascript
const createAPIKey = async (keyName) => {
  const response = await fetch('https://mifumosms.servehttp.com/api/auth/keys/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      key_name: keyName
    })
  });
  
  const data = await response.json();
  return data;
};
```

## Quick Deployment Checklist

- [ ] SSH into production server
- [ ] Pull latest code changes
- [ ] Run database migrations
- [ ] Restart Gunicorn/supervisor
- [ ] Test endpoint with curl
- [ ] Verify frontend can access endpoint
- [ ] Monitor server logs for errors


