# Activity & Performance Dashboard Documentation

## Overview

The Activity & Performance Dashboard provides real-time activity tracking and performance metrics for the Mifumo SMS platform. This system supports the dashboard interface with "Recent Activity" and "Performance Overview" sections, offering comprehensive insights into user engagement and system performance.

## Base URL

```
/api/messaging/
```

## Authentication

All dashboard endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## 📊 Recent Activity Feed

### Endpoint

**GET** `/api/messaging/activity/recent/`

Get real-time activity feed with live indicators for the dashboard.

#### Query Parameters

| Parameter | Type | Description | Default | Example |
|-----------|------|-------------|---------|---------|
| `limit` | integer | Number of activities to return | 10 | `?limit=20` |
| `type` | string | Filter by activity type | null | `?type=conversation_reply` |

#### Activity Types

| Type | Description | Live Status |
|------|-------------|-------------|
| `conversation_reply` | New messages in conversations | ✅ Yes (5 min) |
| `campaign_completed` | Completed campaigns | ❌ No |
| `contact_added` | Single contact added | ❌ No |
| `contacts_added` | Bulk contact imports | ❌ No |
| `template_approved` | Template approvals | ❌ No |
| `campaign_started` | Campaign launches | ✅ Yes (5 min) |

#### Response Structure

```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "string",
        "type": "string",
        "title": "string",
        "description": "string",
        "timestamp": "ISO 8601",
        "time_ago": "string",
        "is_live": boolean,
        "metadata": {
          "conversation_id": "uuid",
          "contact_name": "string",
          "conversation_subject": "string",
          "message_id": "uuid"
        }
      }
    ],
    "has_more": boolean,
    "total_count": integer,
    "live_count": integer
  }
}
```

#### Sample Response

