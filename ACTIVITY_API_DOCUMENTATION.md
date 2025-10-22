# Activity & Performance API Documentation

## Overview

The Activity & Performance API provides real-time activity tracking and performance metrics for the dashboard. This API supports the dashboard interface shown in the UI screenshots with "Recent Activity" and "Performance Overview" sections.

## Base URL

```
/api/messaging/
```

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Recent Activity

**GET** `/api/messaging/activity/recent/`

Get recent activity feed for the dashboard with live activity indicators.

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | integer | Number of activities to return (default: 10) | `?limit=20` |
| `type` | string | Filter by activity type | `?type=conversation_reply` |

#### Activity Types

- `conversation_reply` - New messages in conversations
- `campaign_completed` - Completed campaigns
- `contact_added` - New contacts added
- `contacts_added` - Bulk contact imports
- `template_approved` - Template approvals
- `campaign_started` - Campaign launches

#### Response

```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "msg_uuid",
        "type": "conversation_reply",
        "title": "John Kamau replied to conversation Kenya Coffee Exports",
        "description": "New message: Thank you for the quick response...",
        "timestamp": "2024-01-15T10:30:00Z",
        "time_ago": "2 min ago",
        "is_live": true,
        "metadata": {
          "conversation_id": "uuid",
          "contact_name": "John Kamau",
          "conversation_subject": "Kenya Coffee Exports",
          "message_id": "uuid"
        }
      },
      {
        "id": "camp_uuid",
        "type": "campaign_completed",
        "title": "System completed campaign Mother's Day Promotion",
        "description": "98% delivered",
        "timestamp": "2024-01-15T10:15:00Z",
        "time_ago": "15 min ago",
        "is_live": false,
        "metadata": {
          "campaign_id": "uuid",
          "campaign_name": "Mother's Day Promotion",
          "delivery_rate": 98,
          "sent_count": 1000,
          "delivered_count": 980
        }
      },
      {
        "id": "contact_uuid",
        "type": "contact_added",
        "title": "Sarah Mwangi added to contacts",
        "description": "New contact: +255700000002",
        "timestamp": "2024-01-15T09:30:00Z",
        "time_ago": "1 hour ago",
        "is_live": false,
        "metadata": {
          "contact_id": "uuid",
          "contact_name": "Sarah Mwangi",
          "phone": "+255700000002"
        }
      },
      {
        "id": "contacts_uuid",
        "type": "contacts_added",
        "title": "Added 25 new contacts",
        "description": "Bulk import completed",
        "timestamp": "2024-01-15T09:00:00Z",
        "time_ago": "1 hour ago",
        "is_live": false,
        "metadata": {
          "count": 25,
          "contacts": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
        }
      },
      {
        "id": "template_uuid",
        "type": "template_approved",
        "title": "David Ochieng approved template Welcome Message - Swahili",
        "description": "Onboarding - Kiswahili",
        "timestamp": "2024-01-15T08:30:00Z",
        "time_ago": "2 hours ago",
        "is_live": false,
        "metadata": {
          "template_id": "uuid",
          "template_name": "Welcome Message - Swahili",
          "category": "onboarding",
          "language": "sw",
          "channel": "whatsapp"
        }
      }
    ],
    "has_more": true,
    "total_count": 25,
    "live_count": 1
  }
}
```

---

### 2. Performance Overview

**GET** `/api/messaging/performance/overview/`

Get performance metrics and chart data for the dashboard.

#### Response

```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_messages": 1250,
      "delivery_rate": 96.8,
      "response_rate": 45.2,
      "active_conversations": 25,
      "campaign_success_rate": 94.2
    },
    "charts": {
      "message_volume": {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
        "data": [100, 150, 200, 180, 220]
      },
      "delivery_rates": {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
        "data": [95, 96, 97, 96, 98]
      }
    },
    "coming_soon": true
  }
}
```

#### Metrics Description

| Metric | Description |
|--------|-------------|
| `total_messages` | Total messages sent and received |
| `delivery_rate` | Percentage of successfully delivered messages |
| `response_rate` | Percentage of conversations with replies |
| `active_conversations` | Number of open conversations |
| `campaign_success_rate` | Percentage of successful campaigns |

---

### 3. Activity Statistics

**GET** `/api/messaging/activity/statistics/`

Get detailed activity statistics for different time periods.

#### Response

```json
{
  "success": true,
  "data": {
    "today": {
      "messages_sent": 25,
      "messages_received": 15,
      "conversations_started": 5,
      "campaigns_launched": 2
    },
    "this_week": {
      "messages_sent": 180,
      "messages_received": 120,
      "conversations_started": 35,
      "campaigns_launched": 8
    },
    "this_month": {
      "messages_sent": 750,
      "messages_received": 500,
      "conversations_started": 150,
      "campaigns_launched": 25
    }
  }
}
```

#### Statistics Description

| Statistic | Description |
|-----------|-------------|
| `messages_sent` | Outgoing messages sent |
| `messages_received` | Incoming messages received |
| `conversations_started` | New conversations initiated |
| `campaigns_launched` | Campaigns started |

---

## Frontend Integration Examples

### JavaScript - Recent Activity

```javascript
const getRecentActivity = async (limit = 10, type = null) => {
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit);
  if (type) params.append('type', type);
  
  const response = await fetch(`/api/messaging/activity/recent/?${params}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

