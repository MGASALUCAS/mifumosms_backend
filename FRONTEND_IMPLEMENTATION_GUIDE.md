# Frontend Implementation Guide - Mifumo WMS API Endpoints

This guide provides all the API endpoints and their JSON responses for frontend implementation.

## Base Configuration

```javascript
const API_BASE_URL = 'http://127.0.0.1:8001/api';
const AUTH_TOKEN = 'your-jwt-token-here';

const apiHeaders = {
  'Authorization': `Bearer ${AUTH_TOKEN}`,
  'Content-Type': 'application/json'
};
```

## 1. Authentication Endpoints

### Login
```javascript
// POST /api/auth/login/
const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
};

// Response:
{
  "message": "Login successful",
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "user": {
    "id": 63,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "is_staff": false,
    "is_superuser": false
  }
}
```

### Profile Settings
```javascript
// GET /api/auth/settings/profile/
const getProfile = async () => {
  const response = await fetch(`${API_BASE_URL}/auth/settings/profile/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "id": 63,
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2025-10-19T15:39:18.588437Z",
  "last_login": "2025-10-22T20:08:45.662467+03:00"
}
```

## 2. Dashboard Endpoints

### Dashboard Overview
```javascript
// GET /api/messaging/dashboard/overview/
const getDashboardOverview = async () => {
  const response = await fetch(`${API_BASE_URL}/messaging/dashboard/overview/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "metrics": {
      "total_messages": 2,
      "total_sms_messages": 0,
      "active_contacts": 1,
      "campaign_success_rate": 96.0,
      "sms_delivery_rate": 0,
      "current_credits": 95,
      "total_purchased": 0,
      "sender_ids_this_month": 1
    },
    "recent_campaigns": [
      {
        "id": "84274522-52ae-4820-81d8-10588c0ae1f5",
        "name": "Test Campaign",
        "type": "WhatsApp",
        "status": "completed",
        "sent": 50,
        "delivered": 48,
        "opened": 0,
        "progress": 100,
        "created_at": "2025-10-22 20:09",
        "created_at_human": "Just now"
      }
    ],
    "message_stats": {
      "today": 2,
      "this_week": 2,
      "this_month": 2,
      "growth_rate": 0.0
    },
    "sms_stats": {
      "today": 0,
      "this_month": 0,
      "delivery_rate": 0
    },
    "contact_stats": {
      "total": 1,
      "active": 1,
      "new_this_month": 1,
      "growth_rate": 0.0
    },
    "billing_stats": {
      "current_credits": 95,
      "total_purchased": 0,
      "credits_used": -95
    },
    "last_updated": "2025-10-22T20:09:58.245364+00:00"
  }
}
```

### Dashboard Metrics
```javascript
// GET /api/messaging/dashboard/metrics/
const getDashboardMetrics = async () => {
  const response = await fetch(`${API_BASE_URL}/messaging/dashboard/metrics/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "message_volume": {
      "today": 2,
      "this_week": 2,
      "this_month": 2,
      "last_month": 0,
      "growth_rate": 0.0
    },
    "contact_growth": {
      "total": 1,
      "new_this_month": 1,
      "growth_rate": 0.0
    },
    "campaign_performance": {
      "total_campaigns": 1,
      "completed_campaigns": 1,
      "success_rate": 96.0
    },
    "sms_usage": {
      "total_sent": 0,
      "delivered": 0,
      "failed": 0,
      "delivery_rate": 0.0
    }
  }
}
```

## 3. Recent Activity

### Recent Activity Feed
```javascript
// GET /api/messaging/activity/recent/
const getRecentActivity = async () => {
  const response = await fetch(`${API_BASE_URL}/messaging/activity/recent/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "msg_f5dc6c0b-c718-4958-aa19-7edca14e8910",
        "type": "message_sent",
        "title": "Message sent to Sarah Mwangi",
        "description": "New message: Thank you for using our service!",
        "timestamp": "2025-10-22T20:09:49.612068+00:00",
        "time_ago": "Just now",
        "is_live": true,
        "metadata": {
          "conversation_id": "4fdea49d-5e2a-45a5-be9b-21aaa4515931",
          "contact_name": "Sarah Mwangi",
          "conversation_subject": "Test Conversation",
          "message_id": "f5dc6c0b-c718-4958-aa19-7edca14e8910"
        }
      },
      {
        "id": "msg_0bd8b94b-74e6-48ee-9d8d-22d5e2779105",
        "type": "message_sent",
        "title": "Message sent to Sarah Mwangi",
        "description": "New message: Hello from Mifumo WMS!",
        "timestamp": "2025-10-22T20:09:49.547979+00:00",
        "time_ago": "Just now",
        "is_live": true,
        "metadata": {
          "conversation_id": "4fdea49d-5e2a-45a5-be9b-21aaa4515931",
          "contact_name": "Sarah Mwangi",
          "conversation_subject": "Test Conversation",
          "message_id": "0bd8b94b-74e6-48ee-9d8d-22d5e2779105"
        }
      },
      {
        "id": "camp_84274522-52ae-4820-81d8-10588c0ae1f5",
        "type": "campaign_completed",
        "title": "System completed campaign Test Campaign",
        "description": "96% delivered",
        "timestamp": "2025-10-22T20:09:31.204334+00:00",
        "time_ago": "Just now",
        "is_live": false,
        "metadata": {
          "campaign_id": "84274522-52ae-4820-81d8-10588c0ae1f5",
          "campaign_name": "Test Campaign",
          "delivery_rate": 96,
          "sent_count": 50,
          "delivered_count": 48
        }
      },
      {
        "id": "contact_e0f56ffe-1171-4361-8b96-994c6826ac9c",
        "type": "contact_added",
        "title": "Sarah Mwangi added to contacts",
        "description": "New contact: +255700000001",
        "timestamp": "2025-10-22T20:09:31.102024+00:00",
        "time_ago": "Just now",
        "is_live": false,
        "metadata": {
          "contact_id": "e0f56ffe-1171-4361-8b96-994c6826ac9c",
          "contact_name": "Sarah Mwangi",
          "phone": "+255700000001"
        }
      }
    ],
    "has_more": false,
    "total_count": 4,
    "live_count": 2
  }
}
```

## 4. Performance Overview

### Performance Metrics
```javascript
// GET /api/messaging/performance/overview/
const getPerformanceOverview = async () => {
  const response = await fetch(`${API_BASE_URL}/messaging/performance/overview/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "metrics": {
      "total_messages": 2,
      "delivery_rate": 100.0,
      "response_rate": 0.0,
      "active_conversations": 1,
      "campaign_success_rate": 96.0
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

## 5. Sender ID Management

### Sender ID Statistics
```javascript
// GET /api/messaging/sender-requests/stats/
const getSenderStats = async () => {
  const response = await fetch(`${API_BASE_URL}/messaging/sender-requests/stats/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "stats": {
      "total_requests": 2,
      "pending_requests": 0,
      "approved_requests": 2,
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
      "total_active": 1,
      "active_sender_ids": [
        {
          "id": "22a40828-20b7-486c-a167-932bb202cd7c",
          "sender_id": "Taarifa-SMS",
          "status": "active",
          "created_at": "2025-10-19T15:39:18.588437Z"
        }
      ]
    },
    "recent_requests": [
      {
        "id": "f8256635-aa91-4f7e-9e83-cd465bb8c8ef",
        "tenant": "950555b7-e162-482f-a115-2a4600dd1fd3",
        "user": 63,
        "request_type": "default",
        "requested_sender_id": "Taarifa-SMS",
        "sample_content": "A test use case for the sender name purposely used for information transfer.",
        "status": "approved",
        "reviewed_by": null,
        "reviewed_at": null,
        "rejection_reason": "",
        "sms_package": null,
        "created_at": "2025-10-22T20:08:45.662467+03:00",
        "updated_at": "2025-10-22T20:08:45.662491+03:00",
        "user_email": "test@example.com",
        "user_id": 63,
        "tenant_name": "Test Tenant",
        "sender_name": "Taarifa-SMS",
        "use_case": "A test use case for the sender name purposely used for information transfer."
      }
    ]
  }
}
```

## 6. SMS Balance

### SMS Balance
```javascript
// GET /api/billing/sms/balance/
const getSMSBalance = async () => {
  const response = await fetch(`${API_BASE_URL}/billing/sms/balance/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "id": "af98501d-1e17-4801-8aa6-6484be5f9b5c",
  "tenant": "Test Tenant",
  "credits": 95,
  "total_purchased": 0,
  "total_used": 5,
  "last_updated": "2025-10-19T18:09:05.138637+03:00",
  "created_at": "2025-10-19T18:09:05.093642+03:00"
}
```

## 7. Contacts Management

### List Contacts
```javascript
// GET /api/messaging/contacts/
const getContacts = async () => {
  const response = await fetch(`${API_BASE_URL}/messaging/contacts/`, {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "e0f56ffe-1171-4361-8b96-994c6826ac9c",
      "name": "Sarah Mwangi",
      "phone_e164": "+255700000001",
      "email": "sarah@example.com",
      "attributes": {},
      "tags": [],
      "opt_in_at": null,
      "opt_out_at": null,
      "opt_out_reason": "",
      "is_active": true,
      "last_contacted_at": null,
      "is_opted_in": true,
      "created_by": "test@example.com",
      "created_by_id": 63,
      "created_at": "2025-10-22T20:09:31.102024+00:00",
      "updated_at": "2025-10-22T20:09:31.102024+00:00"
    }
  ]
}
```

## 8. Error Handling

### Common Error Responses
```javascript
// 400 Bad Request
{
  "success": false,
  "message": "User is not associated with any tenant. Please contact support."
}

// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}

// 404 Not Found
{
  "detail": "Not found."
}

// 500 Internal Server Error
{
  "success": false,
  "message": "Failed to retrieve dashboard data",
  "error": "Error details here"
}
```

## 9. Frontend Implementation Examples

### React Hook for Dashboard Data
```javascript
import { useState, useEffect } from 'react';

const useDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/messaging/dashboard/overview/`, {
          headers: apiHeaders
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data');
        }
        
        const data = await response.json();
        setDashboardData(data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return { dashboardData, loading, error };
};
```

### Activity Feed Component
```javascript
const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/messaging/activity/recent/`, {
          headers: apiHeaders
        });
        const data = await response.json();
        setActivities(data.data.activities);
      } catch (error) {
        console.error('Failed to fetch activities:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
  }, []);

  if (loading) return <div>Loading activities...</div>;

  return (
    <div className="activity-feed">
      {activities.map(activity => (
        <div key={activity.id} className={`activity-item ${activity.is_live ? 'live' : ''}`}>
          <h4>{activity.title}</h4>
          <p>{activity.description}</p>
          <span className="time-ago">{activity.time_ago}</span>
        </div>
      ))}
    </div>
  );
};
```

### Sender ID Stats Component
```javascript
const SenderIDStats = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/messaging/sender-requests/stats/`, {
          headers: apiHeaders
        });
        const data = await response.json();
        setStats(data.data);
      } catch (error) {
        console.error('Failed to fetch sender stats:', error);
      }
    };

    fetchStats();
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="sender-stats">
      <div className="stat-card">
        <h3>Sender IDs</h3>
        <div className="stat-number">{stats.active_stats.total_active}</div>
        <p>Active sender names</p>
      </div>
      
      <div className="stat-card">
        <h3>Requests</h3>
        <div className="stat-number">{stats.stats.total_requests}</div>
        <p>Total requests</p>
      </div>
    </div>
  );
};
```

## 10. Important Notes

1. **Authentication**: Always include the JWT token in the Authorization header
2. **Error Handling**: Check response status and handle errors appropriately
3. **Loading States**: Implement loading states for better UX
4. **Data Refresh**: Consider implementing auto-refresh for real-time data
5. **Caching**: Consider caching API responses to reduce server load
6. **Rate Limiting**: Be aware of API rate limits and implement appropriate delays

## 11. API Base URL Configuration

Make sure to update the API base URL for different environments:

```javascript
// Development
const API_BASE_URL = 'http://127.0.0.1:8001/api';

// Production
const API_BASE_URL = 'https://your-domain.com/api';

// Staging
const API_BASE_URL = 'https://staging.your-domain.com/api';
```

This guide provides all the necessary information to implement the frontend dashboard with proper API integration.
