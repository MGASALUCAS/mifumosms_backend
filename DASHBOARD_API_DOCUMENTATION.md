# Dashboard API Documentation

## Overview
This document provides the complete API endpoints and JSON responses for the Dashboard metrics system.

---

## 🔗 Base URL
```
https://104.131.116.55/api/messaging/dashboard/
```

---

## 📊 Endpoints

### 1. Dashboard Overview
**Endpoint:** `GET /api/messaging/dashboard/overview/`

**Description:** Get comprehensive dashboard overview data with key metrics and recent activity.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Response:**
```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_messages": 1250,
      "total_sms_messages": 980,
      "active_contacts": 450,
      "campaign_success_rate": 94.2,
      "sms_delivery_rate": 96.8,
      "current_credits": 1500,
      "total_purchased": 5000,
      "sender_ids_this_month": 3
    },
    "recent_campaigns": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Welcome Campaign",
        "type": "SMS",
        "status": "completed",
        "sent": 150,
        "delivered": 145,
        "opened": 120,
        "progress": 100,
        "created_at": "2024-01-15 10:30:00",
        "created_at_human": "2 days ago"
      },
      {
        "id": "660f9511-f3ac-52e5-b827-557766551111",
        "name": "Promotional SMS",
        "type": "SMS",
        "status": "running",
        "sent": 75,
        "delivered": 72,
        "opened": 45,
        "progress": 50,
        "created_at": "2024-01-16 14:20:00",
        "created_at_human": "1 day ago"
      }
    ],
    "message_stats": {
      "today": 25,
      "this_week": 180,
      "this_month": 750,
      "growth_rate": 15.2
    },
    "sms_stats": {
      "today": 20,
      "this_month": 650,
      "delivery_rate": 96.8
    },
    "contact_stats": {
      "total": 500,
      "active": 450,
      "new_this_month": 25,
      "growth_rate": 5.6
    },
    "billing_stats": {
      "current_credits": 1500,
      "total_purchased": 5000,
      "credits_used": 3500
    },
    "last_updated": "2024-01-17T10:30:00Z"
  }
}
```

---

### 2. Dashboard Metrics
**Endpoint:** `GET /api/messaging/dashboard/metrics/`

**Description:** Get detailed metrics for dashboard cards with percentage changes and trends.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_messages": {
      "value": 750,
      "change": "+12.5%",
      "change_type": "positive",
      "description": "Last 30 days"
    },
    "sms_messages": {
      "value": 650,
      "change": "+8.2%",
      "change_type": "positive",
      "description": "SMS last 30 days"
    },
    "active_contacts": {
      "value": 450,
      "change": "+5.6%",
      "change_type": "positive",
      "description": "Engaged this month"
    },
    "campaign_success": {
      "value": "94.2%",
      "change": "+2.1%",
      "change_type": "positive",
      "description": "Delivery rate"
    },
    "sms_delivery_rate": {
      "value": "96.8%",
      "change": "+1.5%",
      "change_type": "positive",
      "description": "SMS delivery rate"
    },
    "current_credits": {
      "value": 1500,
      "change": "-15.2%",
      "change_type": "negative",
      "description": "Available credits"
    }
  }
}
```

---

### 3. Dashboard Comprehensive
**Endpoint:** `GET /api/messaging/dashboard/comprehensive/`

**Description:** Get complete dashboard data with all metrics, recent activity, and detailed breakdowns.

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_messages": 1250,
      "total_sms_messages": 980,
      "active_contacts": 450,
      "current_credits": 1500,
      "sms_delivery_rate": 96.8,
      "campaign_success_rate": 94.2
    },
    "metrics": {
      "messages": {
        "today": 25,
        "this_week": 180,
        "this_month": 750,
        "total": 1250
      },
      "sms": {
        "today": 20,
        "this_month": 650,
        "total": 980,
        "delivered": 950,
        "failed": 30,
        "delivery_rate": 96.8
      },
      "contacts": {
        "total": 500,
        "active": 450,
        "new_this_month": 25
      },
      "campaigns": {
        "total": 12,
        "completed": 8,
        "running": 2,
        "success_rate": 94.2
      },
      "billing": {
        "current_credits": 1500,
        "total_purchased": 5000,
        "credits_used": 3500
      }
    },
    "recent_activity": {
      "campaigns": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Welcome Campaign",
          "status": "completed",
          "sent": 150,
          "delivered": 145,
          "created_at": "2024-01-15 10:30:00",
          "created_at_human": "2 days ago"
        },
        {
          "id": "660f9511-f3ac-52e5-b827-557766551111",
          "name": "Promotional SMS",
          "status": "running",
          "sent": 75,
          "delivered": 72,
          "created_at": "2024-01-16 14:20:00",
          "created_at_human": "1 day ago"
        }
      ],
      "messages": [
        {
          "id": "770g0622-g4bd-63f6-c938-668877662222",
          "content": "Welcome to our service! We're excited to have you...",
          "direction": "out",
          "status": "delivered",
          "created_at": "2024-01-17 09:15:00",
          "created_at_human": "1 hour ago"
        },
        {
          "id": "880h1733-h5ce-74g7-d049-779988773333",
          "content": "Your order has been confirmed. Thank you!",
          "direction": "out",
          "status": "delivered",
          "created_at": "2024-01-17 08:45:00",
          "created_at_human": "2 hours ago"
        }
      ]
    },
    "last_updated": "2024-01-17T10:30:00Z"
  }
}
```

