# API Endpoints Reference - Settings Page

## Base URL
```
http://127.0.0.1:8001/api/auth/
```

## Authentication
All endpoints require JWT Bearer Token:
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

---

## 1. Get API Settings (API Keys & Webhooks)

**Purpose:** Load all API keys and webhooks for the settings page

**Endpoint:** `GET /api/auth/settings/`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "API settings retrieved successfully.",
  "data": {
    "api_account": {
      "id": "uuid-of-api-account",
      "account_id": "ACC-XYZ123",
      "name": "My API Account",
      "status": "active",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z"
    },
    "api_keys": [
      {
        "id": "uuid-of-key-1",
        "key_name": "Production API Key",
        "api_key": "mif_********************************",
        "secret_key": "****************************************************************",
        "status": "active",
        "permissions": {
          "sms": ["read", "write"]
        },
        "total_uses": 1500,
        "last_used": "2024-07-20T14:30:00Z",
        "expires_at": "2026-12-31T23:59:59Z",
        "created_at": "2024-01-01T10:00:00Z"
      },
      {
        "id": "uuid-of-key-2",
        "key_name": "Development API Key",
        "api_key": "mif_********************************",
        "secret_key": "****************************************************************",
        "status": "active",
        "permissions": {
          "sms": ["read"]
        },
        "total_uses": 50,
        "last_used": "2024-07-19T10:00:00Z",
        "expires_at": null,
        "created_at": "2024-03-15T09:00:00Z"
      }
    ],
    "webhooks": [
      {
        "id": "uuid-of-webhook-1",
        "url": "https://myapp.com/webhooks/mifumo",
        "events": ["message.sent", "message.delivered", "message.failed"],
        "is_active": true,
        "total_calls": 120,
        "successful_calls": 118,
        "failed_calls": 2,
        "last_triggered": "2024-07-20T14:55:00Z",
        "last_error": "",
        "created_at": "2024-05-01T11:00:00Z"
      },
      {
        "id": "uuid-of-webhook-2",
        "url": "https://analytics.example.com/webhook",
        "events": ["campaign.completed"],
        "is_active": false,
        "total_calls": 5,
        "successful_calls": 5,
        "failed_calls": 0,
        "last_triggered": "2024-07-18T08:00:00Z",
        "last_error": "",
        "created_at": "2024-06-10T15:00:00Z"
      }
    ],
    "last_updated": "2024-07-20T15:00:00Z"
  }
}
```

---

## 2. Create New API Key

**Purpose:** "+ New Key" button functionality

**Endpoint:** `POST /api/auth/keys/create/`

**Request Body:**
```json
{
  "key_name": "My New API Key",
  "permissions": {
    "sms": ["send", "status", "balance"],
    "contacts": ["read"]
  },
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "API Key created successfully.",
  "data": {
    "id": "uuid-of-new-key",
    "key_name": "My New API Key",
    "api_key": "mif_YOUR_NEW_API_KEY_HERE",
    "secret_key": "YOUR_NEW_SECRET_KEY_HERE",
    "status": "active",
    "permissions": {
      "sms": ["send", "status", "balance"],
      "contacts": ["read"]
    },
    "total_uses": 0,
    "last_used": null,
    "expires_at": "2025-12-31T23:59:59Z",
    "created_at": "2024-07-20T15:05:00Z"
  }
}
```

---

## 3. Revoke API Key

**Purpose:** Three-dot menu "Revoke" option

**Endpoint:** `POST /api/auth/keys/{key_id}/revoke/`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "API Key revoked successfully.",
  "data": {
    "id": "uuid-of-revoked-key",
    "status": "revoked",
    "is_active": false
  }
}
```

---

## 4. Regenerate API Key

**Purpose:** Three-dot menu "Regenerate" option

**Endpoint:** `POST /api/auth/keys/{key_id}/regenerate/`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "API Key regenerated successfully.",
  "data": {
    "id": "uuid-of-regenerated-key",
    "key_name": "Production API Key",
    "api_key": "mif_YOUR_NEW_API_KEY_HERE",
    "secret_key": "YOUR_NEW_SECRET_KEY_HERE",
    "status": "active",
    "permissions": {
      "sms": ["read", "write"]
    },
    "last_used": null,
    "expires_at": "2026-12-31T23:59:59Z",
    "updated_at": "2024-07-20T15:10:00Z"
  }
}
```

---

## 5. Create New Webhook

**Purpose:** "+ Add Webhook" button functionality

**Endpoint:** `POST /api/auth/webhooks/create/`

**Request Body:**
```json
{
  "url": "https://your-domain.com/webhooks/mifumo",
  "events": ["message.sent", "message.delivered", "campaign.completed"],
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Webhook created successfully.",
  "data": {
    "id": "uuid-of-new-webhook",
    "url": "https://your-domain.com/webhooks/mifumo",
    "events": ["message.sent", "message.delivered", "campaign.completed"],
    "is_active": true,
    "total_calls": 0,
    "successful_calls": 0,
    "failed_calls": 0,
    "last_triggered": null,
    "last_error": "",
    "created_at": "2024-07-20T15:15:00Z"
  }
}
```

---

## 6. Toggle Webhook Status

**Purpose:** Three-dot menu "Toggle" option (Active/Inactive)

**Endpoint:** `POST /api/auth/webhooks/{webhook_id}/toggle/`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Webhook status toggled successfully.",
  "data": {
    "id": "uuid-of-webhook",
    "is_active": false
  }
}
```

---

## 7. Delete Webhook

**Purpose:** Three-dot menu "Delete" option

**Endpoint:** `DELETE /api/auth/webhooks/{webhook_id}/delete/`

**Response (204 No Content):**
```json
{
  "success": true,
  "message": "Webhook deleted successfully.",
  "data": null
}
```

---

## Error Responses

**Common Error Format:**
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": "Additional error details"
}
```

**Common Error Codes:**
- `AUTHENTICATION_REQUIRED` - User not logged in
- `INVALID_CREDENTIALS` - Invalid API key
- `MISSING_MESSAGE` - SMS message is required
- `INVALID_PHONE_FORMAT` - Phone number format is invalid
- `INSUFFICIENT_BALANCE` - Account needs to be topped up

---

## Frontend Implementation Notes

1. **Load Settings:** Call `GET /settings/` on page load
2. **API Keys:** Display with masked values, show full values only on creation/regeneration
3. **Webhooks:** Show status badges (Active/Inactive) and event tags
4. **Actions:** Implement three-dot menus for each API key and webhook
5. **Error Handling:** Show appropriate error messages for failed requests
6. **Real-time Updates:** Refresh data after create/update/delete operations