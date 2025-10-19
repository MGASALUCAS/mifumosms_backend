# 📊 Billing API Documentation

## Overview

The Mifumo SMS Billing API provides comprehensive billing and payment management for SMS services. It supports multi-tenant architecture with JWT authentication, mobile money payments via ZenoPay, and real-time usage tracking.

## 🔐 Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

## 🏢 Multi-Tenant Support

The API is designed for multi-tenant architecture where each user belongs to a tenant. All billing data is automatically isolated by tenant.

## 📋 API Endpoints

### 1. SMS Package Management

#### Get SMS Packages
```http
GET /api/billing/sms/packages/
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Lite Package",
      "package_type": "prepaid",
      "credits": 1000,
      "price": 25000.00,
      "unit_price": 25.00,
      "is_popular": false,
      "is_active": true,
      "features": ["Basic SMS", "Standard delivery"],
      "savings_percentage": 16.7,
      "default_sender_id": "MIFUMO",
      "allowed_sender_ids": ["MIFUMO", "CUSTOM"],
      "sender_id_restriction": "flexible",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Package Types:**
- `prepaid`: Pay-as-you-go packages
- `subscription`: Monthly/yearly recurring packages

**Sender ID Restrictions:**
- `flexible`: Can use any approved sender ID
- `restricted`: Limited to specific sender IDs
- `default_only`: Must use default sender ID

### 2. SMS Balance Management

#### Get SMS Balance
```http
GET /api/billing/sms/balance/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "tenant": "John Doe's Organization",
    "credits": 5000,
    "total_purchased": 10000,
    "total_used": 5000,
    "last_updated": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 3. Purchase Management

#### Get Purchase History
```http
GET /api/billing/sms/purchases/
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "invoice_number": "INV-2024-001",
      "package": "uuid",
      "package_name": "Lite Package",
      "tenant": "John Doe's Organization",
      "amount": 25000.00,
      "credits": 1000,
      "unit_price": 25.00,
      "payment_method": "mobile_money",
      "payment_method_display": "Mobile Money",
      "payment_reference": "MM-123456",
      "status": "completed",
      "status_display": "Completed",
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:05:00Z"
    }
  ]
}
```

#### Get Detailed Purchase History
```http
GET /api/billing/sms/purchases/history/
```

**Query Parameters:**
- `status`: Filter by purchase status (`pending`, `completed`, `failed`, `cancelled`)
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "purchases": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_count": 50,
      "total_pages": 3
    }
  }
}
```

### 4. Custom SMS Pricing

#### Calculate Custom SMS Pricing
```http
POST /api/billing/payments/custom-sms/calculate/
```

**Request Body:**
```json
{
  "credits": 5000
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "credits": 5000,
    "unit_price": 25.00,
    "total_price": 125000.00,
    "active_tier": "Standard",
    "tier_min_credits": 5000,
    "tier_max_credits": 50000,
    "savings_percentage": 16.7,
    "pricing_tiers": [
      {
        "name": "Lite",
        "min": 1,
        "max": 4999,
        "unit_price": 30.00
      },
      {
        "name": "Standard",
        "min": 5000,
        "max": 50000,
        "unit_price": 25.00
      },
      {
        "name": "Pro",
        "min": 50001,
        "max": 250000,
        "unit_price": 18.00
      },
      {
        "name": "Enterprise",
        "min": 250001,
        "max": 1000000,
        "unit_price": 12.00
      }
    ]
  }
}
```

#### Initiate Custom SMS Purchase
```http
POST /api/billing/payments/custom-sms/initiate/
```

**Request Body:**
```json
{
  "credits": 5000,
  "mobile_money_provider": "vodacom",
  "phone_number": "255712345678"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "purchase_id": "uuid",
    "credits": 5000,
    "unit_price": 25.00,
    "total_price": 125000.00,
    "active_tier": "Standard",
    "provider_name": "Vodacom M-Pesa",
    "payment_instructions": "Dial *150*00# and follow prompts",
    "order_id": "MIFUMO-20241201-ABC123",
    "expires_at": "2024-12-01T01:00:00Z"
  }
}
```

#### Check Custom SMS Purchase Status
```http
GET /api/billing/payments/custom-sms/{purchase_id}/status/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "purchase_id": "uuid",
    "credits": 5000,
    "unit_price": 25.00,
    "total_price": 125000.00,
    "active_tier": "Standard",
    "status": "completed",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:05:00Z",
    "completed_at": "2024-01-01T00:05:00Z"
  }
}
```

### 5. Payment Processing

#### Get Mobile Money Providers
```http
GET /api/billing/payments/providers/
```

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "code": "vodacom",
      "name": "Vodacom M-Pesa",
      "description": "Pay with M-Pesa via Vodacom",
      "icon": "vodacom-icon",
      "popular": true,
      "is_active": true,
      "min_amount": 1000,
      "max_amount": 1000000
    },
    {
      "code": "tigo",
      "name": "Tigo Pesa",
      "description": "Pay with Tigo Pesa",
      "icon": "tigo-icon",
      "popular": false,
      "is_active": true,
      "min_amount": 1000,
      "max_amount": 1000000
    },
    {
      "code": "airtel",
      "name": "Airtel Money",
      "description": "Pay with Airtel Money",
      "icon": "airtel-icon",
      "popular": false,
      "is_active": true,
      "min_amount": 1000,
      "max_amount": 1000000
    },
    {
      "code": "halotel",
      "name": "Halotel Money",
      "description": "Pay with Halotel Money",
      "icon": "halotel-icon",
      "popular": false,
      "is_active": true,
      "min_amount": 1000,
      "max_amount": 1000000
    }
  ]
}
```