---

## 🚨 Error Responses

### No Tenant Associated
**Status Code:** `400 Bad Request`
```json
{
  "success": false,
  "message": "User is not associated with any tenant. Please contact support."
}
```

### Unauthorized Access
**Status Code:** `401 Unauthorized`
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Server Error
**Status Code:** `500 Internal Server Error`
```json
{
  "success": false,
  "message": "Failed to retrieve dashboard data",
  "error": "Database connection error"
}
```

---

## 📋 Data Field Descriptions

### Metrics Fields
| Field | Type | Description |
|-------|------|-------------|
| `total_messages` | integer | Total messages sent (all time) |
| `total_sms_messages` | integer | Total SMS messages sent |
| `active_contacts` | integer | Number of active contacts |
| `campaign_success_rate` | float | Campaign delivery success rate (%) |
| `sms_delivery_rate` | float | SMS delivery success rate (%) |
| `current_credits` | integer | Available SMS credits |
| `total_purchased` | integer | Total credits purchased |
| `sender_ids_this_month` | integer | Sender IDs used this month |

### Change Types
| Type | Description |
|------|-------------|
| `positive` | Increase from previous period |
| `negative` | Decrease from previous period |
| `neutral` | No change or insufficient data |

### Campaign Status
| Status | Description |
|--------|-------------|
| `draft` | Campaign created but not started |
| `scheduled` | Campaign scheduled for future |
| `running` | Campaign currently active |
| `paused` | Campaign temporarily stopped |
| `completed` | Campaign finished successfully |
| `cancelled` | Campaign cancelled |
| `failed` | Campaign failed to complete |

### Message Status
| Status | Description |
|--------|-------------|
| `sent` | Message sent to provider |
| `delivered` | Message delivered to recipient |
| `failed` | Message delivery failed |
| `read` | Message read by recipient |

---

## 🔄 Usage Examples

### JavaScript Fetch
```javascript
// Get comprehensive dashboard data
fetch('/api/messaging/dashboard/comprehensive/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Dashboard data:', data.data);
  }
});
```

### cURL Example
```bash
curl -X GET "https://104.131.116.55/api/messaging/dashboard/overview/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 📊 Frontend Integration Notes

1. **Authentication**: All endpoints require JWT authentication
2. **Rate Limiting**: Consider implementing client-side caching
3. **Error Handling**: Always check the `success` field before processing data
4. **Real-time Updates**: Use `last_updated` timestamp for cache invalidation
5. **Empty States**: Handle cases where metrics return 0 values gracefully

---

## 🔧 Testing

Test the endpoints using:
- **Postman**: Import the endpoints with proper headers
- **Browser**: Use developer tools with authentication
- **cURL**: Command line testing as shown above

---

*Last Updated: January 17, 2024*
