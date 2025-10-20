# Default Sender ID Frontend Integration Guide

## Overview
This guide provides complete API documentation for implementing the default sender ID request feature in your frontend. Users can request to use the default sender ID "Taarifa-SMS" and will be guided to purchase SMS credits after approval.

## API Endpoints

### 1. Get Default Sender Overview
**GET** `/api/messaging/sender-requests/default/overview/`

**Description:** Frontend-friendly endpoint that returns the current state of default sender ID requests and provides action URLs.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response (Success - Can Request):**
```json
{
  "success": true,
  "data": {
    "default_sender": "Taarifa-SMS",
    "current_sender_id": null,
    "active_request": null,
    "can_request": true,
    "reason": null,
    "balance": {
      "credits": 0,
      "needs_purchase": true
    },
    "actions": {
      "request_default_url": "/api/messaging/sender-requests/request-default/",
      "status_url": "/api/messaging/sender-requests/status/",
      "available_url": "/api/messaging/sender-requests/available/",
      "purchase_url": "/api/billing/sms/purchase/"
    }
  }
}
```

**Response (Already Requested/Approved):**
```json
{
  "success": true,
  "data": {
    "default_sender": "Taarifa-SMS",
    "current_sender_id": "Taarifa-SMS",
    "active_request": {
      "id": "7a1d2b5e-7c84-4a0b-8a8e-7f7b9d6a1234",
      "requested_sender_id": "Taarifa-SMS",
      "request_type": "default",
      "status": "approved",
      "sample_content": "A test use case for the sender name purposely used for information transfer.",
      "created_at": "2025-10-20T08:16:32.520Z"
    },
    "can_request": false,
    "reason": "Default sender already attached.",
    "balance": {
      "credits": 2000,
      "needs_purchase": false
    },
    "actions": {
      "request_default_url": "/api/messaging/sender-requests/request-default/",
      "status_url": "/api/messaging/sender-requests/status/",
      "available_url": "/api/messaging/sender-requests/available/",
      "purchase_url": "/api/billing/sms/purchase/"
    }
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "User is not associated with any tenant"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - User not associated with tenant
- `401 Unauthorized` - Invalid or missing token

---

### 2. Request Default Sender ID
**POST** `/api/messaging/sender-requests/request-default/`

**Description:** Creates a request for the default sender ID "Taarifa-SMS". This request is automatically approved.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{}
```

**Response (Success):**
```json
{
  "message": "Default sender ID request approved and created successfully",
  "sender_id_request": {
    "id": "0b89b2e3-0e2f-4f41-9b1f-4e8c2f7c9abc",
    "requested_sender_id": "Taarifa-SMS",
    "request_type": "default",
    "status": "approved",
    "sample_content": "A test use case for the sender name purposely used for information transfer.",
    "created_at": "2025-10-20T08:18:41.102Z"
  }
}
```

**Response (Duplicate Request):**
```json
{
  "error": "A request for the default sender ID already exists"
}
```

**Response (Error):**
```json
{
  "error": "No tenant found for this user"
}
```

**Status Codes:**
- `201 Created` - Request created and approved successfully
- `400 Bad Request` - Duplicate request or validation error
- `401 Unauthorized` - Invalid or missing token

---

### 3. Get Sender ID Request Status
**GET** `/api/messaging/sender-requests/status/`

**Description:** Returns the status of all sender ID requests for the current tenant.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response:**
```json
{
  "sms_balance": {
    "credits": 2000,
    "total_purchased": 5000,
    "can_request_sender_id": true
  },
  "sender_id_requests": [
    {
      "id": "0b89b2e3-0e2f-4f41-9b1f-4e8c2f7c9abc",
      "requested_sender_id": "Taarifa-SMS",
      "request_type": "default",
      "status": "approved",
      "sample_content": "A test use case for the sender name purposely used for information transfer.",
      "created_at": "2025-10-20T08:18:41.102Z"
    }
  ]
}
```

---

### 4. Get Available Sender IDs
**GET** `/api/messaging/sender-requests/available/`

**Description:** Returns all approved sender IDs that can be used by the tenant.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response:**
```json
{
  "available_sender_ids": [
    {
      "id": "0b89b2e3-0e2f-4f41-9b1f-4e8c2f7c9abc",
      "requested_sender_id": "Taarifa-SMS",
      "sample_content": "A test use case for the sender name purposely used for information transfer."
    }
  ]
}
```

