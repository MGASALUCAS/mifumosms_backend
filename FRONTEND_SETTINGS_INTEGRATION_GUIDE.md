# Frontend Settings Integration Guide

## User Settings API Integration for Frontend Developers

This guide provides everything frontend developers need to integrate the User Settings API into their settings template.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Frontend Implementation](#frontend-implementation)
5. [Code Examples](#code-examples)
6. [Error Handling](#error-handling)
7. [UI Components](#ui-components)
8. [Testing](#testing)

---

## 🎯 Overview

The User Settings API allows users to manage their API keys, webhooks, and SMS settings through a comprehensive settings interface. Users can:

- View their API account information
- Create, manage, and revoke API keys
- Set up webhooks for notifications
- Monitor usage statistics
- Send test SMS messages

---

## 🔐 Authentication

### Login Required
All User Settings API endpoints require JWT authentication. Users must be logged in to access their settings.

```javascript
// Example login flow
const loginUser = async (email, password) => {
  const response = await fetch('http://127.0.0.1:8001/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  return data.tokens.access; // JWT token
};
```

### Headers for API Calls
```javascript
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};
```

---

## 🔗 API Endpoints

### Base URL
```
http://127.0.0.1:8001/api/integration
```

### 1. Get API Settings
**GET** `/user/settings/`

Returns user's complete API settings including account info, API keys, and webhooks.

### 2. Get Usage Statistics
**GET** `/user/usage/`

Returns usage statistics for API keys and webhooks.

### 3. Create API Key
**POST** `/user/keys/create/`

Creates a new API key for the user.

### 4. Revoke API Key
**POST** `/user/keys/{key_id}/revoke/`

Revokes an existing API key.

### 5. Regenerate API Key
**POST** `/user/keys/{key_id}/regenerate/`

Generates new credentials for an existing API key.

### 6. Create Webhook
**POST** `/user/webhooks/create/`

Creates a new webhook for notifications.

### 7. Toggle Webhook
**POST** `/user/webhooks/{webhook_id}/toggle/`

Enables or disables a webhook.

### 8. Delete Webhook
**DELETE** `/user/webhooks/{webhook_id}/delete/`

Deletes a webhook.

### 9. Send Test SMS
**POST** `/v1/test-sms/send/`

Sends a test SMS message (simulation).

### 10. Check SMS Status
**GET** `/v1/test-sms/status/{message_id}/`

Checks the status of a sent SMS.

### 11. Check Balance
**GET** `/v1/test-sms/balance/`

Checks account balance.

---

## 💻 Frontend Implementation

### 1. Settings Page Structure

```html
<!-- Settings Template Structure -->
<div class="settings-container">
  <!-- API Account Section -->
  <section class="api-account-section">
    <h2>API Account</h2>
    <div class="account-info">
      <!-- Account details will be populated here -->
    </div>
  </section>

  <!-- API Keys Section -->
  <section class="api-keys-section">
    <h2>API Keys</h2>
    <button id="create-api-key-btn">Create New API Key</button>
    <div class="api-keys-list">
      <!-- API keys will be populated here -->
    </div>
  </section>

  <!-- Webhooks Section -->
  <section class="webhooks-section">
    <h2>Webhooks</h2>
    <button id="create-webhook-btn">Create New Webhook</button>
    <div class="webhooks-list">
      <!-- Webhooks will be populated here -->
    </div>
  </section>

  <!-- Usage Statistics Section -->
  <section class="usage-section">
    <h2>Usage Statistics</h2>
    <div class="usage-stats">
      <!-- Usage stats will be populated here -->
    </div>
  </section>

  <!-- SMS Test Section -->
  <section class="sms-test-section">
    <h2>SMS Test</h2>
    <div class="sms-test-form">
      <!-- SMS test form will be here -->
    </div>
  </section>
</div>
```

### 2. JavaScript API Service

```javascript
class UserSettingsAPI {
  constructor(baseURL = 'http://127.0.0.1:8001/api/integration') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('accessToken');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    localStorage.setItem('accessToken', token);
  }

  // Get headers for API calls
  getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  // Get API settings
  async getSettings() {
    const response = await fetch(`${this.baseURL}/user/settings/`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Get usage statistics
  async getUsage() {
    const response = await fetch(`${this.baseURL}/user/usage/`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Create API key
  async createApiKey(keyData) {
    const response = await fetch(`${this.baseURL}/user/keys/create/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(keyData)
    });
    return response.json();
  }

  // Revoke API key
  async revokeApiKey(keyId) {
    const response = await fetch(`${this.baseURL}/user/keys/${keyId}/revoke/`, {
      method: 'POST',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Regenerate API key
  async regenerateApiKey(keyId) {
    const response = await fetch(`${this.baseURL}/user/keys/${keyId}/regenerate/`, {
      method: 'POST',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Create webhook
  async createWebhook(webhookData) {
    const response = await fetch(`${this.baseURL}/user/webhooks/create/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(webhookData)
    });
    return response.json();
  }

  // Toggle webhook
  async toggleWebhook(webhookId) {
    const response = await fetch(`${this.baseURL}/user/webhooks/${webhookId}/toggle/`, {
      method: 'POST',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Delete webhook
  async deleteWebhook(webhookId) {
    const response = await fetch(`${this.baseURL}/user/webhooks/${webhookId}/delete/`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Send test SMS
  async sendTestSMS(smsData) {
    const response = await fetch(`${this.baseURL}/v1/test-sms/send/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(smsData)
    });
    return response.json();
  }

  // Check SMS status
  async checkSMSStatus(messageId) {
    const response = await fetch(`${this.baseURL}/v1/test-sms/status/${messageId}/`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    return response.json();
  }

  // Check balance
  async checkBalance() {
    const response = await fetch(`${this.baseURL}/v1/test-sms/balance/`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    return response.json();
  }
}
```

---

## 🎨 Code Examples

### 1. Load Settings on Page Load

```javascript
// Initialize API service
const api = new UserSettingsAPI();

// Load settings when page loads
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const settings = await api.getSettings();
    const usage = await api.getUsage();
    
    // Populate account info
    populateAccountInfo(settings.data.api_account);
    
    // Populate API keys
    populateApiKeys(settings.data.api_keys);
    
    // Populate webhooks
    populateWebhooks(settings.data.webhooks);
    
    // Populate usage stats
    populateUsageStats(usage.data);
    
  } catch (error) {
    console.error('Error loading settings:', error);
    showError('Failed to load settings. Please try again.');
  }
});
```

### 2. Create API Key

```javascript
// Create API key function
async function createApiKey() {
  const keyName = document.getElementById('key-name').value;
  const permissions = {
    sms: ['send', 'status', 'balance']
  };

  try {
    const response = await api.createApiKey({
      key_name: keyName,
      permissions: permissions
    });

    if (response.success) {
      // Show success message with API key
      showApiKeyModal(response.data);
      // Refresh API keys list
      loadApiKeys();
    } else {
      showError(response.message);
    }
  } catch (error) {
    console.error('Error creating API key:', error);
    showError('Failed to create API key. Please try again.');
  }
}

// Show API key in modal
function showApiKeyModal(keyData) {
  const modal = document.getElementById('api-key-modal');
  const apiKeyElement = document.getElementById('api-key-value');
  const secretKeyElement = document.getElementById('secret-key-value');
  
  apiKeyElement.textContent = keyData.api_key;
  secretKeyElement.textContent = keyData.secret_key;
  
  modal.style.display = 'block';
}
```

### 3. Create Webhook

```javascript
// Create webhook function
async function createWebhook() {
  const url = document.getElementById('webhook-url').value;
  const events = Array.from(document.querySelectorAll('input[name="webhook-events"]:checked'))
    .map(input => input.value);

  try {
    const response = await api.createWebhook({
      url: url,
      events: events
    });

    if (response.success) {
      showSuccess('Webhook created successfully!');
      loadWebhooks();
    } else {
      showError(response.message);
    }
  } catch (error) {
    console.error('Error creating webhook:', error);
    showError('Failed to create webhook. Please try again.');
  }
}
```

### 4. Send Test SMS

```javascript
// Send test SMS function
async function sendTestSMS() {
  const phoneNumber = document.getElementById('test-phone').value;
  const message = document.getElementById('test-message').value;

  try {
    const response = await api.sendTestSMS({
      message: message,
      recipients: [phoneNumber],
      sender_id: 'Taarifa-SMS'
    });

    if (response.success) {
      showSuccess('Test SMS sent successfully!');
      // Check status after a delay
      setTimeout(() => checkSMSStatus(response.data.message_id), 3000);
    } else {
      showError(response.message);
    }
  } catch (error) {
    console.error('Error sending test SMS:', error);
    showError('Failed to send test SMS. Please try again.');
  }
}

// Check SMS status
async function checkSMSStatus(messageId) {
  try {
    const response = await api.checkSMSStatus(messageId);
    if (response.success) {
      showSMSStatus(response.data);
    }
  } catch (error) {
    console.error('Error checking SMS status:', error);
  }
}
```

---

## 🚨 Error Handling

### Error Response Format
```javascript
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": "Additional error details"
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED` - User not logged in
- `INVALID_CREDENTIALS` - Invalid API key
- `MISSING_MESSAGE` - SMS message is required
- `INVALID_PHONE_FORMAT` - Phone number format is invalid
- `INSUFFICIENT_BALANCE` - Account needs to be topped up

### Error Handling Function
```javascript
function handleApiError(error, response) {
  if (response && response.error_code) {
    switch (response.error_code) {
      case 'AUTHENTICATION_REQUIRED':
        // Redirect to login
        window.location.href = '/login';
        break;
      case 'INSUFFICIENT_BALANCE':
        showError('Account balance is insufficient. Please top up your account.');
        break;
      default:
        showError(response.message || 'An error occurred. Please try again.');
    }
  } else {
    showError('Network error. Please check your connection.');
  }
}
```

---

## 🎨 UI Components

### 1. API Key Card Component
```html
<div class="api-key-card">
  <div class="key-info">
    <h3>API Key Name</h3>
    <p class="key-value">mif_xxxxxxxxxxxxxxxxxxxx</p>
    <p class="key-status active">Active</p>
  </div>
  <div class="key-actions">
    <button class="btn-copy" onclick="copyToClipboard('api-key')">Copy</button>
    <button class="btn-regenerate" onclick="regenerateKey('key-id')">Regenerate</button>
    <button class="btn-revoke" onclick="revokeKey('key-id')">Revoke</button>
  </div>
</div>
```

### 2. Webhook Card Component
```html
<div class="webhook-card">
  <div class="webhook-info">
    <h3>Webhook Name</h3>
    <p class="webhook-url">https://example.com/webhook</p>
    <p class="webhook-events">message.sent, message.delivered</p>
    <p class="webhook-status active">Active</p>
  </div>
  <div class="webhook-actions">
    <button class="btn-toggle" onclick="toggleWebhook('webhook-id')">Toggle</button>
    <button class="btn-delete" onclick="deleteWebhook('webhook-id')">Delete</button>
  </div>
</div>
```

### 3. SMS Test Form Component
```html
<div class="sms-test-form">
  <h3>Send Test SMS</h3>
  <form id="sms-test-form">
    <div class="form-group">
      <label for="test-phone">Phone Number</label>
      <input type="tel" id="test-phone" placeholder="+255757347863" required>
    </div>
    <div class="form-group">
      <label for="test-message">Message</label>
      <textarea id="test-message" placeholder="Enter your test message..." required></textarea>
    </div>
    <div class="form-group">
      <label for="sender-id">Sender ID</label>
      <select id="sender-id">
        <option value="Taarifa-SMS">Taarifa-SMS</option>
        <option value="Quantum">Quantum</option>
      </select>
    </div>
    <button type="submit" class="btn-send-sms">Send Test SMS</button>
  </form>
</div>
```

---

## 🧪 Testing

### 1. Test API Connection
```javascript
// Test API connection
async function testApiConnection() {
  try {
    const response = await api.getSettings();
    if (response.success) {
      console.log('API connection successful');
      return true;
    } else {
      console.error('API connection failed:', response.message);
      return false;
    }
  } catch (error) {
    console.error('API connection error:', error);
    return false;
  }
}
```

### 2. Test SMS Functionality
```javascript
// Test SMS functionality
async function testSMSFunctionality() {
  try {
    // Send test SMS
    const smsResponse = await api.sendTestSMS({
      message: 'Test message from frontend',
      recipients: ['+255757347863'],
      sender_id: 'Taarifa-SMS'
    });

    if (smsResponse.success) {
      console.log('SMS test successful');
      
      // Check status
      const statusResponse = await api.checkSMSStatus(smsResponse.data.message_id);
      console.log('SMS status:', statusResponse.data.status);
      
      return true;
    } else {
      console.error('SMS test failed:', smsResponse.message);
      return false;
    }
  } catch (error) {
    console.error('SMS test error:', error);
    return false;
  }
}
```

---

## 📱 Mobile Responsiveness

### CSS for Mobile
```css
@media (max-width: 768px) {
  .settings-container {
    padding: 10px;
  }
  
  .api-key-card,
  .webhook-card {
    flex-direction: column;
  }
  
  .key-actions,
  .webhook-actions {
    margin-top: 10px;
  }
  
  .btn {
    width: 100%;
    margin: 5px 0;
  }
}
```

---

## 🔧 Configuration

### Environment Variables
```javascript
// Configuration object
const config = {
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8001/api/integration',
  defaultSenderId: 'Taarifa-SMS',
  maxMessageLength: 160,
  supportedPhoneFormats: ['+255XXXXXXXXX', '255XXXXXXXXX', '0XXXXXXXXX']
};
```

---

## 📚 Additional Resources

### API Documentation
- [User Settings API Guide](./USER_SETTINGS_API_GUIDE.md)
- [SMS API Documentation](./MIFUMO_SMS_API_DOCUMENTATION.md)

### Support
- For technical support, contact the backend team
- For API issues, check the error codes and messages
- For SMS delivery issues, verify account balance

---

## 🚀 Getting Started

1. **Set up authentication** - Ensure users can log in and get JWT tokens
2. **Initialize API service** - Create an instance of `UserSettingsAPI`
3. **Load settings** - Call `getSettings()` on page load
4. **Implement UI components** - Use the provided HTML/CSS examples
5. **Add error handling** - Implement proper error handling for all API calls
6. **Test functionality** - Use the provided test functions

---

**Happy coding! 🎉**

This guide provides everything you need to integrate the User Settings API into your frontend settings template. The API is fully functional and ready for production use.