// Usage
const activities = await getRecentActivity(10);
const liveActivities = activities.data.activities.filter(a => a.is_live);
```

### JavaScript - Performance Overview

```javascript
const getPerformanceOverview = async () => {
  const response = await fetch('/api/messaging/performance/overview/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

// Usage
const performance = await getPerformanceOverview();
const metrics = performance.data.metrics;
const charts = performance.data.charts;
```

### JavaScript - Activity Statistics

```javascript
const getActivityStatistics = async () => {
  const response = await fetch('/api/messaging/activity/statistics/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

// Usage
const stats = await getActivityStatistics();
const todayStats = stats.data.today;
const weekStats = stats.data.this_week;
const monthStats = stats.data.this_month;
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [activities, setActivities] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [activitiesRes, performanceRes] = await Promise.all([
        fetch('/api/messaging/activity/recent/?limit=10', {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch('/api/messaging/performance/overview/', {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          }
        })
      ]);

      const activitiesData = await activitiesRes.json();
      const performanceData = await performanceRes.json();

      setActivities(activitiesData.data.activities);
      setPerformance(performanceData.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'conversation_reply':
        return '💬';
      case 'campaign_completed':
        return '📊';
      case 'contact_added':
        return '👤';
      case 'template_approved':
        return '✅';
      case 'campaign_started':
        return '🚀';
      default:
        return '📝';
    }
  };

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* Recent Activity */}
        <div className="activity-panel">
          <div className="panel-header">
            <h3>Recent Activity</h3>
            <span className="live-indicator">Live</span>
          </div>
          
          <div className="activity-list">
            {activities.map(activity => (
              <div key={activity.id} className={`activity-item ${activity.is_live ? 'live' : ''}`}>
                <div className="activity-icon">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="activity-content">
                  <div className="activity-title">
                    {activity.title}
                    {activity.is_live && <span className="live-dot">●</span>}
                  </div>
                  <div className="activity-description">
                    {activity.description}
                  </div>
                  <div className="activity-time">
                    {activity.time_ago}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="panel-footer">
            <a href="#" className="view-all-link">View all activity</a>
          </div>
        </div>

        {/* Performance Overview */}
        <div className="performance-panel">
          <div className="panel-header">
            <h3>Performance Overview</h3>
          </div>
          
          {performance.coming_soon ? (
            <div className="coming-soon">
              <div className="chart-placeholder">
                <div className="chart-icon">📈</div>
                <p>Analytics charts coming soon</p>
              </div>
            </div>
          ) : (
            <div className="performance-metrics">
              <div className="metric">
                <div className="metric-value">{performance.metrics.total_messages}</div>
                <div className="metric-label">Total Messages</div>
              </div>
              <div className="metric">
                <div className="metric-value">{performance.metrics.delivery_rate}%</div>
                <div className="metric-label">Delivery Rate</div>
              </div>
              <div className="metric">
                <div className="metric-value">{performance.metrics.response_rate}%</div>
                <div className="metric-label">Response Rate</div>
              </div>
              <div className="metric">
                <div className="metric-value">{performance.metrics.active_conversations}</div>
                <div className="metric-label">Active Conversations</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

---

## Activity Types Reference

### Conversation Reply
- **Type**: `conversation_reply`
- **Trigger**: New incoming message in a conversation
- **Live**: Yes (within 5 minutes)
- **Metadata**: conversation_id, contact_name, conversation_subject, message_id

### Campaign Completed
- **Type**: `campaign_completed`
- **Trigger**: Campaign status changes to 'completed'
- **Live**: No
- **Metadata**: campaign_id, campaign_name, delivery_rate, sent_count, delivered_count

### Contact Added
- **Type**: `contact_added`
- **Trigger**: Single contact created
- **Live**: No
- **Metadata**: contact_id, contact_name, phone

### Contacts Added (Bulk)
- **Type**: `contacts_added`
- **Trigger**: Multiple contacts added in same hour
- **Live**: No
- **Metadata**: count, contacts (array of contact IDs)

### Template Approved
- **Type**: `template_approved`
- **Trigger**: Template status changes to 'approved'
- **Live**: No
- **Metadata**: template_id, template_name, category, language, channel

### Campaign Started
- **Type**: `campaign_started`
- **Trigger**: Campaign status changes to 'running'
- **Live**: Yes (within 5 minutes)
- **Metadata**: campaign_id, campaign_name, recipient_count

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "message": "User is not associated with any tenant"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Failed to retrieve recent activity",
  "error": "Database connection error"
}
```

---

## Rate Limiting

Activity endpoints are subject to rate limiting:

- **Recent Activity**: 60 requests per minute per user
- **Performance Overview**: 30 requests per minute per user
- **Activity Statistics**: 30 requests per minute per user

---

## Testing

Run the activity test suite:

```bash
python test_activity_endpoints.py
```

This will test all activity functionality including:
- Recent activity feed
- Activity filtering
- Performance metrics
- Activity statistics

---

## Summary

The Activity & Performance API provides:

✅ **Real-time Activity Feed** - Live activity tracking with timestamps
✅ **Activity Filtering** - Filter by activity type
✅ **Performance Metrics** - Key performance indicators
✅ **Chart Data** - Ready for visualization
✅ **Time-based Statistics** - Today, week, month breakdowns
✅ **Live Indicators** - Real-time activity status
✅ **Comprehensive Metadata** - Rich context for each activity
✅ **Frontend Ready** - Complete integration examples

This API fully supports the dashboard interface shown in the UI screenshots and provides all the functionality needed for a comprehensive activity tracking and performance monitoring system.
