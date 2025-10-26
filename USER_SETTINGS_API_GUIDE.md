# User Settings API Guide

## Overview
The User Settings API allows authenticated users to manage their API keys and webhooks after normal registration. This is designed for users who have registered through the standard registration process and want to access API functionality.

## Authentication
All endpoints require JWT authentication. Users must login first to get an access token:

```bash
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "password123"
}
```

Use the returned `access` token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## API Endpoints

### 1. Get API Settings
**GET** `/api/integration/user/settings/`

Retrieve user's API account, keys, and webhooks.

**Response:**
```json
{
    "success": true,
    "message": "API settings retrieved successfully",
    "data": {
        "api_account": {
            "id": "uuid",
            "name": "My API Account",
            "description": "Personal API account",
            "created_at": "2024-01-01T10:00:00Z"
        },
        "api_keys": [
            {
                "id": "uuid",
                "key_name": "My Production Key",
                "api_key": "mif_abc123...",
                "secret_key": "secret123...",
                "permissions": ["read", "write"],
                "status": "active",
                "total_uses": 0,
                "last_used": null,
                "created_at": "2024-01-01T10:00:00Z",
                "expires_at": null,
                "is_active": true
            }
        ],
        "webhooks": [
            {
                "id": "uuid",
                "url": "https://myapp.com/webhooks/mifumo",
                "events": ["message.sent", "message.delivered"],
                "is_active": true,
                "created_at": "2024-01-01T10:00:00Z",
                "last_triggered": null
            }
        ]
    }
}
```

### 2. Get Usage Statistics
**GET** `/api/integration/user/usage/`

Get API usage statistics for the user.

**Response:**
```json
{
    "success": true,
    "message": "API usage statistics retrieved successfully",
    "data": {
        "api_keys": {
            "total": 2,
            "active": 1
        },
        "webhooks": {
            "total": 1,
            "active": 1
        },
        "api_calls": {
            "total": 150
        },
        "account_created": "2024-01-01T10:00:00Z"
    }
}
```

### 3. Create API Key
**POST** `/api/integration/user/keys/create/`

Create a new API key for the user.

**Request Body:**
```json
{
    "key_name": "My Production Key",
    "permissions": ["read", "write"],
    "expires_at": null
}
```

**Response:**
```json
{
    "success": true,
    "message": "API key created successfully",
    "data": {
        "id": "uuid",
        "key_name": "My Production Key",
        "api_key": "mif_abc123...",
        "secret_key": "secret123...",
        "permissions": ["read", "write"],
        "created_at": "2024-01-01T10:00:00Z",
        "expires_at": null
    }
}
```

### 4. Revoke API Key
**POST** `/api/integration/user/keys/{key_id}/revoke/`

Revoke an API key.

**Response:**
```json
{
    "success": true,
    "message": "API key revoked successfully"
}
```

### 5. Regenerate API Key
**POST** `/api/integration/user/keys/{key_id}/regenerate/`

Generate new credentials for an existing API key.

**Response:**
```json
{
    "success": true,
    "message": "API key regenerated successfully",
    "data": {
        "api_key": "mif_new123...",
        "secret_key": "new_secret123..."
    }
}
```

### 6. Create Webhook
**POST** `/api/integration/user/webhooks/create/`

Create a new webhook for receiving notifications.

**Request Body:**
```json
{
    "url": "https://myapp.com/webhooks/mifumo",
    "events": ["message.sent", "message.delivered", "message.failed"]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Webhook created successfully",
    "data": {
        "id": "uuid",
        "url": "https://myapp.com/webhooks/mifumo",
        "events": ["message.sent", "message.delivered", "message.failed"],
        "is_active": true,
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

### 7. Toggle Webhook
**POST** `/api/integration/user/webhooks/{webhook_id}/toggle/`

Toggle webhook active status.

**Response:**
```json
{
    "success": true,
    "message": "Webhook activated successfully",
    "data": {
        "is_active": true
    }
}
```

### 8. Delete Webhook
**DELETE** `/api/integration/user/webhooks/{webhook_id}/delete/`

Delete a webhook.

**Response:**
```json
{
    "success": true,
    "message": "Webhook deleted successfully"
}
```

## Using API Keys

Once you have created an API key, you can use it to access the SMS API:

```bash
# Send SMS
curl -X POST "http://127.0.0.1:8001/api/integration/v1/test-sms/send/" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from API!",
    "recipients": ["+255757347863"],
    "sender_id": "MIFUMO"
  }'
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "error_code": "ERROR_CODE",
    "details": "Additional error details"
}
```

## Common Error Codes

- `AUTHENTICATION_REQUIRED` - Missing or invalid authentication
- `MISSING_KEY_NAME` - Key name is required
- `MISSING_WEBHOOK_URL` - Webhook URL is required
- `MISSING_WEBHOOK_EVENTS` - At least one event must be selected
- `CREATE_KEY_ERROR` - Failed to create API key
- `REVOKE_KEY_ERROR` - Failed to revoke API key
- `REGENERATE_KEY_ERROR` - Failed to regenerate API key
- `CREATE_WEBHOOK_ERROR` - Failed to create webhook
- `TOGGLE_WEBHOOK_ERROR` - Failed to toggle webhook
- `DELETE_WEBHOOK_ERROR` - Failed to delete webhook

## Example Usage Flow

1. **Register/Login** - User registers normally or logs in
2. **Get Settings** - Check existing API keys and webhooks
3. **Create API Key** - Generate new API key for SMS access
4. **Use API Key** - Send SMS using the generated API key
5. **Create Webhook** - Set up webhook for delivery notifications
6. **Monitor Usage** - Check usage statistics and manage keys

## Testing

Run the test script to see the complete flow:

```bash
python test_user_settings_api.py
```

This will demonstrate:
- User authentication
- API settings retrieval
- API key creation
- SMS sending with the new key
- Webhook creation
- Usage statistics
- Key management operations

