# Dashboard API Reference - Exact Image Data

## Base URL
```
http://127.0.0.1:8001/api/messaging/
```

## Authentication
```javascript
headers: {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
}
```

---

## 1. Dashboard Metrics - 4 Main Cards

**Endpoint:** `GET /api/messaging/dashboard/metrics/`

**Purpose:** Get the 4 main dashboard cards data (exactly as shown in image)

### JSON Response:
```json
{
  "success": true,
  "data": {
    "total_messages": {
      "value": 2,
      "description": "Last 30 days"
    },
    "active_contacts": {
      "value": 1,
      "description": "Engaged this month"
    },
    "campaign_success": {
      "value": 98.0,
      "unit": "%",
      "description": "Delivery rate"
    },
    "senderId": {
      "value": 2,
      "description": "Approved sender names"
    }
  }
}
```

### Frontend Usage:
```javascript
// Display the 4 main cards exactly as in image
const metrics = response.data;
document.getElementById('total-messages').textContent = metrics.total_messages.value;
document.getElementById('active-contacts').textContent = metrics.active_contacts.value;
document.getElementById('campaign-success').textContent = metrics.campaign_success.value + '%';
document.getElementById('sender-id').textContent = metrics.senderId.value;
```

---

## 2. Recent Campaigns

**Endpoint:** `GET /api/messaging/campaigns/summary/`

**Purpose:** Get recent campaigns for dashboard display

### JSON Response:
```json
{
  "success": true,
  "summary": {
    "recent_campaigns": [
      {
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

### Frontend Usage:
```javascript
// Display recent campaigns
const campaigns = response.summary.recent_campaigns;
campaigns.forEach(campaign => {
  console.log(`${campaign.name} - ${campaign.type} - ${campaign.status} - ${campaign.sent} sent, ${campaign.delivered} delivered`);
});
```

---

## 3. Recent Activity

**Endpoint:** `GET /api/messaging/activity/recent/`

**Purpose:** Get recent activity feed for dashboard

### JSON Response:
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "actor": "John Kamau",
        "action": "replied to conversation",
        "target": "Kenya Coffee Exports",
        "timeAgo": "2 min ago",
        "isLive": true
      },
      {
        "actor": "System",
        "action": "completed campaign",
        "target": "Mother's Day Promotion",
        "deliveryRate": "98% delivered",
        "timeAgo": "15 min ago"
      },
      {
        "actor": "Sarah Mwangi",
        "action": "added 25 new contacts",
        "target": "Nairobi SME List",
        "timeAgo": "1 hour ago"
      },
      {
        "actor": "David Ochieng",
        "action": "approved template",
        "target": "Welcome Message - Swahili",
        "timeAgo": "2 hours ago"
      }
    ]
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
    <div class="activity-item ${activity.isLive ? 'live' : ''}">
      <strong>${activity.actor}</strong> ${activity.action} <strong>${activity.target}</strong>
      <span class="time">${activity.timeAgo}</span>
    </div>
  `;
  document.getElementById('activity-feed').appendChild(activityElement);
});
```

---

## Complete Frontend Integration

```javascript
// Simple dashboard data fetcher
async function fetchDashboardData(token) {
  const baseURL = 'http://127.0.0.1:8001/api/messaging';
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  try {
    // Fetch all dashboard data
    const [metrics, campaigns, activity] = await Promise.all([
      fetch(`${baseURL}/dashboard/metrics/`, { headers }).then(r => r.json()),
      fetch(`${baseURL}/campaigns/summary/`, { headers }).then(r => r.json()),
      fetch(`${baseURL}/activity/recent/`, { headers }).then(r => r.json())
    ]);

    return {
      metrics: metrics.data,
      campaigns: campaigns.summary.recent_campaigns,
      activity: activity.data.activities
    };
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return null;
  }
}

// Usage
const dashboardData = await fetchDashboardData('your-jwt-token');
if (dashboardData) {
  // Update your dashboard UI with the data
  updateDashboard(dashboardData);
}
```

---

## Current Data in Your System

Based on the API responses, your dashboard shows:

- **Total Messages**: 2 (Last 30 days)
- **Active Contacts**: 1 (Engaged this month)  
- **Campaign Success**: 98.0% (Delivery rate)
- **Sender ID**: 2 (Approved sender names)

- **Recent Campaign**: "Welcome Campaign" - WhatsApp - Completed - 100 sent, 98 delivered
- **Recent Activity**: 4 activities including message sent, campaign completed, contact added

This matches exactly what's shown in your dashboard image!