#### Initiate Payment
```http
POST /api/billing/payments/initiate/
```

**Request Body:**
```json
{
  "package_id": "uuid",
  "mobile_money_provider": "vodacom",
  "phone_number": "255712345678"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": "uuid",
    "order_id": "MIFUMO-20241201-ABC123",
    "amount": 25000.00,
    "provider_name": "Vodacom M-Pesa",
    "payment_instructions": "Dial *150*00# and follow prompts",
    "expires_at": "2024-12-01T01:00:00Z"
  }
}
```

#### Verify Payment
```http
GET /api/billing/payments/verify/{order_id}/
```

**Response:**
```json
{
  "success": true,
  "status": "completed",
  "amount": 25000.00,
  "transaction_reference": "TXN-123456",
  "message": "Payment completed successfully",
  "last_checked": "2024-01-01T00:05:00Z"
}
```

#### Get Payment Progress
```http
GET /api/billing/payments/transactions/{transaction_id}/progress/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": "uuid",
    "status": "processing",
    "progress": {
      "percentage": 75,
      "current_step": "Payment verification",
      "next_step": "SMS credit allocation",
      "completed_steps": ["Payment initiated", "Mobile money prompt sent"],
      "remaining_steps": ["SMS credit allocation", "Purchase completion"]
    },
    "progress_percentage": 75,
    "current_step": "Payment verification",
    "next_step": "SMS credit allocation",
    "steps": ["Payment initiated", "Mobile money prompt sent", "Payment verification", "SMS credit allocation", "Purchase completion"]
  }
}
```

#### Get Active Payments
```http
GET /api/billing/payments/active/
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "order_id": "MIFUMO-20241201-ABC123",
      "amount": 25000.00,
      "status": "processing",
      "provider": "vodacom",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Cancel Payment
```http
POST /api/billing/payments/transactions/{transaction_id}/cancel/
```

**Response:**
```json
{
  "success": true,
  "message": "Payment cancelled successfully"
}
```

### 6. Usage Statistics

#### Get Usage Statistics
```http
GET /api/billing/sms/usage/statistics/
```

**Query Parameters:**
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": {
    "current_balance": 5000,
    "total_usage": {
      "credits": 1400,
      "cost": 35000.0,
      "period": "all_time"
    },
    "monthly_usage": {
      "credits": 800,
      "cost": 20000.0,
      "period": "monthly"
    },
    "weekly_usage": {
      "credits": 200,
      "cost": 5000.0,
      "period": "weekly"
    },
    "daily_usage": [
      {
        "date": "2024-01-01",
        "credits": 100,
        "cost": 2500.0
      },
      {
        "date": "2024-01-02",
        "credits": 150,
        "cost": 3750.0
      }
    ]
  }
}
```

### 7. Billing Overview

