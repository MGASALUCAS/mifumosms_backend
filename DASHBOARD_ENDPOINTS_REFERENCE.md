# Dashboard API Endpoints Reference

## Base URL
```
https://104.131.116.55/api/messaging/
```

## Authentication
All endpoints require JWT authentication:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## 1. Dashboard Metrics Overview

**Endpoint:** `GET /api/messaging/dashboard/metrics/`

**Description:** Get key performance indicators for dashboard cards

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "totalMessages": {
      "value": 2,
      "period": "Last 30 days"
    },
    "activeContacts": {
      "value": 1,
      "period": "Engaged this month"
    },
    "campaignSuccess": {
      "value": 98.0,
      "unit": "%",
      "description": "Delivery rate"
    },
    "senderId": {
      "value": 0,
      "description": "Approved sender names"
    }
  }
}
```

### Error Response (500)
```json
{
  "success": false,
  "message": "Failed to retrieve dashboard metrics.",
  "code": 500,
  "details": "An unexpected error occurred on the server."
}
```

---

## 2. Recent Campaigns

**Endpoint:** `GET /api/messaging/campaigns/summary/`

**Description:** Get recent campaigns for dashboard display

### Success Response (200)
```json
{
  "success": true,
  "summary": {
    "recent_campaigns": [
      {
        "id": "campaign_welcome_123",
        "name": "Welcome Campaign",
        "type": "WhatsApp",
        "status": "Completed",
        "timeAgo": "18 minutes ago",
        "sent": 100,
        "delivered": 98
      }
    ]
  }
}
```

### Error Response (404)
```json
{
  "success": false,
  "message": "Could not fetch recent campaigns.",
  "code": 404,
  "details": "No campaigns found or an issue with the campaign service."
}
```

---

## 3. Recent Activity

**Endpoint:** `GET /api/messaging/activity/recent/`

**Description:** Get recent activity feed for dashboard

### Query Parameters
- `limit` (optional): Number of activities to return (default: 10)

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "activity_reply_001",
        "type": "reply",
        "actor": "John Kamau",
        "action": "replied to conversation",
        "target": "Kenya Coffee Exports",
        "timeAgo": "2 min ago",
        "isLive": true
      },
      {
        "id": "activity_campaign_002",
        "type": "campaign_completion",
        "actor": "System",
        "action": "completed campaign",
        "target": "Mother's Day Promotion",
        "deliveryRate": "98% delivered",
        "timeAgo": "15 min ago"
      },
      {
        "id": "activity_contacts_003",
        "type": "contacts_added",
        "actor": "Sarah Mwangi",
        "action": "added 25 new contacts",
        "target": "Nairobi SME List",
        "timeAgo": "1 hour ago"
      },
      {
        "id": "activity_template_004",
        "type": "template_approval",
        "actor": "David Ochieng",
        "action": "approved template",
        "target": "Welcome Message - Swahili",
        "timeAgo": "2 hours ago"
      }
    ],
    "has_more": true,
    "total_count": 4,
    "live_count": 1
  }
}
```

### Error Response (403)
```json
{
  "success": false,
  "message": "Failed to load recent activity feed.",
  "code": 403,
  "details": "User does not have permission to view activity."
}
```

---

## 4. Quick Actions (POST Endpoints)

### Send Message
**Endpoint:** `POST /api/messaging/messages/`

**Success Response (201)**
```json
{
  "success": true,
  "message": "Message sent successfully.",
  "data": {
    "messageId": "msg_xyz_789",
    "status": "queued"
  }
}
```

**Error Response (400)**
```json
{
  "success": false,
  "message": "Failed to send message.",
  "code": 400,
  "details": "Recipient number is invalid or message content is too long."
}
```

### Add New Campaign
**Endpoint:** `POST /api/messaging/campaigns/`

**Success Response (201)**
```json
{
  "success": true,
  "message": "Campaign created successfully.",
  "data": {
    "campaignId": "campaign_abc_123",
    "status": "draft"
  }
}
```

**Error Response (400)**
```json
{
  "success": false,
  "message": "Failed to create campaign.",
  "code": 400,
  "details": "Invalid campaign data or missing required fields."
}
```

### Add Contacts
**Endpoint:** `POST /api/messaging/contacts/bulk-import/`

**Success Response (201)**
```json
{
  "success": true,
  "message": "Contacts imported successfully.",
  "data": {
    "importId": "import_xyz_456",
    "totalContacts": 25,
    "status": "processing"
  }
}
```

**Error Response (400)**
```json
{
  "success": false,
  "message": "Failed to import contacts.",
  "code": 400,
  "details": "Invalid CSV format or missing required contact fields."
}
```

### Create Template
**Endpoint:** `POST /api/messaging/templates/`

**Success Response (201)**
```json
{
  "success": true,
  "message": "Template created successfully.",
  "data": {
    "templateId": "template_def_789",
    "status": "pending_approval"
  }
}
```

**Error Response (400)**
```json
{
  "success": false,
  "message": "Failed to create template.",
  "code": 400,
  "details": "Template content violates guidelines or missing required fields."
}
```

---

## 5. Performance Overview

**Endpoint:** `GET /api/messaging/performance/overview/`

**Description:** Get performance analytics (currently placeholder)

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "message": "Analytics charts coming soon.",
    "status": "placeholder"
  }
}
```

---

## General Error Response Structure

All error responses follow this format:
```json
{
  "success": false,
  "message": "A concise, human-readable error description.",
  "code": 400,
  "details": "Optional: More specific technical details or validation errors."
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
