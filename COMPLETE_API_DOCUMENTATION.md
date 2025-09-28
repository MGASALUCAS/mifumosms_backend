# 🚀 Mifumo WMS - Complete API Documentation

## 📋 **Overview**

This document provides a comprehensive guide to all API endpoints in the Mifumo WMS (WhatsApp Management System) backend. The API is built with Django REST Framework and provides multi-tenant messaging capabilities with WhatsApp, SMS, and other communication channels.

## 🔗 **Base Information**

- **Base URL**: `http://127.0.0.1:8000` (Development)
- **API Version**: v1
- **Authentication**: JWT Bearer Token
- **Content-Type**: `application/json`
- **Documentation**: `http://127.0.0.1:8000/swagger/`

## 🔐 **Authentication**

All API endpoints (except registration and login) require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer your-jwt-token-here
```

---

## 📚 **API Endpoints**

### 🔑 **Authentication & User Management**

#### **POST** `/api/auth/register/`
**Description**: Register a new user account
**Authentication**: None required

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+255700000001"
}
```

**Response** (201):
```json
{
    "message": "User created successfully. Please check your email for verification.",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_verified": false
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### **POST** `/api/auth/login/`
**Description**: Authenticate user and get JWT tokens
**Authentication**: None required

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response** (200):
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_verified": true
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### **POST** `/api/auth/token/refresh/`
**Description**: Refresh JWT access token
**Authentication**: None required

**Request Body**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### **GET** `/api/auth/profile/`
**Description**: Get current user profile
**Authentication**: Required

**Response** (200):
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+255700000001",
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### **PUT** `/api/auth/profile/`
**Description**: Update user profile
**Authentication**: Required

#### **POST** `/api/auth/password/change/`
**Description**: Change user password
**Authentication**: Required

#### **POST** `/api/auth/password/reset/`
**Description**: Request password reset
**Authentication**: None required

#### **POST** `/api/auth/verify-email/`
**Description**: Verify email address
**Authentication**: Required

#### **POST** `/api/auth/api-key/generate/`
**Description**: Generate API key for user
**Authentication**: Required

#### **POST** `/api/auth/api-key/revoke/`
**Description**: Revoke user API key
**Authentication**: Required

---

### 🏢 **Tenant Management**

#### **GET** `/api/tenants/`
**Description**: List all tenants for current user
**Authentication**: Required

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "name": "Company Name",
        "subdomain": "company",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### **POST** `/api/tenants/`
**Description**: Create new tenant
**Authentication**: Required

**Request Body**:
```json
{
    "name": "My Company",
    "subdomain": "mycompany",
    "business_name": "My Company Ltd",
    "business_type": "Technology",
    "phone_number": "+255700000001",
    "email": "contact@mycompany.com"
}
```

#### **GET** `/api/tenants/{tenant_id}/`
**Description**: Get tenant details
**Authentication**: Required

#### **PUT** `/api/tenants/{tenant_id}/`
**Description**: Update tenant
**Authentication**: Required

#### **POST** `/api/tenants/switch/`
**Description**: Switch active tenant
**Authentication**: Required

#### **GET** `/api/tenants/{tenant_id}/domains/`
**Description**: List tenant domains
**Authentication**: Required

#### **POST** `/api/tenants/{tenant_id}/domains/`
**Description**: Add domain to tenant
**Authentication**: Required

#### **GET** `/api/tenants/{tenant_id}/members/`
**Description**: List tenant members
**Authentication**: Required

#### **POST** `/api/tenants/{tenant_id}/members/`
**Description**: Invite member to tenant
**Authentication**: Required

#### **GET** `/api/tenants/invite/{token}/`
**Description**: Accept tenant invitation
**Authentication**: None required

---

### 📱 **Messaging - Contacts**

#### **GET** `/api/messaging/contacts/`
**Description**: List all contacts
**Authentication**: Required
**Query Parameters**:
- `search`: Search in name, phone, email
- `is_active`: Filter by active status
- `tags`: Filter by tags (JSON)

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "name": "John Doe",
        "phone_e164": "+255700000001",
        "email": "john@example.com",
        "is_active": true,
        "opt_in_at": "2024-01-01T00:00:00Z",
        "tags": ["vip", "customer"],
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### **POST** `/api/messaging/contacts/`
**Description**: Create new contact
**Authentication**: Required

**Request Body**:
```json
{
    "name": "John Doe",
    "phone_e164": "+255700000001",
    "email": "john@example.com",
    "tags": ["vip", "customer"],
    "attributes": {
        "company": "ABC Corp",
        "department": "Sales"
    }
}
```

#### **GET** `/api/messaging/contacts/{contact_id}/`
**Description**: Get contact details
**Authentication**: Required

#### **PUT** `/api/messaging/contacts/{contact_id}/`
**Description**: Update contact
**Authentication**: Required

#### **DELETE** `/api/messaging/contacts/{contact_id}/`
**Description**: Delete contact
**Authentication**: Required

#### **POST** `/api/messaging/contacts/bulk-import/`
**Description**: Bulk import contacts from CSV/Excel
**Authentication**: Required

#### **POST** `/api/messaging/contacts/{contact_id}/opt-in/`
**Description**: Mark contact as opted-in
**Authentication**: Required

#### **POST** `/api/messaging/contacts/{contact_id}/opt-out/`
**Description**: Mark contact as opted-out
**Authentication**: Required

---

### 📊 **Messaging - Segments**

#### **GET** `/api/messaging/segments/`
**Description**: List contact segments
**Authentication**: Required

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "name": "VIP Customers",
        "description": "High-value customers",
        "contact_count": 150,
        "filter_json": {
            "tags": ["vip"],
            "is_active": true
        },
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### **POST** `/api/messaging/segments/`
**Description**: Create new segment
**Authentication**: Required

**Request Body**:
```json
{
    "name": "VIP Customers",
    "description": "High-value customers",
    "filter_json": {
        "tags": ["vip"],
        "is_active": true
    }
}
```

#### **GET** `/api/messaging/segments/{segment_id}/`
**Description**: Get segment details
**Authentication**: Required

#### **PUT** `/api/messaging/segments/{segment_id}/`
**Description**: Update segment
**Authentication**: Required

#### **DELETE** `/api/messaging/segments/{segment_id}/`
**Description**: Delete segment
**Authentication**: Required

#### **POST** `/api/messaging/segments/{segment_id}/update-count/`
**Description**: Update segment contact count
**Authentication**: Required

---

### 📝 **Messaging - Templates**

#### **GET** `/api/messaging/templates/`
**Description**: List message templates
**Authentication**: Required

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "name": "Welcome Message",
        "category": "greeting",
        "language": "en",
        "content": "Hello {{name}}, welcome to our service!",
        "variables": ["name"],
        "is_active": true,
        "approval_status": "approved",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### **POST** `/api/messaging/templates/`
**Description**: Create new template
**Authentication**: Required

**Request Body**:
```json
{
    "name": "Welcome Message",
    "category": "greeting",
    "language": "en",
    "content": "Hello {{name}}, welcome to our service!",
    "variables": ["name"]
}
```

#### **GET** `/api/messaging/templates/{template_id}/`
**Description**: Get template details
**Authentication**: Required

#### **PUT** `/api/messaging/templates/{template_id}/`
**Description**: Update template
**Authentication**: Required

#### **DELETE** `/api/messaging/templates/{template_id}/`
**Description**: Delete template
**Authentication**: Required

---

### 💬 **Messaging - Conversations**

#### **GET** `/api/messaging/conversations/`
**Description**: List conversations
**Authentication**: Required
**Query Parameters**:
- `contact_id`: Filter by contact
- `status`: Filter by status
- `search`: Search in messages

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "contact": {
            "id": "uuid-here",
            "name": "John Doe",
            "phone_e164": "+255700000001"
        },
        "status": "active",
        "last_message_at": "2024-01-01T00:00:00Z",
        "message_count": 15,
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### **POST** `/api/messaging/conversations/`
**Description**: Create new conversation
**Authentication**: Required

#### **GET** `/api/messaging/conversations/{conversation_id}/`
**Description**: Get conversation details
**Authentication**: Required

#### **PUT** `/api/messaging/conversations/{conversation_id}/`
**Description**: Update conversation
**Authentication**: Required

---

### 📨 **Messaging - Messages**

#### **GET** `/api/messaging/messages/`
**Description**: List messages
**Authentication**: Required
**Query Parameters**:
- `conversation_id`: Filter by conversation
- `direction`: Filter by direction (in/out)
- `status`: Filter by status
- `provider`: Filter by provider

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "conversation": "uuid-here",
        "direction": "out",
        "provider": "whatsapp",
        "text": "Hello John, how can I help you?",
        "status": "delivered",
        "sent_at": "2024-01-01T00:00:00Z",
        "delivered_at": "2024-01-01T00:00:05Z",
        "cost_micro": 5000
    }
]
```

