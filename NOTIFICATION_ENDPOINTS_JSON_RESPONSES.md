# Notification System - API Endpoints & JSON Responses

## 🔗 **Base URL**
```
http://127.0.0.1:8001/api/notifications/
```

## 📋 **Authentication Required**
All endpoints require JWT authentication:
```http
Authorization: Bearer <your_jwt_token>
```

---

## 1. **Get Recent Notifications** (Header Dropdown)
```http
GET /api/notifications/recent/
```

### **Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "7fe86ae1-b06a-49cb-ba0f-10129a98aeba",
      "title": "System Issue: SMS Service",
      "message": "SMS Service is experiencing issues: SMS success rate is 50.0% (below 80% threshold)",
      "notification_type": "error",
      "priority": "high",
      "status": "unread",
      "is_system": true,
      "is_auto_generated": true,
      "action_text": "View Details",
      "action_url": null,
      "data": {
        "success_rate": 50.0,
        "total_messages": 4,
        "successful_messages": 2
      },
      "created_at": "2025-10-23T10:10:00.840Z",
      "time_ago": "2 hours ago",
      "is_unread": true
    },
    {
      "id": "8fe86ae1-b06a-49cb-ba0f-10129a98aebc",
      "title": "Low SMS Credit Warning",
      "message": "Your SMS credit balance is running low. Current balance: 5.00%. Please top up soon to avoid service interruption.",
      "notification_type": "sms_credit",
      "priority": "medium",
      "status": "read",
      "is_system": false,
      "is_auto_generated": true,
      "action_text": "Top Up Now",
      "action_url": "/billing/top-up",
      "data": {
        "current_credit": "5.00%"
      },
      "created_at": "2025-10-23T09:42:30.829Z",
      "time_ago": "3 hours ago",
      "is_unread": false
    }
  ],
  "unread_count": 1
}
```

---

## 2. **Get Real Notifications** (Comprehensive)
```http
GET /api/notifications/real/?limit=20
```

### **Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "7fe86ae1-b06a-49cb-ba0f-10129a98aeba",
      "title": "System Issue: SMS Service",
      "message": "SMS Service is experiencing issues: SMS success rate is 50.0% (below 80% threshold)",
      "notification_type": "error",
      "priority": "high",
      "status": "unread",
      "is_system": true,
      "is_auto_generated": true,
      "action_text": "View Details",
      "action_url": null,
      "data": {
        "success_rate": 50.0,
        "total_messages": 4,
        "successful_messages": 2
      },
      "created_at": "2025-10-23T10:10:00.840Z",
      "time_ago": "2 hours ago",
      "is_unread": true
    }
  ],
  "count": 1
}
```

---

## 3. **Get Unread Count**
```http
GET /api/notifications/unread-count/
```

### **Response:**
```json
{
  "success": true,
  "unread_count": 3
}
```

---

## 4. **Get Notification Statistics**
```http
GET /api/notifications/stats/
```

### **Response:**
```json
{
  "success": true,
  "data": {
    "total": 15,
    "unread": 3,
    "recent_count": 8,
    "by_type": {
      "error": 2,
      "sms_credit": 5,
      "info": 3,
      "warning": 5
    },
    "by_priority": {
      "high": 2,
      "medium": 8,
      "low": 5
    }
  }
}
```

---

## 5. **Mark Notification as Read**
```http
POST /api/notifications/{notification_id}/mark-read/
```

### **Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

## 6. **Mark All Notifications as Read**
```http
POST /api/notifications/mark-all-read/
```

### **Response:**
```json
{
  "success": true,
  "message": "Marked 3 notifications as read"
}
```

---

## 7. **System Health Check** (Admin Only)
```http
GET /api/notifications/system/health-check/
```

### **Response:**
```json
{
  "success": true,
  "health_status": {
    "healthy": false,
    "issues": [
      {
        "component": "SMS Service",
        "healthy": false,
        "status": "WARNING",
        "error": "SMS success rate is 50.0% (below 80% threshold)",
        "priority": "medium",
        "details": {
          "success_rate": 50.0,
          "total_messages": 4,
          "successful_messages": 2
        }
      }
    ],
    "warnings": [
      {
        "component": "SMS Credits",
        "healthy": false,
        "status": "WARNING",
        "error": "32 tenants have low SMS credits",
        "priority": "medium",
        "details": {
          "low_credit_tenants": 32
        }
      }
    ],
    "timestamp": "2025-10-23T10:15:00.000Z"
  }
}
```

---

## 8. **Report System Problem** (Admin Only)
```http
POST /api/notifications/system/report-problem/
```

### **Request Body:**
```json
{
  "problem_type": "SMS_SERVICE_DOWN",
  "description": "SMS service is experiencing downtime. Messages are not being delivered.",
  "priority": "high",
  "data": {
    "service": "Beem Africa",
    "error_code": "SERVICE_UNAVAILABLE",
    "affected_users": 150
  }
}
```

### **Response:**
```json
{
  "success": true,
  "message": "Problem reported and notification created",
  "notification_id": "9fe86ae1-b06a-49cb-ba0f-10129a98aebd"
}
```

---

## 9. **Create System Notification** (Admin Only)
```http
POST /api/notifications/system/create/
```