```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "msg_123e4567-e89b-12d3-a456-426614174000",
        "type": "conversation_reply",
        "title": "John Kamau replied to conversation Kenya Coffee Exports",
        "description": "New message: Thank you for the quick response...",
        "timestamp": "2024-01-15T10:30:00Z",
        "time_ago": "2 min ago",
        "is_live": true,
        "metadata": {
          "conversation_id": "conv_123e4567-e89b-12d3-a456-426614174000",
          "contact_name": "John Kamau",
          "conversation_subject": "Kenya Coffee Exports",
          "message_id": "msg_123e4567-e89b-12d3-a456-426614174000"
        }
      },
      {
        "id": "camp_123e4567-e89b-12d3-a456-426614174001",
        "type": "campaign_completed",
        "title": "System completed campaign Mother's Day Promotion",
        "description": "98% delivered",
        "timestamp": "2024-01-15T10:15:00Z",
        "time_ago": "15 min ago",
        "is_live": false,
        "metadata": {
          "campaign_id": "camp_123e4567-e89b-12d3-a456-426614174001",
          "campaign_name": "Mother's Day Promotion",
          "delivery_rate": 98,
          "sent_count": 1000,
          "delivered_count": 980
        }
      },
      {
        "id": "contact_123e4567-e89b-12d3-a456-426614174002",
        "type": "contact_added",
        "title": "Sarah Mwangi added to contacts",
        "description": "New contact: +255700000002",
        "timestamp": "2024-01-15T09:30:00Z",
        "time_ago": "1 hour ago",
        "is_live": false,
        "metadata": {
          "contact_id": "contact_123e4567-e89b-12d3-a456-426614174002",
          "contact_name": "Sarah Mwangi",
          "phone": "+255700000002"
        }
      },
      {
        "id": "contacts_123e4567-e89b-12d3-a456-426614174003",
        "type": "contacts_added",
        "title": "Added 25 new contacts",
        "description": "Bulk import completed",
        "timestamp": "2024-01-15T09:00:00Z",
        "time_ago": "1 hour ago",
        "is_live": false,
        "metadata": {
          "count": 25,
          "contacts": [
            "contact_123e4567-e89b-12d3-a456-426614174004",
            "contact_123e4567-e89b-12d3-a456-426614174005",
            "contact_123e4567-e89b-12d3-a456-426614174006",
            "contact_123e4567-e89b-12d3-a456-426614174007",
            "contact_123e4567-e89b-12d3-a456-426614174008"
          ]
        }
      },
      {
        "id": "template_123e4567-e89b-12d3-a456-426614174009",
        "type": "template_approved",
        "title": "David Ochieng approved template Welcome Message - Swahili",
        "description": "Onboarding - Kiswahili",
        "timestamp": "2024-01-15T08:30:00Z",
        "time_ago": "2 hours ago",
        "is_live": false,
        "metadata": {
          "template_id": "template_123e4567-e89b-12d3-a456-426614174009",
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

## 📈 Performance Overview

### Endpoint

**GET** `/api/messaging/performance/overview/`

Get performance metrics and chart data for the dashboard overview.

#### Response Structure

```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_messages": integer,
      "delivery_rate": float,
      "response_rate": float,
      "active_conversations": integer,
      "campaign_success_rate": float
    },
    "charts": {
      "message_volume": {
        "labels": ["string"],
        "data": [integer]
      },
      "delivery_rates": {
        "labels": ["string"],
        "data": [float]
      }
    },
    "coming_soon": boolean
  }
}
```

#### Sample Response

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

| Metric | Description | Unit |
|--------|-------------|------|
| `total_messages` | Total messages sent and received | Count |
| `delivery_rate` | Percentage of successfully delivered messages | Percentage |
| `response_rate` | Percentage of conversations with replies | Percentage |
| `active_conversations` | Number of open conversations | Count |
| `campaign_success_rate` | Percentage of successful campaigns | Percentage |

---

## 📊 Activity Statistics

### Endpoint

**GET** `/api/messaging/activity/statistics/`

Get detailed activity statistics for different time periods.

#### Response Structure

```json
{
  "success": true,
  "data": {
    "today": {
      "messages_sent": integer,
      "messages_received": integer,
      "conversations_started": integer,
      "campaigns_launched": integer
    },
    "this_week": {
      "messages_sent": integer,
      "messages_received": integer,
      "conversations_started": integer,
      "campaigns_launched": integer
    },
    "this_month": {
      "messages_sent": integer,
      "messages_received": integer,
      "conversations_started": integer,
      "campaigns_launched": integer
    }
  }
}
```

#### Sample Response

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

## 🔴 Live Activity Indicators

### Live Status Logic

Activities are marked as "live" based on the following criteria:

1. **Time-based**: Activities within the last 5 minutes
2. **Type-based**: Only certain activity types can be live:
   - `conversation_reply` - New incoming messages
   - `campaign_started` - Campaign launches

### Live Activity Features

- **Visual Indicators**: Live activities show a red dot (●) in the UI
- **Real-time Updates**: Frontend can poll for updates every 30 seconds
- **Live Count**: Total number of live activities returned in response
- **Metadata**: Rich context for each live activity

---

## 🎯 Frontend Integration

### JavaScript Implementation

#### Recent Activity Component

```javascript
class ActivityFeed {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseUrl = '/api/messaging';
  }

  async getRecentActivity(limit = 10, type = null) {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit);
    if (type) params.append('type', type);
    
    const response = await fetch(`${this.baseUrl}/activity/recent/?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    return await response.json();
  }

  async getLiveActivities() {
    const data = await this.getRecentActivity(50);
    return data.data.activities.filter(activity => activity.is_live);
  }

  getActivityIcon(type) {
    const icons = {
      'conversation_reply': '💬',
      'campaign_completed': '📊',
      'contact_added': '👤',
      'contacts_added': '👥',
      'template_approved': '✅',
      'campaign_started': '🚀'
    };
    return icons[type] || '📝';
  }

  formatTimeAgo(timestamp) {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffMs = now - activityTime;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  }
}
```

#### Performance Overview Component

```javascript
class PerformanceOverview {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseUrl = '/api/messaging';
  }

  async getPerformanceMetrics() {
    const response = await fetch(`${this.baseUrl}/performance/overview/`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    return await response.json();
  }

  async getActivityStatistics() {
    const response = await fetch(`${this.baseUrl}/activity/statistics/`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    return await response.json();
  }

  formatMetric(value, type = 'number') {
    switch (type) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'number':
        return value.toLocaleString();
      default:
        return value;
    }
  }
}
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const Dashboard = ({ accessToken }) => {
  const [activities, setActivities] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [liveCount, setLiveCount] = useState(0);

  useEffect(() => {
    loadDashboardData();
    
    // Poll for live updates every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const activityFeed = new ActivityFeed(accessToken);
      const performanceOverview = new PerformanceOverview(accessToken);

      const [activitiesRes, performanceRes, statisticsRes] = await Promise.all([
        activityFeed.getRecentActivity(10),
        performanceOverview.getPerformanceMetrics(),
        performanceOverview.getActivityStatistics()
      ]);

      setActivities(activitiesRes.data.activities);
      setLiveCount(activitiesRes.data.live_count);
      setPerformance(performanceRes.data);
      setStatistics(statisticsRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type) => {
    const icons = {
      'conversation_reply': '💬',
      'campaign_completed': '📊',
      'contact_added': '👤',
      'contacts_added': '👥',
      'template_approved': '✅',
      'campaign_started': '🚀'
    };
    return icons[type] || '📝';
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        {liveCount > 0 && (
          <div className="live-indicator">
            <span className="live-dot">●</span>
            {liveCount} live
          </div>
        )}
      </div>

      <div className="dashboard-grid">
        {/* Recent Activity Panel */}
        <div className="activity-panel">
          <div className="panel-header">
            <h3>Recent Activity</h3>
            <span className="live-badge">Live</span>
          </div>
          
          <div className="activity-list">
            {activities.map(activity => (
              <div 
                key={activity.id} 
                className={`activity-item ${activity.is_live ? 'live' : ''}`}
              >
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

        {/* Performance Overview Panel */}
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
              <div className="metric-grid">
                <div className="metric">
                  <div className="metric-value">
                    {performance.metrics.total_messages.toLocaleString()}
                  </div>
                  <div className="metric-label">Total Messages</div>
                </div>
                <div className="metric">
                  <div className="metric-value">
                    {performance.metrics.delivery_rate.toFixed(1)}%
                  </div>
                  <div className="metric-label">Delivery Rate</div>
                </div>
                <div className="metric">
                  <div className="metric-value">
                    {performance.metrics.response_rate.toFixed(1)}%
                  </div>
                  <div className="metric-label">Response Rate</div>
                </div>
                <div className="metric">
                  <div className="metric-value">
                    {performance.metrics.active_conversations}
                  </div>
                  <div className="metric-label">Active Conversations</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Activity Statistics Panel */}
        <div className="statistics-panel">
          <div className="panel-header">
            <h3>Activity Statistics</h3>
          </div>
          
          <div className="statistics-grid">
            <div className="stat-period">
              <h4>Today</h4>
              <div className="stat-items">
                <div className="stat-item">
                  <span className="stat-label">Messages Sent:</span>
                  <span className="stat-value">{statistics.today.messages_sent}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Messages Received:</span>
                  <span className="stat-value">{statistics.today.messages_received}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Conversations Started:</span>
                  <span className="stat-value">{statistics.today.conversations_started}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Campaigns Launched:</span>
                  <span className="stat-value">{statistics.today.campaigns_launched}</span>
                </div>
              </div>
            </div>

            <div className="stat-period">
              <h4>This Week</h4>
              <div className="stat-items">
                <div className="stat-item">
                  <span className="stat-label">Messages Sent:</span>
                  <span className="stat-value">{statistics.this_week.messages_sent}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Messages Received:</span>
                  <span className="stat-value">{statistics.this_week.messages_received}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Conversations Started:</span>
                  <span className="stat-value">{statistics.this_week.conversations_started}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Campaigns Launched:</span>
                  <span className="stat-value">{statistics.this_week.campaigns_launched}</span>
                </div>
              </div>
            </div>

            <div className="stat-period">
              <h4>This Month</h4>
              <div className="stat-items">
                <div className="stat-item">
                  <span className="stat-label">Messages Sent:</span>
                  <span className="stat-value">{statistics.this_month.messages_sent}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Messages Received:</span>
                  <span className="stat-value">{statistics.this_month.messages_received}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Conversations Started:</span>
                  <span className="stat-value">{statistics.this_month.conversations_started}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Campaigns Launched:</span>
                  <span className="stat-value">{statistics.this_month.campaigns_launched}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

### CSS Styling Example

```css
/* Dashboard Layout */
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e74c3c;
  font-weight: 600;
}