#### **POST** `/api/messaging/messages/`
**Description**: Send new message
**Authentication**: Required

**Request Body**:
```json
{
    "conversation_id": "uuid-here",
    "text": "Hello John, how can I help you?",
    "provider": "whatsapp",
    "template_id": "uuid-here"
}
```

#### **GET** `/api/messaging/messages/{message_id}/`
**Description**: Get message details
**Authentication**: Required

---

### 📢 **Messaging - Campaigns**

#### **GET** `/api/messaging/campaigns/`
**Description**: List campaigns
**Authentication**: Required

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "name": "Holiday Sale",
        "description": "Promotional campaign for holiday season",
        "status": "draft",
        "template": {
            "id": "uuid-here",
            "name": "Holiday Sale Template"
        },
        "segment": {
            "id": "uuid-here",
            "name": "All Customers"
        },
        "scheduled_at": "2024-12-01T10:00:00Z",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### **POST** `/api/messaging/campaigns/`
**Description**: Create new campaign
**Authentication**: Required

**Request Body**:
```json
{
    "name": "Holiday Sale",
    "description": "Promotional campaign for holiday season",
    "template_id": "uuid-here",
    "segment_id": "uuid-here",
    "scheduled_at": "2024-12-01T10:00:00Z"
}
```

#### **GET** `/api/messaging/campaigns/{campaign_id}/`
**Description**: Get campaign details
**Authentication**: Required