### **Request Body:**
```json
{
  "title": "System Maintenance",
  "message": "Scheduled maintenance will occur on 2025-10-24 from 02:00 to 04:00 UTC. Services may be temporarily interrupted.",
  "notification_type": "system",
  "priority": "medium",
  "link": "https://status.mifumo.com",
  "metadata": {
    "maintenance_id": "MAINT-2025-001",
    "affected_services": ["SMS", "API", "Dashboard"]
  }
}
```

### **Response:**
```json
{
  "success": true,
  "message": "System notification created successfully",
  "notification_id": "afe86ae1-b06a-49cb-ba0f-10129a98aebe"
}
```

---

## 10. **Test SMS Credit Notification**
```http
POST /api/notifications/sms-credit/test/
```

### **Request Body:**
```json
{
  "current_credits": 5,
  "total_credits": 100
}
```

### **Response:**
```json
{
  "success": true,
  "message": "SMS credit notification test completed",
  "percentage": 5.0
}
```

---

## 11. **Cleanup Old Notifications** (Admin Only)
```http
POST /api/notifications/system/cleanup/
```

### **Request Body:**
```json
{
  "days": 30
}
```

### **Response:**
```json
{
  "success": true,
  "message": "Cleaned up 5 old notifications",
  "deleted_count": 5
}
```

---

## 12. **Get Notification Settings**
```http
GET /api/notifications/settings/
```

### **Response:**
```json
{
  "success": true,
  "data": {
    "id": "settings-uuid-here",
    "email_notifications_enabled": true,
    "sms_notifications_enabled": false,
    "in_app_notifications_enabled": true,
    "sms_credit_warning_threshold": 25.00,
    "sms_credit_critical_threshold": 10.00,
    "created_at": "2025-10-23T08:00:00.000Z",
    "updated_at": "2025-10-23T10:15:00.000Z"
  }
}
```

---

## 13. **Update Notification Settings**
```http
PUT /api/notifications/settings/
```

### **Request Body:**
```json
{
  "email_notifications_enabled": true,
  "sms_notifications_enabled": true,
  "in_app_notifications_enabled": true,
  "sms_credit_warning_threshold": 30.00,
  "sms_credit_critical_threshold": 15.00
}
```

### **Response:**
```json
{
  "success": true,
  "message": "Notification settings updated successfully",
  "data": {
    "id": "settings-uuid-here",
    "email_notifications_enabled": true,
    "sms_notifications_enabled": true,
    "in_app_notifications_enabled": true,
    "sms_credit_warning_threshold": 30.00,
    "sms_credit_critical_threshold": 15.00,
    "created_at": "2025-10-23T08:00:00.000Z",
    "updated_at": "2025-10-23T10:20:00.000Z"
  }
}
```

---

## 14. **Get Notification Templates** (Admin Only)
```http
GET /api/notifications/templates/
```

### **Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": "template-uuid-here",
      "name": "sms_credit_low",
      "title": "Low SMS Credit Alert",
      "message": "Your SMS credit balance is running low. Current balance: {{ current_credit }}. Please top up soon to avoid service interruption.",
      "notification_type": "sms_credit",
      "priority": "high",
      "is_active": true,
      "created_at": "2025-10-23T08:00:00.000Z",
      "updated_at": "2025-10-23T08:00:00.000Z"
    }
  ]
}
```

---

## 📱 **Frontend Integration Examples**

### **Header Notification Dropdown:**
```javascript
// Fetch recent notifications for header dropdown
const response = await fetch('/api/notifications/recent/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();

// Display notifications
data.notifications.forEach(notification => {
  console.log(`${notification.title} - ${notification.time_ago}`);
  if (notification.is_system) {
    console.log('[SYSTEM]', notification.message);
  }
});

// Show unread count
document.getElementById('notification-badge').textContent = data.unread_count;
```

### **Admin Dashboard Health Check:**
```javascript
// Check system health
const healthResponse = await fetch('/api/notifications/system/health-check/', {
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  }
});
const healthData = await healthResponse.json();

if (!healthData.health_status.healthy) {
  console.log('System Issues:', healthData.health_status.issues.length);
  console.log('Warnings:', healthData.health_status.warnings.length);
}
```

### **Report Problem:**
```javascript
// Report a system problem
const problemData = {
  problem_type: 'PAYMENT_GATEWAY_ERROR',
  description: 'Payment gateway is returning 500 errors for all transactions',
  priority: 'high',
  data: {
    gateway: 'Stripe',
    error_code: '500',
    affected_transactions: 25
  }
};

const reportResponse = await fetch('/api/notifications/system/report-problem/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(problemData)
});
```

---

## 🔧 **Error Responses**

### **Authentication Error:**
```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

### **Permission Error:**
```json
{
  "success": false,
  "error": "Permission denied. Admin access required."
}
```

### **Validation Error:**
```json
{
  "success": false,
  "error": "Problem type and description are required"
}
```

### **Server Error:**
```json
{
  "success": false,
  "error": "Failed to get recent notifications"
}
```

---

## 📊 **Notification Types**

- `error` - System errors and critical issues
- `warning` - Warnings that need attention
- `info` - General information
- `sms_credit` - SMS credit related notifications
- `system` - System maintenance and updates
- `campaign` - SMS campaign related
- `billing` - Payment and billing related
- `security` - Security alerts

## 🎯 **Priority Levels**

- `critical` - Immediate attention required
- `high` - High priority issues
- `medium` - Normal priority
- `low` - Low priority information

---

**All endpoints are now fully functional and ready for frontend integration!** 🚀
