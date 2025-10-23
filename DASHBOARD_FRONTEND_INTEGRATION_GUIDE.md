# Dashboard Frontend Integration Guide

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

## 1. Recent Activity - Activity Feed

**Endpoint:** `GET /api/messaging/activity/recent/`

**Purpose:** Get recent activity feed for the dashboard

### JSON Response:
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "msg_756d7148-b2ef-476d-8dc7-001892a80129",
        "type": "message_sent",
        "title": "Message sent to Mgasa Engineer",
        "description": "New message: Welcome to Mifumo WMS!",
        "timestamp": "2025-10-22T20:06:48.669446+00:00",
        "time_ago": "1 hour ago",
        "is_live": false,
        "metadata": {
          "conversation_id": "0921c374-4b4d-4889-9990-ae6962885fa6",
          "contact_name": "Mgasa Engineer",
          "conversation_subject": "Welcome Conversation",
          "message_id": "756d7148-b2ef-476d-8dc7-001892a80129"
        }
      },
      {
        "id": "camp_75cd9c85-8d71-4f18-aa7d-2388b6990591",
        "type": "campaign_completed",
        "title": "System completed campaign Welcome Campaign",
        "description": "98% delivered",
        "timestamp": "2025-10-22T20:06:30.144879+00:00",
        "time_ago": "2 hours ago",
        "is_live": false,
        "metadata": {
          "campaign_id": "75cd9c85-8d71-4f18-aa7d-2388b6990591",
          "campaign_name": "Welcome Campaign",
          "delivery_rate": 98,
          "sent_count": 100,
          "delivered_count": 98
        }
      },
      {
        "id": "contact_3f83f7dd-d09c-454a-8fdc-36de7967546d",
        "type": "contact_added",
        "title": "Mgasa Engineer added to contacts",
        "description": "New contact: +255689726060",
        "timestamp": "2025-10-22T20:06:30.072215+00:00",
        "time_ago": "2 hours ago",
        "is_live": false,
        "metadata": {
          "contact_id": "3f83f7dd-d09c-454a-8fdc-36de7967546d",
          "contact_name": "Mgasa Engineer",
          "phone": "+255689726060"
        }
      },
      {
        "id": "msg_476074f2-6a4a-467a-b8d4-db0c21f8b3dd",
        "type": "message_sent",
        "title": "Message sent to 255614853618",
        "description": "New message: Hello, this is me ivan 0614853618",
        "timestamp": "2025-10-22T20:02:35.075755+00:00",
        "time_ago": "2 hours ago",
        "is_live": false,
        "metadata": {
          "conversation_id": null,
          "contact_name": "255614853618",
          "conversation_subject": "SMS",
          "message_id": "476074f2-6a4a-467a-b8d4-db0c21f8b3dd"
        }
      }
    ],
    "has_more": false,
    "total_count": 4,
    "live_count": 0
  }
}
```

### Frontend Usage:
```javascript
// Display activity feed
const activities = response.data.activities;
activities.forEach(activity => {
  const activityElement = document.createElement('div');
  activityElement.innerHTML = `
    <div class="activity-item ${activity.is_live ? 'live' : ''}">
      <h4>${activity.title}</h4>
      <p>${activity.description}</p>
      <span class="time">${activity.time_ago}</span>
    </div>
  `;
  document.getElementById('activity-feed').appendChild(activityElement);
});
```

---

## 2. Performance Overview

**Endpoint:** `GET /api/messaging/performance/overview/`

**Purpose:** Get performance analytics and metrics for the dashboard

### JSON Response:
```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_messages": 2,
      "delivery_rate": 50.0,
      "response_rate": 0.0,
      "active_conversations": 1,
      "campaign_success_rate": 98.0
    },
    "charts": {
      "message_volume": {
        "labels": [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "May"
        ],
        "data": [
          100,
          150,
          200,
          180,
          220
        ]
      },
      "delivery_rates": {
        "labels": [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "May"
        ],
        "data": [
          95,
          96,
          97,
          96,
          98
        ]
      }
    },
    "coming_soon": true
  }
}
```

### Frontend Usage:
```javascript
// Display performance overview
const performance = response.data;
console.log(`Total Messages: ${performance.metrics.total_messages}`);
console.log(`Delivery Rate: ${performance.metrics.delivery_rate}%`);
console.log(`Campaign Success: ${performance.metrics.campaign_success_rate}%`);

// Display charts data
const messageVolume = performance.charts.message_volume;
const deliveryRates = performance.charts.delivery_rates;
```

---

## 3. Sender IDs - Accepted Sender IDs

**Endpoint:** `GET /api/messaging/sender-ids/`

**Purpose:** Get list of active/accepted sender IDs for the current tenant

### JSON Response:
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

### Frontend Usage:
```javascript
// Display accepted sender IDs
const senderIds = response.data;
senderIds.forEach(senderId => {
  console.log(`${senderId.sender_id} - ${senderId.status} - ${senderId.sample_content}`);
});
```

---

## Complete Frontend Integration Example

```javascript
// Dashboard API Integration
class DashboardAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async fetchDashboardData() {
    try {
      const [activity, performance, senderIds] = await Promise.all([
        this.fetchActivity(),
        this.fetchPerformance(),
        this.fetchSenderIds()
      ]);

      return {
        activity: activity.data.activities,
        performance: performance.data,
        senderIds: senderIds.data
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  async fetchActivity() {
    const response = await fetch(`${this.baseURL}/api/messaging/activity/recent/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return await response.json();
  }

  async fetchPerformance() {
    const response = await fetch(`${this.baseURL}/api/messaging/performance/overview/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return await response.json();
  }

  async fetchSenderIds() {
    const response = await fetch(`${this.baseURL}/api/messaging/sender-ids/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return await response.json();
  }
}

// Usage
const dashboard = new DashboardAPI('http://127.0.0.1:8001', 'your-jwt-token');
dashboard.fetchDashboardData().then(data => {
  console.log('Dashboard data loaded:', data);
  // Update your UI with the data
  console.log('Activity:', data.activity);    // Activity feed
  console.log('Performance:', data.performance); // Performance data
  console.log('Sender IDs:', data.senderIds); // Accepted sender IDs
});
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "code": 400,
  "details": "Additional error details"
}
```

### Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `500` - Internal Server Error

---

## Notes for Frontend Development

1. **Authentication**: Always include the JWT token in the Authorization header
2. **Error Handling**: Check the `success` field in responses before processing data
3. **Data Structure**: All successful responses have a `data` field containing the actual data
4. **Timestamps**: Use `time_ago` for user-friendly time display
5. **Live Indicators**: Check `is_live` field for real-time activity indicators
6. **Pagination**: Use `has_more` field to implement pagination for activity feed

The dashboard APIs are fully functional and returning real data from your database!