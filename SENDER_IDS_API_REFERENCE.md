# Sender IDs API Reference

## Overview
This document provides the complete API endpoints and JSON responses for managing and viewing accepted sender IDs in the Mifumo WMS system.

## Base URL
```
http://127.0.0.1:8001/api/messaging/
```

## Authentication
All endpoints require JWT authentication:
```javascript
headers: {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
}
```

---

## 1. Get Accepted Sender IDs

**Endpoint:** `GET /api/messaging/sender-ids/`

**Purpose:** Get list of active/accepted sender IDs for the current tenant

### Success Response (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "174f79cc-f1c8-4784-a139-49ab317a5f64",
      "sender_id": "Taarifa-SMS",
      "sample_content": "A test use case for the sender name purposely used for information transfer.",
      "status": "active",
      "created_at": "2025-10-22T20:02:35.010387+00:00",
      "updated_at": "2025-10-22T20:02:35.010472+00:00"
    },
    {
      "id": "ac6f9f83-4713-436b-838a-1dc685424a9d",
      "sender_id": "MIFUMO",
      "sample_content": "Welcome to Mifumo WMS! Your SMS messaging solution.",
      "status": "active",
      "created_at": "2025-10-22T20:00:42.584116+00:00",
      "updated_at": "2025-10-22T20:00:42.584227+00:00"
    }
  ]
}
```

### Error Response (400):
```json
{
  "success": false,
  "message": "User is not associated with any tenant"
}
```

---

## 2. Get Available Sender IDs

**Endpoint:** `GET /api/messaging/sender-requests/available/`

**Purpose:** Get available sender IDs including approved requests and provider data

### Success Response (200):
```json
{
  "available_sender_ids": [
    {
      "requested_sender_id": "Taarifa-SMS",
      "sample_content": "A test use case for the sender name purposely used for information transfer."
    },
    {
      "requested_sender_id": "MIFUMO",
      "sample_content": "Welcome to Mifumo WMS! Your SMS messaging solution."
    }
  ],
  "provider": {
    "name": "Beem Africa",
    "active_sender_ids": []
  }
}
```

---

## 3. Get Sender ID Statistics

**Endpoint:** `GET /api/messaging/sender-requests/stats/`

**Purpose:** Get sender ID request statistics and recent requests

### Success Response (200):
```json
{
  "success": true,
  "data": {
    "stats": {
      "total_requests": 3,
      "pending_requests": 0,
      "approved_requests": 3,
      "rejected_requests": 0,
      "requires_changes_requests": 0
    },
    "request_stats": {
      "total_requests": 1,
      "pending_requests": 0,
      "approved_requests": 1,
      "rejected_requests": 0,
      "requires_changes_requests": 0
    },
    "active_stats": {
      "total_active": 2,
      "active_sender_ids": [
        {
          "id": "174f79cc-f1c8-4784-a139-49ab317a5f64",
          "sender_id": "Taarifa-SMS",
          "status": "active",
          "created_at": "2025-10-22T20:02:35.010387Z"
        },
        {
          "id": "ac6f9f83-4713-436b-838a-1dc685424a9d",
          "sender_id": "MIFUMO",
          "status": "active",
          "created_at": "2025-10-22T20:00:42.584116Z"
        }
      ]
    },
    "recent_requests": [
      {
        "id": "ca80f38d-51f1-4173-84f9-e3b963be71d5",
        "requested_sender_id": "Taarifa-SMS",
        "status": "approved",
        "sample_content": "A test use case for the sender name purposely used for information transfer.",
        "created_at": "2025-10-22T22:51:59.116188+03:00",
        "reviewed_at": "2025-10-22T22:56:06.314954+03:00"
      }
    ]
  }
}
```

---

## Frontend Integration Examples

### JavaScript/React Example:
```javascript
// Fetch accepted sender IDs
async function fetchSenderIds(token) {
  try {
    const response = await fetch('http://127.0.0.1:8001/api/messaging/sender-ids/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Display sender IDs
      data.data.forEach(senderId => {
        console.log(`${senderId.sender_id} - ${senderId.status}`);
        console.log(`Sample: ${senderId.sample_content}`);
      });
      
      return data.data;
    } else {
      console.error('Error:', data.message);
      return [];
    }
  } catch (error) {
    console.error('Request failed:', error);
    return [];
  }
}

// Usage
const senderIds = await fetchSenderIds('your-jwt-token');
```

### Display in Dashboard:
```javascript
// Update dashboard with sender ID count
function updateDashboard(senderIds) {
  const senderIdCount = senderIds.length;
  document.getElementById('sender-id-count').textContent = senderIdCount;
  
  // Display sender ID list
  const senderIdList = document.getElementById('sender-id-list');
  senderIdList.innerHTML = '';
  
  senderIds.forEach(senderId => {
    const item = document.createElement('div');
    item.className = 'sender-id-item';
    item.innerHTML = `
      <strong>${senderId.sender_id}</strong>
      <span class="status ${senderId.status}">${senderId.status}</span>
      <p>${senderId.sample_content}</p>
    `;
    senderIdList.appendChild(item);
  });
}
```

---

## Data Structure Reference

### Sender ID Object:
```typescript
interface SenderID {
  id: string;                    // UUID
  sender_id: string;             // The actual sender ID name
  sample_content: string;        // Sample message content
  status: 'active' | 'inactive'; // Status
  created_at: string;            // ISO timestamp
  updated_at: string;            // ISO timestamp
}
```

### Statistics Object:
```typescript
interface SenderIDStats {
  stats: {
    total_requests: number;
    pending_requests: number;
    approved_requests: number;
    rejected_requests: number;
    requires_changes_requests: number;
  };
  active_stats: {
    total_active: number;
    active_sender_ids: SenderID[];
  };
  recent_requests: Array<{
    id: string;
    requested_sender_id: string;
    status: string;
    sample_content: string;
    created_at: string;
    reviewed_at: string;
  }>;
}
```

---

## Current Data in Your System

Based on the test results, you currently have:

- **2 Active Sender IDs:**
  - `Taarifa-SMS` - Default sender ID
  - `MIFUMO` - Custom sender ID

- **3 Total Approved Requests**
- **0 Pending Requests**
- **0 Rejected Requests**

The sender IDs are working correctly and ready for frontend integration!
