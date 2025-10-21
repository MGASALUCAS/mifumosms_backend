# Frontend Integration Guide - Complete API Endpoints

This guide provides comprehensive documentation for all API endpoints that frontend developers need to integrate with the Mifumo SMS backend.

## Base URLs
- **Local Development**: `http://127.0.0.1:8000/api/`
- **Production**: `https://your-domain.com/api/`

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

---

## 🔐 Authentication Endpoints

### Login
```javascript
POST /api/auth/login/
```
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### Register
```javascript
POST /api/auth/register/
```
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Refresh Token
```javascript
POST /api/auth/token/refresh/
```
**Request:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

## 📊 Billing History Endpoints

### 1. Comprehensive Billing History
```javascript
GET /api/billing/history/
```
**Query Parameters:**
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_purchased": 150000.00,
      "total_credits_purchased": 5000,
      "total_usage_cost": 125000.00,
      "total_credits_used": 4500,
      "current_balance": 500,
      "total_purchases": 3,
      "total_payments": 3,
      "total_usage_records": 45
    },
    "purchases": [...],
    "payments": [...],
    "usage_records": [...],
    "custom_purchases": [...]
  }
}
```

### 2. Billing History Summary with Charts
```javascript
GET /api/billing/history/summary/
```
**Query Parameters:**
- `period` (optional): Time period (7d, 30d, 90d, 1y) - Default: 30d
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_purchased": 150000.00,
      "total_credits_purchased": 5000,
      "total_usage_cost": 125000.00,
      "total_credits_used": 4500,
      "current_balance": 500,
      "period": "30d",
      "start_date": "2025-01-01",
      "end_date": "2025-01-31"
    },
    "charts": {
      "monthly_usage": [
        {
          "month": "2025-01",
          "credits": 1000,
          "cost": 25000.00
        }
      ],
      "payment_methods": [
        {
          "method": "mpesa",
          "count": 2,
          "amount": 100000.00
        }
      ]
    }
  }
}
```

