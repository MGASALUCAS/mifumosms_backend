# Dashboard Metrics Configuration

## 🎯 Required Dashboard Metrics

Based on your dashboard image, here are the exact 4 metrics you want to display:

### 1. Total Messages
- **Display**: "1" message sent
- **Period**: "Last 30 days"
- **API Field**: `total_messages.value`
- **Description**: Total messages sent in the last 30 days

### 2. Active Contacts  
- **Display**: "0" contacts
- **Period**: "Engaged this month"
- **API Field**: `active_contacts.value`
- **Description**: Number of contacts that have engaged this month

### 3. Campaign Success
- **Display**: "0%" 
- **Period**: "Delivery rate"
- **API Field**: `campaign_success.value`
- **Description**: Campaign delivery success rate percentage

### 4. Sender ID
- **Display**: "0"
- **Period**: "Registered"
- **API Field**: `sender_ids.value`
- **Description**: Number of registered Sender IDs

---

## 📊 API Endpoint

**Endpoint**: `GET /api/messaging/dashboard/metrics/`

**Response Structure**:
```json
{
  "success": true,
  "data": {
    "total_messages": {
      "value": 1,
      "change": "+0%",
      "change_type": "neutral",
      "description": "Last 30 days"
    },
    "active_contacts": {
      "value": 0,
      "change": "+0%",
      "change_type": "neutral",
      "description": "Engaged this month"
    },
    "campaign_success": {
      "value": "0%",
      "change": "+0%",
      "change_type": "neutral",
      "description": "Delivery rate"
    },
    "sender_ids": {
      "value": 0,
      "change": "+0",
      "change_type": "neutral",
      "description": "Registered"
    }
  }
}
```

---

## 🎨 Frontend Implementation

### React Component
```jsx
import React, { useState, useEffect } from 'react';

const DashboardMetrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/messaging/dashboard/metrics/', {
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'),
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        
        if (data.success) {
          setMetrics(data.data);
        }
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return <div className="loading">Loading metrics...</div>;
  }

  if (!metrics) {
    return <div className="error">Failed to load metrics</div>;
  }

  return (
    <div className="dashboard-metrics">
      <div className="metrics-grid">
        <MetricCard
          title="Total Messages"
          value={metrics.total_messages.value}
          period={metrics.total_messages.description}
          change={metrics.total_messages.change}
          changeType={metrics.total_messages.change_type}
        />
        <MetricCard
          title="Active Contacts"
          value={metrics.active_contacts.value}
          period={metrics.active_contacts.description}
          change={metrics.active_contacts.change}
          changeType={metrics.active_contacts.change_type}
        />
        <MetricCard
          title="Campaign Success"
          value={metrics.campaign_success.value}
          period={metrics.campaign_success.description}
          change={metrics.campaign_success.change}
          changeType={metrics.campaign_success.change_type}
        />
        <MetricCard
          title="Sender ID"
          value={metrics.sender_ids.value}
          period={metrics.sender_ids.description}
          change={metrics.sender_ids.change}
          changeType={metrics.sender_ids.change_type}
        />
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, period, change, changeType }) => {
  const changeClass = changeType === 'positive' ? 'positive' : 
                     changeType === 'negative' ? 'negative' : 'neutral';

  return (
    <div className="metric-card">
      <div className="metric-header">
        <h3 className="metric-title">{title}</h3>
        <span className={`metric-change ${changeClass}`}>{change}</span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-period">{period}</div>
    </div>
  );
};

export default DashboardMetrics;
```

### CSS Styles
```css
.dashboard-metrics {
  padding: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.metric-title {
  font-size: 14px;
  color: #666;
  margin: 0;
  font-weight: 500;
}

.metric-change {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.metric-change.positive {
  color: #10b981;
  background-color: #d1fae5;
}

.metric-change.negative {
  color: #ef4444;
  background-color: #fee2e2;
}

.metric-change.neutral {
  color: #6b7280;
  background-color: #f3f4f6;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #111;
  margin-bottom: 5px;
}

.metric-period {
  font-size: 12px;
  color: #666;
}
```

---

## 🔄 Auto-Refresh

### Refresh every 30 seconds
```javascript
useEffect(() => {
  const fetchMetrics = async () => {
    // ... fetch logic
  };

  // Initial fetch
  fetchMetrics();

  // Set up auto-refresh
  const interval = setInterval(fetchMetrics, 30000);

  // Cleanup
  return () => clearInterval(interval);
}, []);
```

---

## 📱 Mobile Responsive

### CSS Grid for Mobile
```css
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .metric-card {
    padding: 15px;
  }
  
  .metric-value {
    font-size: 24px;
  }
}
```

---

## 🎯 Summary

This configuration shows exactly the 4 metrics from your dashboard image:
1. **Total Messages** (Last 30 days)
2. **Active Contacts** (Engaged this month)  
3. **Campaign Success** (Delivery rate)
4. **Sender ID** (Registered)

The API endpoint `/api/messaging/dashboard/metrics/` provides all the data needed to display these metrics with proper formatting and change indicators.