#### Get Billing Overview
```http
GET /api/billing/overview/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subscription": {
      "plan_id": "uuid",
      "plan_name": "Professional",
      "status": "active",
      "current_period_end": "2024-12-31T23:59:59Z",
      "is_active": true
    },
    "sms_balance": {
      "credits": 5000,
      "total_purchased": 10000,
      "total_used": 5000
    },
    "usage": {
      "total_credits": 1400,
      "total_cost": 35000.0
    },
    "usage_summary": {
      "total_credits": 1400,
      "total_cost": 35000.0,
      "current_balance": 5000
    },
    "recent_purchases": [
      {
        "id": "uuid",
        "invoice_number": "INV-2024-001",
        "amount": 25000.00,
        "credits": 1000,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "active_payments": [
      {
        "id": "uuid",
        "order_id": "MIFUMO-20241201-ABC123",
        "amount": 25000.00,
        "status": "processing",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 8. Subscription Management

#### Get Billing Plans
```http
GET /api/billing/plans/
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Professional",
      "description": "Professional SMS plan",
      "price": 50000.00,
      "billing_cycle": "monthly",
      "features": ["Unlimited SMS", "Priority support"],
      "is_active": true
    }
  ]
}
```

#### Get Subscription Details
```http
GET /api/billing/subscription/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "plan": "uuid",
    "plan_name": "Professional",
    "tenant": "John Doe's Organization",
    "status": "active",
    "status_display": "Active",
    "current_period_start": "2024-01-01T00:00:00Z",
    "current_period_end": "2024-12-31T23:59:59Z",
    "cancel_at_period_end": false,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## 🔧 Error Handling

### Error Response Format
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

### Common Error Messages
- `"User is not associated with any tenant"` - User needs to be assigned to a tenant
- `"Invalid mobile money provider"` - Provider not supported
- `"Invalid phone number format"` - Phone number validation failed
- `"Package not found"` - SMS package doesn't exist
- `"Insufficient credits"` - Not enough SMS credits for operation

## 📊 Data Models

### SMS Package
```json
{
  "id": "uuid",
  "name": "string",
  "package_type": "prepaid|subscription",
  "credits": "integer",
  "price": "decimal",
  "unit_price": "decimal",
  "is_popular": "boolean",
  "is_active": "boolean",
  "features": ["string"],
  "savings_percentage": "decimal",
  "default_sender_id": "string",
  "allowed_sender_ids": ["string"],
  "sender_id_restriction": "flexible|restricted|default_only",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### SMS Balance
```json
{
  "id": "uuid",
  "tenant": "string",
  "credits": "integer",
  "total_purchased": "integer",
  "total_used": "integer",
  "last_updated": "datetime",
  "created_at": "datetime"
}
```

### Purchase
```json
{
  "id": "uuid",
  "invoice_number": "string",
  "package": "uuid",
  "package_name": "string",
  "tenant": "string",
  "amount": "decimal",
  "credits": "integer",
  "unit_price": "decimal",
  "payment_method": "mobile_money|bank_transfer|cash",
  "payment_method_display": "string",
  "payment_reference": "string",
  "status": "pending|completed|failed|cancelled",
  "status_display": "string",
  "created_at": "datetime",
  "completed_at": "datetime"
}
```

### Payment Transaction
```json
{
  "id": "uuid",
  "order_id": "string",
  "amount": "decimal",
  "status": "pending|processing|completed|failed|cancelled|expired",
  "mobile_money_provider": "string",
  "phone_number": "string",
  "zenopay_order_id": "string",
  "zenopay_reference": "string",
  "zenopay_transid": "string",
  "zenopay_channel": "string",
  "zenopay_msisdn": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🔄 Real-time Updates

The API supports real-time updates through WebSocket connections for:
- Payment status changes
- SMS balance updates
- Usage statistics
- Purchase completion notifications

## 🚀 Rate Limiting

API requests are rate-limited to prevent abuse:
- 1000 requests per hour per user
- 100 requests per minute per user
- Burst allowance: 20 requests per second

## 📝 Notes

1. All monetary values are in Tanzanian Shillings (TZS)
2. Phone numbers must be in international format (e.g., 255712345678)
3. All timestamps are in UTC format
4. UUIDs are used for all resource identifiers
5. The API automatically handles tenant isolation
6. Payment transactions expire after 1 hour if not completed
