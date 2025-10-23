# Frontend Integration JSON Script

## 🚀 Complete Frontend Integration Guide

This document provides comprehensive JSON scripts and examples for integrating all the new backend endpoints with your frontend application.

---

## 📱 **1. Bulk Contact Operations**

### **Bulk Edit Contacts**
```javascript
// Request
const bulkEditContacts = async (contactIds, updates) => {
  const response = await fetch('/api/messaging/contacts/bulk-edit/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contact_ids: contactIds,
      updates: updates
    })
  });
  return await response.json();
};

// Example Usage
const result = await bulkEditContacts(
  [1, 2, 3], // Contact IDs
  {
    first_name: "Updated Name",
    last_name: "Updated Last Name",
    tags: ["updated", "bulk"]
  }
);

// Expected Response
{
  "success": true,
  "message": "Successfully updated 3 contacts",
  "data": {
    "updated_count": 3,
    "updated_contacts": [
      {
        "id": 1,
        "first_name": "Updated Name",
        "last_name": "Updated Last Name",
        "phone_e164": "+255712345678",
        "email": "contact1@example.com",
        "tags": ["updated", "bulk"]
      }
    ],
    "errors": []
  }
}
```

### **Bulk Delete Contacts**
```javascript
// Request
const bulkDeleteContacts = async (contactIds) => {
  const response = await fetch('/api/messaging/contacts/bulk-delete/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contact_ids: contactIds
    })
  });
  return await response.json();
};

// Example Usage
const result = await bulkDeleteContacts([1, 2, 3]);

// Expected Response
{
  "success": true,
  "message": "Successfully deleted 3 contacts",
  "data": {
    "deleted_count": 3,
    "deleted_contacts": [1, 2, 3],
    "errors": []
  }
}
```

### **CSV/Excel Bulk Import**
```javascript
// Request - CSV Data
const importCSVContacts = async (csvData) => {
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      import_type: 'csv',
      csv_data: csvData,
      skip_duplicates: true,
      update_existing: false
    })
  });
  return await response.json();
};

// Example Usage - CSV Format (matches the image format)
const csvData = `name,phone,local_number
John Mkumbo,+255672883530,672883530
Fatma Mbwana,+255771978307,771978307
Juma Shaaban,+255712345678,712345678
Gloria Kimaro,+255765432109,765432109
Hassan Ndallahwa,+255789012345,789012345`;

const result = await importCSVContacts(csvData);

// Expected Response
{
  "success": true,
  "message": "Successfully imported 5 contacts",
  "imported": 5,
  "updated": 0,
  "skipped": 0,
  "total_processed": 5,
  "errors": []
}
```

### **Phone Contact Picker Import**
```javascript
// Request
const importPhoneContacts = async (contacts) => {
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      import_type: 'phone_contacts',
      contacts: contacts,
      skip_duplicates: true,
      update_existing: false
    })
  });
  return await response.json();
};

// Example Usage
const result = await importPhoneContacts([
  {
    full_name: "John Doe",
    phone: "+255712345678",
    email: "john@example.com"
  },
  {
    full_name: "Jane Smith",
    phone: "+255712345679",
    email: "jane@example.com"
  }
]);

// Expected Response
{
  "success": true,
  "message": "Successfully imported 2 contacts",
  "imported": 2,
  "updated": 0,
  "skipped": 0,
  "total_processed": 2,
  "errors": []
}
```

---

## 👤 **2. User Profile Settings**

