# Notification System API Endpoints

## Overview

The notification system provides comprehensive notification management for the Mifumo WMS platform, including:

- **Real-time notifications** displayed in the user header
- **SMS credit monitoring** with automatic low-balance alerts
- **System-wide notifications** for administrators
- **Email and SMS delivery** based on user preferences
- **Notification templates** for consistent messaging
- **User notification settings** for customization

## Base URL
```
http://127.0.0.1:8001/api/notifications/
```

## Authentication
All endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 1. Notification Management

### 1.1 List Notifications
**GET** `/api/notifications/`

Get paginated list of notifications for the authenticated user.

**Query Parameters:**
- `status` (optional): Filter by status (`unread`, `read`, `archived`)
- `type` (optional): Filter by notification type
- `priority` (optional): Filter by priority (`low`, `medium`, `high`, `urgent`)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8001/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": "cf5802a6-0111-4367-995e-18d2b590d390",
      "title": "Low SMS Credit Warning",
      "message": "Your SMS credit is running low. You have 15 credits remaining (15.0% of your total).",
      "notification_type": "sms_credit",
      "priority": "medium",
      "status": "unread",
      "data": {
        "current_credits": 15,
        "percentage": 15.0,
        "type": "low_credit"
      },
      "action_url": "/billing/sms/purchase/",
      "action_text": "Buy Credits",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "read_at": null,
      "expires_at": null,
      "is_system": false,
      "is_auto_generated": true,
      "time_ago": "2 minutes ago",
      "is_unread": true
    }
  ]
}
```

### 1.2 Create Notification
**POST** `/api/notifications/`

Create a new notification for the authenticated user.

**Request Body:**
```json
{
  "title": "Test Notification",
  "message": "This is a test notification",
  "notification_type": "info",
  "priority": "medium",
  "data": {
    "custom_field": "value"
  },
  "action_url": "https://example.com",
  "action_text": "View Details",
  "expires_at": "2024-01-16T10:30:00Z"
}
```

**Response:**
```json
{
  "id": "c1ec78c1-e6fb-42e6-bff1-954c36b903b8",
  "title": "Test Notification",
  "message": "This is a test notification",
  "notification_type": "info",
  "priority": "medium",
  "status": "unread",
  "data": {
    "custom_field": "value"
  },
  "action_url": "https://example.com",
  "action_text": "View Details",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "read_at": null,
  "expires_at": "2024-01-16T10:30:00Z",
  "is_system": false,
  "is_auto_generated": false,
  "time_ago": "Just now",
  "is_unread": true
}
```

### 1.3 Get Notification Details
**GET** `/api/notifications/{id}/`

Get details of a specific notification.

**Response:**
```json
{
  "id": "cf5802a6-0111-4367-995e-18d2b590d390",
  "title": "Low SMS Credit Warning",
  "message": "Your SMS credit is running low...",
  "notification_type": "sms_credit",
  "priority": "medium",
  "status": "unread",
  "data": {
    "current_credits": 15,
    "percentage": 15.0
  },
  "action_url": "/billing/sms/purchase/",
  "action_text": "Buy Credits",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "read_at": null,
  "expires_at": null,
  "is_system": false,
  "is_auto_generated": true,
  "time_ago": "2 minutes ago",
  "is_unread": true
}
```

### 1.4 Update Notification
**PUT/PATCH** `/api/notifications/{id}/`

Update a notification (limited fields).

**Request Body:**
```json
{
  "status": "read"
}
```

### 1.5 Delete Notification
**DELETE** `/api/notifications/{id}/`

Delete a notification.

**Response:**
```json
{
  "success": true,
  "message": "Notification deleted successfully"
}
```

---

## 2. Notification Actions

### 2.1 Mark Notification as Read
**POST** `/api/notifications/{id}/mark-read/`

Mark a specific notification as read.

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

### 2.2 Mark All Notifications as Read
**POST** `/api/notifications/mark-all-read/`

Mark all notifications as read for the authenticated user.

**Response:**
```json
{
  "success": true,
  "message": "Marked 5 notifications as read"
}
```

### 2.3 Get Unread Count
**GET** `/api/notifications/unread-count/`

Get the count of unread notifications for the header badge.

**Response:**
```json
{
  "success": true,
  "unread_count": 3
}
```

### 2.4 Get Recent Notifications
**GET** `/api/notifications/recent/`

Get recent notifications for the header dropdown (last 5 unread + 5 recent read).

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "cf5802a6-0111-4367-995e-18d2b590d390",
      "title": "Low SMS Credit Warning",
      "message": "Your SMS credit is running low...",
      "notification_type": "sms_credit",
      "priority": "medium",
      "action_url": "/billing/sms/purchase/",
      "action_text": "Buy Credits",
      "created_at": "2024-01-15T10:30:00Z",
      "time_ago": "2 minutes ago"
    }
  ],
  "unread_count": 3
}
```