---

## Frontend Implementation Flow

### 1. Initial Load
```javascript
// Get overview to determine what to show
const response = await fetch('/api/messaging/sender-requests/default/overview/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
```

### 2. Show Appropriate UI
Based on the response:

**If `can_request` is true:**
- Show "Request Default Sender ID" button
- Display current balance and purchase hint if `needs_purchase` is true

**If `can_request` is false:**
- Show current status from `active_request.status`
- Display reason from `reason` field
- Show "Refresh Status" button

### 3. Handle Request Action
```javascript
// When user clicks "Request Default Sender ID"
const response = await fetch('/api/messaging/sender-requests/request-default/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({})
});

const result = await response.json();
if (result.message) {
  // Success - refresh overview
  await loadOverview();
} else {
  // Error - show error message
  showError(result.error);
}
```

### 4. Handle Post-Approval Flow
After successful request:
1. Refresh overview to get updated status
2. If `balance.needs_purchase` is true, guide user to purchase SMS credits
3. Use `actions.purchase_url` for the purchase link

---

## Response Field Descriptions

### Overview Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `default_sender` | string | The default sender ID name ("Taarifa-SMS") |
| `current_sender_id` | string\|null | Currently active sender ID, null if none |
| `active_request` | object\|null | Latest request for default sender, null if none |
| `can_request` | boolean | Whether user can request default sender |
| `reason` | string\|null | Reason why `can_request` is false, null if can request |
| `balance.credits` | number | Current SMS credits available |
| `balance.needs_purchase` | boolean | Whether user needs to buy more credits |
| `actions.request_default_url` | string | URL to request default sender |
| `actions.status_url` | string | URL to check request status |
| `actions.available_url` | string | URL to get available sender IDs |
| `actions.purchase_url` | string | URL to purchase SMS credits |

### Request Status Values

| Status | Description |
|--------|-------------|
| `pending` | Request submitted, awaiting approval |
| `approved` | Request approved, sender ID available |
| `rejected` | Request rejected |
| `requires_changes` | Request needs modifications |
| `cancelled` | Request cancelled by user |

---

## Error Handling

### Common Error Scenarios

1. **User not associated with tenant:**
   ```json
   {
     "success": false,
     "message": "User is not associated with any tenant"
   }
   ```

2. **Duplicate request:**
   ```json
   {
     "error": "A request for the default sender ID already exists"
   }
   ```

3. **Authentication required:**
   ```json
   {
     "detail": "Authentication credentials were not provided."
   }
   ```

### Frontend Error Handling
```javascript
try {
  const response = await fetch('/api/messaging/sender-requests/default/overview/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      // Redirect to login
      redirectToLogin();
    } else if (response.status === 400) {
      // Show user-friendly error
      const error = await response.json();
      showError(error.message || 'Request failed');
    }
  }
  
  const data = await response.json();
  // Handle success...
  
} catch (error) {
  // Network error
  showError('Network error. Please try again.');
}
```

---

## Testing

### Test Scenarios

1. **New User (No Requests):**
   - `can_request` should be `true`
   - `active_request` should be `null`
   - `current_sender_id` should be `null`

2. **After Request:**
   - `can_request` should be `false`
   - `active_request.status` should be `approved`
   - `reason` should explain why can't request

3. **With Credits:**
   - `balance.needs_purchase` should be `false`
   - `balance.credits` should show available credits

4. **Without Credits:**
   - `balance.needs_purchase` should be `true`
   - `balance.credits` should be 0 or low

---

## Integration Checklist

- [ ] Implement overview endpoint call
- [ ] Handle `can_request` logic in UI
- [ ] Implement request action
- [ ] Handle post-request refresh
- [ ] Show purchase guidance when needed
- [ ] Implement error handling
- [ ] Test all scenarios
- [ ] Add loading states
- [ ] Add success/error notifications

---

## Notes

- Default sender ID requests are **automatically approved**
- Users must purchase SMS credits to actually send messages
- The system prevents duplicate requests for the same sender ID
- All endpoints require authentication
- Responses include helpful action URLs for frontend navigation