### **Profile Information**
```javascript
// Get Profile
const getProfile = async () => {
  const response = await fetch('/api/accounts/settings/profile/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Update Profile
const updateProfile = async (profileData) => {
  const response = await fetch('/api/accounts/settings/profile/', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(profileData)
  });
  return await response.json();
};

// Example Usage
const profile = await getProfile();
const updatedProfile = await updateProfile({
  first_name: "John",
  last_name: "Doe",
  phone: "+255712345678"
});

// Expected Response
{
  "success": true,
  "data": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+255712345678",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### **User Preferences**
```javascript
// Get Preferences
const getPreferences = async () => {
  const response = await fetch('/api/accounts/settings/preferences/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Update Preferences
const updatePreferences = async (preferences) => {
  const response = await fetch('/api/accounts/settings/preferences/', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(preferences)
  });
  return await response.json();
};

// Example Usage
const preferences = await updatePreferences({
  language: "en",
  timezone: "Africa/Dar_es_Salaam",
  date_format: "DD/MM/YYYY",
  time_format: "24h"
});

// Expected Response
{
  "success": true,
  "data": {
    "language": "en",
    "timezone": "Africa/Dar_es_Salaam",
    "date_format": "DD/MM/YYYY",
    "time_format": "24h",
    "theme": "light"
  }
}
```

### **Notification Settings**
```javascript
// Get Notification Settings
const getNotificationSettings = async () => {
  const response = await fetch('/api/accounts/settings/notifications/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Update Notification Settings
const updateNotificationSettings = async (settings) => {
  const response = await fetch('/api/accounts/settings/notifications/', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
  return await response.json();
};

// Example Usage
const notificationSettings = await updateNotificationSettings({
  email_notifications: true,
  sms_notifications: false,
  push_notifications: true,
  marketing_emails: false
});

// Expected Response
{
  "success": true,
  "data": {
    "email_notifications": true,
    "sms_notifications": false,
    "push_notifications": true,
    "marketing_emails": false,
    "notification_frequency": "immediate"
  }
}
```

---

## 🔐 **3. Password Reset**

### **Forgot Password**
```javascript
// Request Password Reset
const forgotPassword = async (email) => {
  const response = await fetch('/api/accounts/forgot-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email })
  });
  return await response.json();
};

// Example Usage
const result = await forgotPassword("user@example.com");

// Expected Response
{
  "success": true,
  "message": "Password reset email sent successfully",
  "data": {
    "email": "user@example.com",
    "reset_token": "abc123...",
    "expires_at": "2024-01-15T11:30:00Z"
  }
}
```

### **Reset Password**
```javascript
// Reset Password
const resetPassword = async (token, newPassword) => {
  const response = await fetch('/api/accounts/password/reset/confirm/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      token: token,
      new_password: newPassword
    })
  });
  return await response.json();
};

// Example Usage
const result = await resetPassword("abc123...", "newpassword123");