#### **PUT** `/api/messaging/campaigns/{campaign_id}/`
**Description**: Update campaign
**Authentication**: Required

#### **POST** `/api/messaging/campaigns/{campaign_id}/start/`
**Description**: Start campaign
**Authentication**: Required

#### **POST** `/api/messaging/campaigns/{campaign_id}/pause/`
**Description**: Pause campaign
**Authentication**: Required

#### **POST** `/api/messaging/campaigns/{campaign_id}/cancel/`
**Description**: Cancel campaign
**Authentication**: Required

---

### 🔄 **Messaging - Flows**

#### **GET** `/api/messaging/flows/`
**Description**: List automated flows
**Authentication**: Required

#### **POST** `/api/messaging/flows/`
**Description**: Create new flow
**Authentication**: Required

#### **GET** `/api/messaging/flows/{flow_id}/`
**Description**: Get flow details
**Authentication**: Required

#### **PUT** `/api/messaging/flows/{flow_id}/`
**Description**: Update flow
**Authentication**: Required

#### **POST** `/api/messaging/flows/{flow_id}/activate/`
**Description**: Activate flow
**Authentication**: Required

#### **POST** `/api/messaging/flows/{flow_id}/deactivate/`
**Description**: Deactivate flow
**Authentication**: Required

---