### 3. Detailed Purchase History
```javascript
GET /api/billing/history/purchases/
```
**Query Parameters:**
- `status` (optional): Filter by status (pending, completed, failed, cancelled, expired, refunded)
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "purchases": [
      {
        "id": "uuid",
        "invoice_number": "INV-001",
        "package_name": "Standard Package",
        "amount": 50000.00,
        "credits": 2000,
        "status": "completed",
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "count": 10,
      "next": "?page=2&page_size=20",
      "previous": null,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

### 4. Detailed Payment History
```javascript
GET /api/billing/history/payments/
```
**Query Parameters:**
- `status` (optional): Filter by payment status
- `payment_method` (optional): Filter by payment method (mpesa, tigopesa, airtelmoney, etc.)
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

### 5. Detailed Usage History
```javascript
GET /api/billing/history/usage/
```
**Query Parameters:**
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

---

## 📱 SMS Management Endpoints

### SMS Balance
```javascript
GET /api/billing/sms/balance/
```
**Response:**
```json
{
  "success": true,
  "data": {
    "credits": 1000,
    "total_purchased": 5000,
    "total_used": 4000,
    "last_updated": "2025-01-15T10:30:00Z"
  }
}
```

### SMS Packages
```javascript
GET /api/billing/sms/packages/
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Standard Package",
      "credits": 2000,
      "price": 50000.00,
      "unit_price": 25.00,
      "is_popular": true,
      "features": ["SMS", "Analytics"]
    }
  ]
}
```

### Send SMS
```javascript
POST /api/messaging/sms/send/
```
**Request:**
```json
{
  "recipients": ["+255757347863"],
  "message": "Hello from Mifumo SMS!",
  "sender_id": "TAARIFA-SMS"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "status": "sent",
    "recipients_count": 1,
    "credits_used": 1
  }
}
```

---

## 👥 Contact Management Endpoints

### List Contacts
```javascript
GET /api/messaging/contacts/
```
**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Items per page
- `search` (optional): Search in name, phone, or email
- `tags` (optional): Filter by tags

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "John Doe",
      "phone_e164": "+255757347863",
      "email": "john@example.com",
      "tags": ["customer", "vip"],
      "is_active": true,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "count": 100,
    "next": "?page=2",
    "previous": null,
    "page": 1,
    "page_size": 20
  }
}
```

### Create Contact
```javascript
POST /api/messaging/contacts/
```
**Request:**
```json
{
  "name": "John Doe",
  "phone_e164": "+255757347863",
  "email": "john@example.com",
  "tags": ["customer", "vip"],
  "attributes": {
    "company": "Acme Corp",
    "department": "Sales"
  }
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "John Doe",
    "phone_e164": "+255757347863",
    "email": "john@example.com",
    "tags": ["customer", "vip"],
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

### Update Contact
```javascript
PUT /api/messaging/contacts/{id}/
PATCH /api/messaging/contacts/{id}/
```

### Delete Contact
```javascript
DELETE /api/messaging/contacts/{id}/
```

### Bulk Import Contacts
```javascript
POST /api/messaging/contacts/bulk-import/
```
**Request:**
```json
{
  "csv_data": "name,phone_e164,email\nJohn Doe,+255757347863,john@example.com\nJane Smith,+255757347864,jane@example.com"
}
```

---

## 📢 Sender ID Management Endpoints

### List Sender IDs
```javascript
GET /api/messaging/sender-ids/
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "sender_id": "TAARIFA-SMS",
      "status": "active",
      "sample_content": "A test use case for the sender name...",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Request Sender ID
```javascript
POST /api/messaging/sender-ids/request/
```
**Request:**
```json
{
  "requested_sender_id": "MyCompany-SMS",
  "business_name": "My Company Ltd",
  "business_type": "Technology",
  "contact_person": "John Doe",
  "contact_phone": "0744963858",
  "contact_email": "admin@mycompany.com",
  "business_license": "LIC123456",
  "purpose": "Customer notifications"
}
```

### Submit Sender ID Request (Frontend Compatible)
```javascript
POST /api/messaging/sender-requests/submit/
```
**Request:**
```json
{
  "requested_sender_id": "MyCompany",
  "sample_content": "A test use case for the sender name purposely used for information transfer.",
  "business_justification": "Requesting to use this sender ID for customer notifications and business communications.",
  "business_name": "My Company Ltd",
  "business_type": "Technology",
  "contact_person": "John Doe",
  "contact_phone": "0744963858",
  "contact_email": "admin@mycompany.com",
  "business_license": "LIC123456"
}
```
**Response:**
```json
{
  "success": true,
  "message": "Sender ID request submitted successfully",
  "data": {
    "id": "uuid",
    "requested_sender_id": "MYCOMPANY",
    "status": "pending",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

### List Sender Requests
```javascript
GET /api/messaging/sender-requests/
```
**Query Parameters:**
- `status` (optional): Filter by status (pending, approved, rejected)
- `page` (optional): Page number
- `page_size` (optional): Items per page

### Request Default Sender ID
```javascript
POST /api/messaging/sender-requests/request-default/
```
**Response:**
```json
{
  "success": true,
  "message": "Default sender ID request approved and created successfully",
  "sender_id_request": {
    "id": "uuid",
    "requested_sender_id": "TAARIFA-SMS",
    "status": "approved",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

---

## 💳 Payment Endpoints

### Initiate Payment
```javascript
POST /api/billing/payments/initiate/
```
**Request:**
```json
{
  "package_id": "uuid",
  "buyer_email": "user@example.com",
  "buyer_name": "John Doe",
  "buyer_phone": "0744963858"
}
```

### Get Active Payments
```javascript
GET /api/billing/payments/active/
```

### Payment Status
```javascript
GET /api/billing/payments/transactions/{transaction_id}/status/
```

---

## 📈 Analytics Endpoints

### Dashboard Overview
```javascript
GET /api/messaging/dashboard/overview/
```

### Dashboard Metrics
```javascript
GET /api/messaging/dashboard/metrics/
```

### SMS Statistics
```javascript
GET /api/messaging/sms/stats/
```

---

## 🎯 Campaign Management Endpoints

### List Campaigns
```javascript
GET /api/messaging/campaigns/
```

### Create Campaign
```javascript
POST /api/messaging/campaigns/
```
**Request:**
```json
{
  "name": "Welcome Campaign",
  "message": "Welcome to our service!",
  "recipients": ["+255757347863", "+255757347864"],
  "sender_id": "TAARIFA-SMS",
  "scheduled_at": "2025-01-20T10:00:00Z"
}
```

### Start Campaign
```javascript
POST /api/messaging/campaigns/{id}/start/
```

### Pause Campaign
```javascript
POST /api/messaging/campaigns/{id}/pause/
```

---

## 🔧 Frontend Integration Examples

### React/JavaScript Integration

```javascript
class MifumoSMSAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || 'API request failed');
    }
    
    return data;
  }

  // Billing History
  async getBillingHistory(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/billing/history/?${params}`);
  }

  async getBillingSummary(period = '30d') {
    return this.request(`/billing/history/summary/?period=${period}`);
  }

  // Contacts
  async getContacts(page = 1, pageSize = 20, search = '') {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(search && { search })
    });
    return this.request(`/messaging/contacts/?${params}`);
  }

  async createContact(contactData) {
    return this.request('/messaging/contacts/', {
      method: 'POST',
      body: JSON.stringify(contactData)
    });
  }

  // Sender IDs
  async getSenderIDs() {
    return this.request('/messaging/sender-ids/');
  }

  async requestSenderID(requestData) {
    return this.request('/messaging/sender-ids/request/', {
      method: 'POST',
      body: JSON.stringify(requestData)
    });
  }

  async submitSenderRequest(requestData) {
    return this.request('/messaging/sender-requests/submit/', {
      method: 'POST',
      body: JSON.stringify(requestData)
    });
  }

  // SMS
  async sendSMS(recipients, message, senderID = 'TAARIFA-SMS') {
    return this.request('/messaging/sms/send/', {
      method: 'POST',
      body: JSON.stringify({
        recipients,
        message,
        sender_id: senderID
      })
    });
  }

  async getSMSBalance() {
    return this.request('/billing/sms/balance/');
  }
}

// Usage Example
const api = new MifumoSMSAPI('http://127.0.0.1:8000/api', 'your-jwt-token');

// Get billing summary
const billingSummary = await api.getBillingSummary('30d');
console.log('Total purchased:', billingSummary.data.summary.total_purchased);

// Get contacts
const contacts = await api.getContacts(1, 20, 'john');
console.log('Contacts:', contacts.data);

// Send SMS
const smsResult = await api.sendSMS(
  ['+255757347863'], 
  'Hello from Mifumo SMS!'
);
console.log('SMS sent:', smsResult.data);

// Submit sender ID request
const senderRequest = await api.submitSenderRequest({
  requested_sender_id: 'MyCompany',
  sample_content: 'A test use case for the sender name purposely used for information transfer.',
  business_justification: 'Requesting to use this sender ID for customer notifications.',
  business_name: 'My Company Ltd',
  business_type: 'Technology',
  contact_person: 'John Doe',
  contact_phone: '0744963858',
  contact_email: 'admin@mycompany.com',
  business_license: 'LIC123456'
});
console.log('Sender request submitted:', senderRequest.data);
```

### Vue.js Integration

```javascript
// composables/useMifumoSMS.js
import { ref, computed } from 'vue'

export function useMifumoSMS() {
  const baseURL = 'http://127.0.0.1:8000/api'
  const token = ref(localStorage.getItem('jwt_token'))
  
  const request = async (endpoint, options = {}) => {
    const response = await fetch(`${baseURL}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })
    
    if (!response.ok) {
      throw new Error('API request failed')
    }
    
    return response.json()
  }

  const getBillingHistory = (filters = {}) => {
    const params = new URLSearchParams(filters)
    return request(`/billing/history/?${params}`)
  }

  const getContacts = (page = 1, pageSize = 20) => {
    return request(`/messaging/contacts/?page=${page}&page_size=${pageSize}`)
  }

  const sendSMS = (recipients, message, senderID = 'TAARIFA-SMS') => {
    return request('/messaging/sms/send/', {
      method: 'POST',
      body: JSON.stringify({
        recipients,
        message,
        sender_id: senderID
      })
    })
  }

  return {
    getBillingHistory,
    getContacts,
    sendSMS
  }
}
```

---

## 📋 Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## 🔒 Security Notes

1. **Always use HTTPS in production**
2. **Store JWT tokens securely** (httpOnly cookies recommended)
3. **Implement token refresh logic**
4. **Validate all user inputs on the frontend**
5. **Handle authentication errors gracefully**

---

## 📚 Additional Resources

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **API Reference**: See `BILLING_HISTORY_API_DOCUMENTATION.md`
- **Frontend SDK**: See `FRONTEND_SDK.js`

---

## 🚀 Quick Start Checklist

- [ ] Set up authentication (login/register)
- [ ] Implement JWT token management
- [ ] Add billing history dashboard
- [ ] Implement contact management
- [ ] Add sender ID request functionality
- [ ] Implement SMS sending
- [ ] Add error handling
- [ ] Test all endpoints
- [ ] Deploy to production

This guide provides everything needed for frontend integration with the Mifumo SMS backend API.