// Expected Response
{
  "success": true,
  "message": "Password reset successfully",
  "data": {
    "user_id": 1,
    "email": "user@example.com"
  }
}
```

---

## 📝 **4. Message Template Management**

### **Template CRUD Operations**
```javascript
// Get Templates
const getTemplates = async (filters = {}) => {
  const queryParams = new URLSearchParams(filters);
  const response = await fetch(`/api/messaging/templates/?${queryParams}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Create Template
const createTemplate = async (templateData) => {
  const response = await fetch('/api/messaging/templates/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(templateData)
  });
  return await response.json();
};

// Update Template
const updateTemplate = async (templateId, updates) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });
  return await response.json();
};

// Delete Template
const deleteTemplate = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example Usage
const templates = await getTemplates({
  category: 'marketing',
  status: 'approved',
  search: 'welcome'
});

const newTemplate = await createTemplate({
  name: "Welcome Message",
  body_text: "Welcome {{first_name}}! Your account is ready.",
  category: "marketing",
  language: "en",
  channel: "sms"
});

// Expected Response
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "name": "Welcome Message",
        "body_text": "Welcome {{first_name}}! Your account is ready.",
        "category": "marketing",
        "language": "en",
        "channel": "sms",
        "status": "approved",
        "is_favorite": false,
        "usage_count": 0,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "count": 1,
    "next": null,
    "previous": null
  }
}
```

### **Template Actions**
```javascript
// Toggle Favorite
const toggleFavorite = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/toggle-favorite/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Increment Usage
const incrementUsage = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/increment-usage/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Approve Template
const approveTemplate = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/approve/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Copy Template
const copyTemplate = async (templateId, newName) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/copy/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name: newName })
  });
  return await response.json();
};

// Get Template Variables
const getTemplateVariables = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/variables/`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example Usage
const favoriteResult = await toggleFavorite(1);
const usageResult = await incrementUsage(1);
const approveResult = await approveTemplate(1);
const copyResult = await copyTemplate(1, "Welcome Message Copy");
const variables = await getTemplateVariables(1);

// Expected Response (Toggle Favorite)
{
  "success": true,
  "message": "Template favorite status updated",
  "data": {
    "template_id": 1,
    "is_favorite": true
  }
}
```

---

## 📊 **5. Activity & Performance Dashboard**

### **Recent Activity**
```javascript
// Get Recent Activity
const getRecentActivity = async (limit = 10) => {
  const response = await fetch(`/api/messaging/activity/recent/?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example Usage
const activity = await getRecentActivity(10);

// Expected Response
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": 1,
        "type": "conversation_reply",
        "title": "New message received",
        "description": "John Doe replied to your message",
        "timestamp": "2024-01-15T10:30:00Z",
        "is_live": true,
        "metadata": {
          "conversation_id": 1,
          "contact_name": "John Doe",
          "message_preview": "Hello, how can I help you?"
        }
      }
    ],
    "total_count": 1,
    "has_more": false
  }
}
```

### **Performance Overview**
```javascript
// Get Performance Overview
const getPerformanceOverview = async () => {
  const response = await fetch('/api/messaging/performance/overview/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example Usage
const performance = await getPerformanceOverview();

// Expected Response
{
  "success": true,
  "data": {
    "delivery_rate": 95.5,
    "response_rate": 78.2,
    "active_conversations": 12,
    "total_messages_sent": 1250,
    "total_messages_received": 890,
    "average_response_time": "2.5 minutes",
    "chart_data": {
      "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "datasets": [
        {
          "label": "Messages Sent",
          "data": [120, 150, 180, 200, 160, 140, 100]
        }
      ]
    }
  }
}
```

### **Activity Statistics**
```javascript
// Get Activity Statistics
const getActivityStatistics = async (period = 'today') => {
  const response = await fetch(`/api/messaging/activity/statistics/?period=${period}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  return await response.json();
};

// Example Usage
const stats = await getActivityStatistics('week');

// Expected Response
{
  "success": true,
  "data": {
    "period": "week",
    "total_activities": 45,
    "activities_by_type": {
      "conversation_reply": 20,
      "campaign_completed": 5,
      "contact_imported": 15,
      "template_created": 5
    },
    "chart_data": {
      "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "datasets": [
        {
          "label": "Activities",
          "data": [5, 8, 12, 15, 10, 3, 2]
        }
      ]
    }
  }
}
```

---

## 🔧 **6. Complete Frontend Integration Example**

### **Main API Service Class**
```javascript
class MifumoSMSAPI {
  constructor(baseURL, accessToken) {
    this.baseURL = baseURL;
    this.accessToken = accessToken;
  }

  // Helper method for making requests
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    const response = await fetch(url, config);
    return await response.json();
  }

  // Bulk Operations
  async bulkEditContacts(contactIds, updates) {
    return this.makeRequest('/api/messaging/contacts/bulk-edit/', {
      method: 'POST',
      body: JSON.stringify({ contact_ids: contactIds, updates })
    });
  }

  async bulkDeleteContacts(contactIds) {
    return this.makeRequest('/api/messaging/contacts/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ contact_ids: contactIds })
    });
  }

  async importCSVContacts(csvData, options = {}) {
    return this.makeRequest('/api/messaging/contacts/bulk-import/', {
      method: 'POST',
      body: JSON.stringify({
        import_type: 'csv',
        csv_data: csvData,
        skip_duplicates: options.skipDuplicates || true,
        update_existing: options.updateExisting || false
      })
    });
  }

  async importPhoneContacts(contacts, options = {}) {
    return this.makeRequest('/api/messaging/contacts/bulk-import/', {
      method: 'POST',
      body: JSON.stringify({
        import_type: 'phone_contacts',
        contacts,
        skip_duplicates: options.skipDuplicates || true,
        update_existing: options.updateExisting || false
      })
    });
  }

  // User Settings
  async getProfile() {
    return this.makeRequest('/api/accounts/settings/profile/');
  }

  async updateProfile(profileData) {
    return this.makeRequest('/api/accounts/settings/profile/', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  }

  async getPreferences() {
    return this.makeRequest('/api/accounts/settings/preferences/');
  }

  async updatePreferences(preferences) {
    return this.makeRequest('/api/accounts/settings/preferences/', {
      method: 'PUT',
      body: JSON.stringify(preferences)
    });
  }

  async getNotificationSettings() {
    return this.makeRequest('/api/accounts/settings/notifications/');
  }

  async updateNotificationSettings(settings) {
    return this.makeRequest('/api/accounts/settings/notifications/', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  // Password Reset
  async forgotPassword(email) {
    return this.makeRequest('/api/accounts/forgot-password/', {
      method: 'POST',
      body: JSON.stringify({ email })
    });
  }

  async resetPassword(token, newPassword) {
    return this.makeRequest('/api/accounts/password/reset/confirm/', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword })
    });
  }

  // Template Management
  async getTemplates(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    return this.makeRequest(`/api/messaging/templates/?${queryParams}`);
  }

  async createTemplate(templateData) {
    return this.makeRequest('/api/messaging/templates/', {
      method: 'POST',
      body: JSON.stringify(templateData)
    });
  }

  async updateTemplate(templateId, updates) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async deleteTemplate(templateId) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/`, {
      method: 'DELETE'
    });
  }

  async toggleTemplateFavorite(templateId) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/toggle-favorite/`, {
      method: 'POST'
    });
  }

  async incrementTemplateUsage(templateId) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/increment-usage/`, {
      method: 'POST'
    });
  }

  async approveTemplate(templateId) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/approve/`, {
      method: 'POST'
    });
  }

  async copyTemplate(templateId, newName) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/copy/`, {
      method: 'POST',
      body: JSON.stringify({ name: newName })
    });
  }

  async getTemplateVariables(templateId) {
    return this.makeRequest(`/api/messaging/templates/${templateId}/variables/`);
  }

  // Activity & Performance
  async getRecentActivity(limit = 10) {
    return this.makeRequest(`/api/messaging/activity/recent/?limit=${limit}`);
  }

  async getPerformanceOverview() {
    return this.makeRequest('/api/messaging/performance/overview/');
  }

  async getActivityStatistics(period = 'today') {
    return this.makeRequest(`/api/messaging/activity/statistics/?period=${period}`);
  }
}

// Usage Example
const api = new MifumoSMSAPI('https://mifumosms.servehttp.com', 'your-access-token');

// Example: Get all templates
const templates = await api.getTemplates({ category: 'marketing' });

// Example: Create a new template
const newTemplate = await api.createTemplate({
  name: "Welcome Message",
  body_text: "Welcome {{first_name}}! Your account is ready.",
  category: "marketing",
  language: "en",
  channel: "sms"
});

// Example: Get recent activity
const activity = await api.getRecentActivity(10);
```