### 🤖 **Messaging - AI Features**

#### **POST** `/api/messaging/ai/suggest-reply/{conversation_id}/`
**Description**: Get AI-suggested reply for conversation
**Authentication**: Required

**Response** (200):
```json
{
    "suggestions": [
        "Thank you for your message. How can I help you today?",
        "I understand your concern. Let me assist you with that.",
        "Is there anything specific you'd like to know about our services?"
    ],
    "confidence": 0.85
}
```

#### **POST** `/api/messaging/ai/summarize/{conversation_id}/`
**Description**: Get AI summary of conversation
**Authentication**: Required

**Response** (200):
```json
{
    "summary": "Customer inquired about pricing for premium package. Discussed features and benefits. Customer requested follow-up call.",
    "key_points": [
        "Pricing inquiry",
        "Premium package discussion",
        "Follow-up requested"
    ],
    "sentiment": "positive"
}
```

---

### 📊 **Messaging - Analytics**

#### **GET** `/api/messaging/analytics/overview/`
**Description**: Get messaging analytics overview
**Authentication**: Required

**Response** (200):
```json
{
    "total_messages": 1500,
    "messages_today": 45,
    "active_conversations": 23,
    "total_contacts": 500,
    "delivery_rate": 0.95,
    "response_time_avg": 120,
    "top_templates": [
        {
            "id": "uuid-here",
            "name": "Welcome Message",
            "usage_count": 150
        }
    ],
    "messages_by_provider": {
        "whatsapp": 1200,
        "sms": 300
    }
}
```

---

### 📱 **SMS - General**

#### **GET** `/api/messaging/sms/sms/providers/`
**Description**: List SMS providers
**Authentication**: Required

#### **POST** `/api/messaging/sms/sms/providers/`
**Description**: Create SMS provider
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/sender-ids/`
**Description**: List sender IDs
**Authentication**: Required

#### **POST** `/api/messaging/sms/sms/sender-ids/`
**Description**: Create sender ID
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/templates/`
**Description**: List SMS templates
**Authentication**: Required

#### **POST** `/api/messaging/sms/sms/templates/`
**Description**: Create SMS template
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/messages/`
**Description**: List SMS messages
**Authentication**: Required

#### **POST** `/api/messaging/sms/sms/send/`
**Description**: Send SMS message
**Authentication**: Required

**Request Body**:
```json
{
    "message": "Hello from Mifumo WMS!",
    "recipients": ["+255700000001"],
    "sender_id": "MIFUMO",
    "template_id": "uuid-here"
}
```

#### **POST** `/api/messaging/sms/sms/send-bulk/`
**Description**: Send bulk SMS
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/balance/`
**Description**: Get SMS account balance
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/stats/`
**Description**: Get SMS statistics
**Authentication**: Required

---

### 📱 **SMS - Beem Integration**

#### **POST** `/api/messaging/sms/sms/beem/send/`
**Description**: Send SMS via Beem Africa
**Authentication**: Required

**Request Body**:
```json
{
    "message": "Hello from Mifumo WMS!",
    "recipients": ["255700000001"],
    "sender_id": "Taarifa-SMS",
    "encoding": 0
}
```

**Response** (201):
```json
{
    "success": true,
    "message": "SMS sent successfully via Beem",
    "data": {
        "message_id": "uuid-here",
        "provider": "beem",
        "recipient_count": 1,
        "cost_estimate": 0.05,
        "status": "sent"
    }
}
```

#### **POST** `/api/messaging/sms/sms/beem/send-bulk/`
**Description**: Send bulk SMS via Beem
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/beem/test-connection/`
**Description**: Test Beem connection
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/beem/balance/`
**Description**: Get Beem account balance
**Authentication**: Required

#### **POST** `/api/messaging/sms/sms/beem/validate-phone/`
**Description**: Validate phone number
**Authentication**: Required

#### **GET** `/api/messaging/sms/sms/beem/{message_id}/status/`
**Description**: Get SMS delivery status
**Authentication**: Required

---

### 💳 **Billing**

#### **GET** `/api/billing/plans/`
**Description**: List available plans
**Authentication**: Required

**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "name": "Starter",
        "description": "Perfect for small businesses",
        "price": 29.99,
        "currency": "USD",
        "billing_cycle": "monthly",
        "features": [
            "1000 messages/month",
            "WhatsApp integration",
            "Basic analytics"
        ]
    }
]
```