---

## 3. Notification Statistics

### 3.1 Get Notification Stats
**GET** `/api/notifications/stats/`

Get comprehensive notification statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 25,
    "unread": 3,
    "by_type": {
      "sms_credit": 5,
      "campaign": 8,
      "contact": 3,
      "billing": 2,
      "system": 7
    },
    "by_priority": {
      "low": 10,
      "medium": 12,
      "high": 2,
      "urgent": 1
    },
    "recent_count": 15
  }
}
```

---

## 4. Notification Settings

### 4.1 Get Notification Settings
**GET** `/api/notifications/settings/`

Get user's notification preferences.

**Response:**
```json
{
  "email_notifications": true,
  "email_sms_credit": true,
  "email_campaigns": true,
  "email_contacts": true,
  "email_billing": true,
  "email_security": true,
  "sms_notifications": false,
  "sms_credit_warning": true,
  "sms_critical": true,
  "in_app_notifications": true,
  "credit_warning_threshold": 25,
  "credit_critical_threshold": 10
}
```

### 4.2 Update Notification Settings
**PATCH** `/api/notifications/settings/`

Update user's notification preferences.

**Request Body:**
```json
{
  "credit_warning_threshold": 30,
  "credit_critical_threshold": 15,
  "email_sms_credit": true,
  "sms_credit_warning": true
}
```

**Response:**
```json
{
  "email_notifications": true,
  "email_sms_credit": true,
  "email_campaigns": true,
  "email_contacts": true,
  "email_billing": true,
  "email_security": true,
  "sms_notifications": false,
  "sms_credit_warning": true,
  "sms_critical": true,
  "in_app_notifications": true,
  "credit_warning_threshold": 30,
  "credit_critical_threshold": 15
}
```

---

## 5. SMS Credit Monitoring

### 5.1 Test SMS Credit Notification
**POST** `/api/notifications/sms-credit/test/`

Test SMS credit notification system (for testing purposes).

**Request Body:**
```json
{
  "current_credits": 15,
  "total_credits": 100
}
```

**Response:**
```json
{
  "success": true,
  "message": "SMS credit notification test completed",
  "current_credits": 15,
  "total_credits": 100,
  "percentage": 15.0
}
```

---

## 6. System Notifications (Admin Only)

### 6.1 Create System Notification
**POST** `/api/notifications/system/create/`

Create system-wide notifications (admin users only).

**Request Body:**
```json
{
  "title": "System Maintenance",
  "message": "Scheduled maintenance will occur tonight from 2 AM to 4 AM.",
  "notification_type": "maintenance",
  "priority": "medium",
  "user_emails": ["user1@example.com", "user2@example.com"],
  "action_url": "https://mifumo.com/announcements",
  "action_text": "Read More"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Created 15 notifications",
  "notifications_created": 15
}
```

---

## 7. Notification Templates

### 7.1 Get Notification Templates
**GET** `/api/notifications/templates/`

Get available notification templates.

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": "uuid-here",
      "name": "sms_credit_low",
      "title_template": "Low SMS Credit Warning",
      "message_template": "Your SMS credit is running low. You have {current_credits} credits remaining ({percentage:.1f}% of your total).",
      "notification_type": "sms_credit",
      "priority": "medium",
      "is_active": true,
      "variables": ["current_credits", "percentage"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 8. Frontend Integration

### 8.1 Header Notification Dropdown

The notification system is designed to work with a header notification dropdown as shown in the image. Here's how to integrate it:

**JavaScript Example:**
```javascript
// Get unread count for badge
async function getUnreadCount() {
  const response = await fetch('/api/notifications/unread-count/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const data = await response.json();
  document.getElementById('notification-badge').textContent = data.unread_count;
}

// Get recent notifications for dropdown
async function getRecentNotifications() {
  const response = await fetch('/api/notifications/recent/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const data = await response.json();
  displayNotifications(data.notifications);
}

// Mark notification as read
async function markAsRead(notificationId) {
  await fetch(`/api/notifications/${notificationId}/mark-read/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  // Refresh notification count
  getUnreadCount();
}

// Display notifications in dropdown
function displayNotifications(notifications) {
  const container = document.getElementById('notification-dropdown');
  container.innerHTML = notifications.map(notification => `
    <div class="notification-item ${notification.is_unread ? 'unread' : ''}">
      <div class="notification-title">${notification.title}</div>
      <div class="notification-message">${notification.message}</div>
      <div class="notification-time">${notification.time_ago}</div>
      ${notification.action_url ? `<a href="${notification.action_url}" class="notification-action">${notification.action_text || 'View'}</a>` : ''}
    </div>
  `).join('');
}
```

### 8.2 CSS Example for Header Dropdown

```css
.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 350px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 1000;
}

.notification-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.notification-item.unread {
  background-color: #f8f9fa;
  border-left: 3px solid #007bff;
}

.notification-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.notification-message {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.notification-time {
  color: #999;
  font-size: 12px;
}

.notification-action {
  color: #007bff;
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
}
```

---

## 9. Notification Types

The system supports the following notification types:

- **`system`** - General system notifications
- **`sms_credit`** - SMS credit-related notifications
- **`campaign`** - Campaign-related notifications
- **`contact`** - Contact management notifications
- **`billing`** - Billing and payment notifications
- **`security`** - Security-related notifications
- **`maintenance`** - System maintenance notifications
- **`error`** - Error notifications
- **`success`** - Success notifications
- **`warning`** - Warning notifications
- **`info`** - Information notifications

## 10. Priority Levels

- **`low`** - Low priority notifications
- **`medium`** - Medium priority notifications (default)
- **`high`** - High priority notifications
- **`urgent`** - Urgent notifications (may trigger SMS)

## 11. Automatic Notifications

The system automatically creates notifications for:

1. **SMS Credit Monitoring**: When credits fall below configured thresholds
2. **Campaign Status**: When campaigns are sent or fail
3. **Contact Import**: When contacts are imported successfully or fail
4. **Billing Events**: When payments succeed or fail
5. **Security Events**: When suspicious login activity is detected
6. **System Events**: For maintenance, errors, and updates

## 12. Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- **200** - Success
- **201** - Created
- **400** - Bad Request (validation errors)
- **401** - Unauthorized (invalid token)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **500** - Internal Server Error

**Error Response Format:**
```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "details": "Additional error details if available"
}
```

---

## 13. Rate Limiting

The notification system includes built-in rate limiting to prevent spam:

- **SMS Credit Notifications**: Maximum 1 per hour per user
- **System Notifications**: No limit for admin users
- **User Notifications**: Maximum 100 per hour per user

---

## 14. Database Cleanup

The system automatically cleans up:

- **Expired notifications** older than their expiration date
- **Read notifications** older than 30 days (configurable)
- **Archived notifications** older than 90 days (configurable)

---

This notification system provides a comprehensive solution for user notifications in the Mifumo WMS platform, with automatic SMS credit monitoring and a user-friendly header dropdown interface.