---

## 🎯 **7. Error Handling**

### **Standard Error Response Format**
```javascript
// All endpoints return errors in this format
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "message": "Enter a valid email address"
    }
  }
}

// Common Error Codes
const ERROR_CODES = {
  VALIDATION_ERROR: 'Invalid input data',
  AUTHENTICATION_ERROR: 'Authentication required',
  PERMISSION_ERROR: 'Insufficient permissions',
  NOT_FOUND: 'Resource not found',
  RATE_LIMIT_ERROR: 'Too many requests',
  SERVER_ERROR: 'Internal server error'
};

// Error Handling Helper
const handleAPIError = (error) => {
  if (error.success === false) {
    switch (error.error.code) {
      case 'VALIDATION_ERROR':
        console.error('Validation Error:', error.error.message);
        break;
      case 'AUTHENTICATION_ERROR':
        console.error('Authentication Error:', error.error.message);
        // Redirect to login
        break;
      case 'PERMISSION_ERROR':
        console.error('Permission Error:', error.error.message);
        break;
      default:
        console.error('API Error:', error.error.message);
    }
  }
};
```

---

## 🚀 **8. Frontend Integration Checklist**

### **Required Dependencies**
```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.0.0",
    "react-router-dom": "^6.0.0",
    "react-query": "^3.0.0"
  }
}
```

### **Environment Variables**
```javascript
// .env
REACT_APP_API_BASE_URL=https://mifumosms.servehttp.com
REACT_APP_API_VERSION=v1
```

### **API Configuration**
```javascript
// config/api.js
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001',
  VERSION: process.env.REACT_APP_API_VERSION || 'v1',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
};
```

---

## ✅ **Ready for Implementation!**

This JSON script provides everything your frontend needs to integrate with the new backend endpoints. All endpoints are fully documented with request/response examples, error handling, and complete integration code.

**Key Features:**
- ✅ Complete API integration examples
- ✅ Error handling patterns
- ✅ TypeScript-ready code
- ✅ React/JavaScript examples
- ✅ Comprehensive documentation
- ✅ Ready-to-use service classes

**Next Steps:**
1. Copy the relevant code snippets
2. Adapt to your frontend framework
3. Implement error handling
4. Test with your backend
5. Deploy and enjoy! 🚀