.live-dot {
  color: #e74c3c;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* Activity Panel */
.activity-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.live-badge {
  background: #e74c3c;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  padding: 15px 20px;
  border-bottom: 1px solid #f5f5f5;
  transition: background-color 0.2s;
}

.activity-item:hover {
  background-color: #f8f9fa;
}

.activity-item.live {
  background-color: #fff5f5;
  border-left: 3px solid #e74c3c;
}

.activity-icon {
  font-size: 20px;
  margin-right: 15px;
  margin-top: 2px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.activity-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.activity-time {
  color: #999;
  font-size: 12px;
}

/* Performance Panel */
.performance-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.coming-soon {
  padding: 40px 20px;
  text-align: center;
}

.chart-placeholder {
  color: #999;
}

.chart-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.performance-metrics {
  padding: 20px;
}

.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.metric {
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.metric-label {
  color: #666;
  font-size: 14px;
}

/* Statistics Panel */
.statistics-panel {
  grid-column: 1 / -1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 20px;
}

.stat-period h4 {
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 16px;
}

.stat-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
  color: #2c3e50;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .statistics-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 🔄 Real-time Updates

### Polling Strategy

For real-time updates, implement the following polling strategy:

```javascript
class RealTimeDashboard {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.pollInterval = 30000; // 30 seconds
    this.isPolling = false;
    this.pollTimer = null;
  }

  startPolling() {
    if (this.isPolling) return;
    
    this.isPolling = true;
    this.pollTimer = setInterval(() => {
      this.updateDashboard();
    }, this.pollInterval);
  }

  stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    this.isPolling = false;
  }

  async updateDashboard() {
    try {
      const activityFeed = new ActivityFeed(this.accessToken);
      const data = await activityFeed.getRecentActivity(10);
      
      // Update UI with new data
      this.updateActivityFeed(data.data.activities);
      this.updateLiveCount(data.data.live_count);
    } catch (error) {
      console.error('Failed to update dashboard:', error);
    }
  }

  updateActivityFeed(activities) {
    // Update activity feed in UI
    const activityList = document.querySelector('.activity-list');
    // ... update logic
  }

  updateLiveCount(count) {
    // Update live count indicator
    const liveIndicator = document.querySelector('.live-indicator');
    if (count > 0) {
      liveIndicator.style.display = 'flex';
      liveIndicator.querySelector('.live-count').textContent = count;
    } else {
      liveIndicator.style.display = 'none';
    }
  }
}
```

---

## 🚨 Error Handling

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

### Error Handling in Frontend

```javascript
const handleDashboardError = (error, context) => {
  console.error(`Dashboard error in ${context}:`, error);
  
  // Show user-friendly error message
  const errorMessage = error.message || 'An unexpected error occurred';
  
  // Display error notification
  showNotification({
    type: 'error',
    title: 'Dashboard Error',
    message: errorMessage,
    duration: 5000
  });
  
  // Retry logic for transient errors
  if (error.status >= 500) {
    setTimeout(() => {
      loadDashboardData();
    }, 5000);
  }
};
```

---

## 📊 Rate Limiting

Dashboard endpoints are subject to rate limiting:

- **Recent Activity**: 60 requests per minute per user
- **Performance Overview**: 30 requests per minute per user
- **Activity Statistics**: 30 requests per minute per user

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642248000
```

---

## 🧪 Testing

### Test the Activity Endpoints

```bash
# Run the activity test suite
python test_activity_endpoints.py
```

### Manual Testing Examples

```bash
# Get recent activity
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/messaging/activity/recent/"

# Get filtered activity
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/messaging/activity/recent/?type=conversation_reply&limit=5"

# Get performance overview
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/messaging/performance/overview/"

# Get activity statistics
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/messaging/activity/statistics/"
```

---

## 📋 Summary

The Activity & Performance Dashboard provides:

✅ **Real-time Activity Feed** - Live activity tracking with timestamps  
✅ **Live Indicators** - Visual indicators for recent activities  
✅ **Activity Filtering** - Filter by activity type  
✅ **Performance Metrics** - Key performance indicators  
✅ **Chart Data** - Ready for visualization  
✅ **Time-based Statistics** - Today, week, month breakdowns  
✅ **Rich Metadata** - Comprehensive context for each activity  
✅ **Frontend Ready** - Complete integration examples  
✅ **Error Handling** - Comprehensive error management  
✅ **Rate Limiting** - Protection against abuse  
✅ **Testing Suite** - Complete test coverage  

This dashboard system fully supports the UI requirements and provides a comprehensive real-time activity tracking and performance monitoring solution.