#### **GET** `/api/billing/subscription/`
**Description**: Get current subscription
**Authentication**: Required

#### **POST** `/api/billing/subscription/create/`
**Description**: Create new subscription
**Authentication**: Required

#### **POST** `/api/billing/subscription/cancel/`
**Description**: Cancel subscription
**Authentication**: Required

#### **GET** `/api/billing/invoices/`
**Description**: List invoices
**Authentication**: Required

#### **GET** `/api/billing/invoices/{invoice_id}/`
**Description**: Get invoice details
**Authentication**: Required

#### **GET** `/api/billing/payment-methods/`
**Description**: List payment methods
**Authentication**: Required

#### **POST** `/api/billing/payment-methods/`
**Description**: Add payment method
**Authentication**: Required

#### **GET** `/api/billing/usage/`
**Description**: Get usage records
**Authentication**: Required

#### **GET** `/api/billing/usage/limits/`
**Description**: Get usage limits
**Authentication**: Required

#### **GET** `/api/billing/overview/`
**Description**: Get billing overview
**Authentication**: Required

#### **GET** `/api/billing/coupons/`
**Description**: List available coupons
**Authentication**: Required

#### **POST** `/api/billing/coupons/validate/`
**Description**: Validate coupon code
**Authentication**: Required

---

### 🔗 **Webhooks**

#### **GET** `/webhooks/whatsapp/`
**Description**: WhatsApp webhook verification
**Authentication**: None required
**Query Parameters**:
- `hub.mode`: subscribe
- `hub.verify_token`: verification token
- `hub.challenge`: challenge string

#### **POST** `/webhooks/whatsapp/`
**Description**: WhatsApp webhook events
**Authentication**: None required

#### **POST** `/webhooks/stripe/`
**Description**: Stripe webhook events
**Authentication**: None required

---

## 🔧 **Common Response Formats**

### **Success Response**
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    }
}
```

### **Error Response**
```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error message"]
    }
}
```

### **Validation Error**
```json
{
    "field_name": ["This field is required."],
    "another_field": ["Invalid format."]
}
```

---

## 📊 **Status Codes**

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

---

## 🔒 **Rate Limiting**

- **Message Sending**: 60 messages per minute
- **API Calls**: 1000 requests per minute
- **Bulk Operations**: 10 requests per minute

---

## 🌍 **Multi-Tenant Support**

All endpoints are tenant-aware and automatically filter data based on the authenticated user's tenant. Users can only access data belonging to their tenant.

---

## 📱 **Supported Providers**

- **WhatsApp Business Cloud API**
- **SMS (Beem Africa)**
- **SMS (Twilio)**
- **Telegram (Future)**

---

## 🚀 **Getting Started**

1. **Register**: `POST /api/auth/register/`
2. **Login**: `POST /api/auth/login/`
3. **Create Tenant**: `POST /api/tenants/`
4. **Add Contacts**: `POST /api/messaging/contacts/`
5. **Send Message**: `POST /api/messaging/messages/`

---

## 📞 **Support**

- **API Documentation**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`
- **JSON Schema**: `http://127.0.0.1:8000/swagger.json`

---

**Built with ❤️ for African SMEs by [Mifumo Labs](https://mifumolabs.com)**

*Empowering businesses across Africa with world-class messaging technology.*
