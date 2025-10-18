# Mifumo SMS Billing API - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication & Setup](#authentication--setup)
3. [API Endpoints](#api-endpoints)
   - [SMS Billing](#sms-billing)
   - [Payment Management](#payment-management)
   - [Subscription Management](#subscription-management)
   - [Custom SMS Purchase](#custom-sms-purchase)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Frontend Integration Guide](#frontend-integration-guide)
7. [Real-time Features](#real-time-features)
8. [Testing & Examples](#testing--examples)
9. [Security & Best Practices](#security--best-practices)

---

## Overview

The Mifumo SMS Billing API provides a comprehensive payment and credit management system for SMS services. It integrates with ZenoPay for mobile money payments in Tanzania and supports multiple payment providers including M-Pesa, Tigo Pesa, Airtel Money, and Halotel.

### Key Features
- **Multi-Provider Mobile Money**: Support for all major Tanzanian mobile money providers
- **Real-time Payment Tracking**: Live payment status updates with progress indicators
- **SMS Credit Management**: Package-based credit purchasing and usage tracking
- **Custom SMS Purchase**: Flexible credit purchasing with dynamic pricing
- **Subscription Management**: Billing plans and tenant subscriptions
- **Webhook Support**: Automated payment status updates
- **Multi-tenant Architecture**: Isolated billing per tenant
- **Comprehensive Analytics**: Usage statistics and billing insights

### Base URL
```
https://your-domain.com/api/billing/
```

---

## Authentication & Setup

### Authentication
All endpoints require JWT authentication via the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Tenant Association
Users must be associated with a tenant to access billing functionality. The system automatically filters all data based on the user's tenant.

### Content Type
All requests should include:
```http
Content-Type: application/json
```

---

## API Endpoints

## SMS Billing

### 1. List SMS Packages
**GET** `/api/billing/sms/packages/`

Retrieves available SMS packages for purchase with pricing and features.

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Lite Package",
            "package_type": "lite",
            "credits": 1000,
            "price": "25000.00",
            "unit_price": "25.00",
            "is_popular": false,
            "is_active": true,
            "features": [
                "1000 SMS Credits",
                "Standard Support",
                "Basic Analytics"
            ],
            "savings_percentage": 16.7,
            "default_sender_id": "Taarifa-SMS",
            "allowed_sender_ids": ["Taarifa-SMS", "Quantum"],
            "sender_id_restriction": "allowed_list",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Standard Package",
            "package_type": "standard",
            "credits": 5000,
            "price": "100000.00",
            "unit_price": "20.00",
            "is_popular": true,
            "is_active": true,
            "features": [
                "5000 SMS Credits",
                "Priority Support",
                "Advanced Analytics",
                "Bulk SMS Tools"
            ],
            "savings_percentage": 33.3,
            "default_sender_id": "Taarifa-SMS",
            "allowed_sender_ids": ["Taarifa-SMS", "Quantum", "Mifumo"],
            "sender_id_restriction": "allowed_list",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "count": 2
}
```

### 2. Get SMS Balance
**GET** `/api/billing/sms/balance/`

Retrieves current SMS credit balance and usage statistics for the tenant.

**Response (Success - 200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "credits": 1500,
    "total_purchased": 10000,
    "total_used": 8500,
    "last_updated": "2024-12-01T10:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "tenant": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Get Usage Statistics
**GET** `/api/billing/sms/usage/statistics/`

Retrieves detailed SMS usage statistics for billing and analytics.

**Query Parameters:**
- `period`: Time period (`daily`, `weekly`, `monthly`, `yearly`) - default: `monthly`
- `start_date`: Start date filter (YYYY-MM-DD)
- `end_date`: End date filter (YYYY-MM-DD)

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "current_balance": 1500,
        "total_usage": {
            "credits": 8500,
            "cost": 212500.00,
            "period": "all_time"
        },
        "monthly_usage": {
            "credits": 500,
            "cost": 12500.00,
            "period": "2024-12"
        },
        "weekly_usage": {
            "credits": 125,
            "cost": 3125.00,
            "period": "2024-W49"
        },
        "daily_usage": {
            "credits": 25,
            "cost": 625.00,
            "period": "2024-12-01"
        },
        "usage_trend": [
            {
                "date": "2024-11-25",
                "credits": 20,
                "cost": 500.00
            },
            {
                "date": "2024-11-26",
                "credits": 35,
                "cost": 875.00
            }
        ]
    }
}
```

### 4. List Purchase History
**GET** `/api/billing/sms/purchases/`

Retrieves purchase history for the tenant with filtering and pagination.

**Query Parameters:**
- `status`: Filter by status (`pending`, `completed`, `failed`, `cancelled`)
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "invoice_number": "INV-20241201-ABC12345",
            "package": "550e8400-e29b-41d4-a716-446655440001",
            "package_name": "Standard Package",
            "amount": "100000.00",
            "credits": 5000,
            "unit_price": "20.00",
            "payment_method": "zenopay_mobile_money",
            "payment_method_display": "ZenoPay Mobile Money",
            "payment_reference": "MPESA123456789",
            "status": "completed",
            "status_display": "Completed",
            "created_at": "2024-12-01T10:00:00Z",
            "completed_at": "2024-12-01T10:30:00Z",
            "tenant": "550e8400-e29b-41d4-a716-446655440000"
        }
    ],
    "count": 1,
    "next": null,
    "previous": null
}
```

### 5. Get Purchase Detail
**GET** `/api/billing/sms/purchases/{purchase_id}/`

Retrieves detailed information about a specific purchase.

**Response (Success - 200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "invoice_number": "INV-20241201-ABC12345",
    "package": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Standard Package",
        "package_type": "standard",
        "credits": 5000,
        "price": "100000.00",
        "unit_price": "20.00"
    },
    "amount": "100000.00",
    "credits": 5000,
    "unit_price": "20.00",
    "payment_method": "zenopay_mobile_money",
    "payment_method_display": "ZenoPay Mobile Money",
    "payment_reference": "MPESA123456789",
    "status": "completed",
    "status_display": "Completed",
    "created_at": "2024-12-01T10:00:00Z",
    "completed_at": "2024-12-01T10:30:00Z",
    "tenant": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Payment Management

### 1. Initiate Payment
**POST** `/api/billing/payments/initiate/`

Initiates a new payment with ZenoPay for SMS package purchase.

**Request Body:**
```json
{
    "package_id": "550e8400-e29b-41d4-a716-446655440001",
    "buyer_email": "user@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
}
```

**Mobile Money Providers:**
- `vodacom` - M-Pesa (Vodacom)
- `tigo` - Tigo Pesa
- `airtel` - Airtel Money
- `halotel` - Halotel Money

**Response (Success - 201):**
```json
{
    "success": true,
    "message": "Payment initiated successfully. Please complete payment on your mobile device.",
    "data": {
        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
        "order_id": "MIFUMO-20241201-ABC12345",
        "amount": 100000.00,
        "currency": "TZS",
        "mobile_money_provider": "vodacom",
        "provider_name": "Vodacom M-Pesa",
        "credits": 5000,
        "package": {
            "name": "Standard Package",
            "credits": 5000,
            "price": 100000.00
        },
        "payment_instructions": "Request in progress. You will receive a callback shortly",
        "timeout_seconds": 300,
        "created_at": "2024-12-01T10:00:00Z"
    }
}
```

### 2. Verify Payment
**GET** `/api/billing/payments/verify/{order_id}/`

Checks the status of a payment using the order ID.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
        "order_id": "MIFUMO-20241201-ABC12345",
        "status": "completed",
        "status_display": "Payment Completed",
        "amount": 100000.00,
        "currency": "TZS",
        "payment_reference": "MPESA123456789",
        "provider": "vodacom",
        "provider_name": "Vodacom M-Pesa",
        "completed_at": "2024-12-01T10:30:00Z",
        "created_at": "2024-12-01T10:00:00Z"
    }
}
```

### 3. Get Active Payments
**GET** `/api/billing/payments/active/`

Retrieves all active (pending) payments for the tenant.

**Response (Success - 200):**
```json
{
    "success": true,
    "active_payments": {
        "550e8400-e29b-41d4-a716-446655440000": {
            "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
            "order_id": "MIFUMO-20241201-ABC12345",
            "invoice_number": "INV-20241201-ABC12345",
            "amount": 100000.00,
            "status": "pending",
            "created_at": "2024-12-01T10:00:00Z",
            "updated_at": "2024-12-01T10:00:00Z",
            "timeout_in": 150
        }
    },
    "expired_payments": [
        {
            "transaction_id": "550e8400-e29b-41d4-a716-446655440001",
            "order_id": "MIFUMO-20241201-DEF67890",
            "amount": 50000.00,
            "reason": "timeout"
        }
    ],
    "count": 1
}
```

### 4. Payment Progress
**GET** `/api/billing/payments/transactions/{transaction_id}/progress/`

Gets real-time payment progress with user-friendly status updates.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
        "order_id": "MIFUMO-20241201-ABC12345",
        "status": "processing",
        "status_display": "Processing Payment",
        "progress_percentage": 75,
        "current_step": "Waiting for mobile money confirmation",
        "steps": [
            {
                "step": "Payment initiated",
                "completed": true,
                "timestamp": "2024-12-01T10:00:00Z"
            },
            {
                "step": "Mobile money request sent",
                "completed": true,
                "timestamp": "2024-12-01T10:00:05Z"
            },
            {
                "step": "Waiting for mobile money confirmation",
                "completed": false,
                "timestamp": null
            },
            {
                "step": "Payment verification",
                "completed": false,
                "timestamp": null
            }
        ],
        "estimated_completion": "2024-12-01T10:05:00Z",
        "timeout_in": 150
    }
}
```

### 5. Cancel Payment
**POST** `/api/billing/payments/transactions/{transaction_id}/cancel/`

Cancels an active payment.

**Response (Success - 200):**
```json
{
    "success": true,
    "message": "Payment cancelled successfully.",
    "cancelled_order": "MIFUMO-20241201-ABC12345"
}
```

### 6. List Payment Transactions
**GET** `/api/billing/payments/transactions/`

Retrieves payment transaction history with filtering and pagination.

**Query Parameters:**
- `status`: Filter by status (`pending`, `completed`, `failed`, `cancelled`)
- `provider`: Filter by mobile money provider
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "order_id": "MIFUMO-20241201-ABC12345",
            "invoice_number": "INV-20241201-ABC12345",
            "amount": 100000.00,
            "currency": "TZS",
            "status": "completed",
            "status_display": "Payment Completed",
            "payment_reference": "MPESA123456789",
            "provider": "vodacom",
            "provider_name": "Vodacom M-Pesa",
            "created_at": "2024-12-01T10:00:00Z",
            "completed_at": "2024-12-01T10:30:00Z",
            "tenant": "550e8400-e29b-41d4-a716-446655440000"
        }
    ],
    "count": 1,
    "next": null,
    "previous": null
}
```

### 7. Get Mobile Money Providers
**GET** `/api/billing/payments/providers/`

Retrieves available mobile money providers with their details.

**Response (Success - 200):**
```json
{
    "success": true,
    "providers": [
        {
            "code": "vodacom",
            "name": "Vodacom M-Pesa",
            "description": "Pay with M-Pesa via Vodacom",
            "icon": "https://example.com/icons/mpesa.png",
            "is_active": true,
            "min_amount": 1000,
            "max_amount": 1000000
        },
        {
            "code": "tigo",
            "name": "Tigo Pesa",
            "description": "Pay with Tigo Pesa",
            "icon": "https://example.com/icons/tigo.png",
            "is_active": true,
            "min_amount": 1000,
            "max_amount": 1000000
        },
        {
            "code": "airtel",
            "name": "Airtel Money",
            "description": "Pay with Airtel Money",
            "icon": "https://example.com/icons/airtel.png",
            "is_active": true,
            "min_amount": 1000,
            "max_amount": 1000000
        },
        {
            "code": "halotel",
            "name": "Halotel Money",
            "description": "Pay with Halotel Money",
            "icon": "https://example.com/icons/halotel.png",
            "is_active": true,
            "min_amount": 1000,
            "max_amount": 1000000
        }
    ]
}
```

---

## Custom SMS Purchase

### 1. Calculate Custom SMS Pricing
**POST** `/api/billing/payments/custom-sms/calculate/`

Calculates pricing for custom SMS credit amounts with dynamic tier-based pricing.

**Request Body:**
```json
{
    "credits": 5000
}
```

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "credits": 5000,
        "unit_price": 20.00,
        "total_price": 100000.00,
        "active_tier": "Standard",
        "tier_min_credits": 1000,
        "tier_max_credits": 10000,
        "savings_percentage": 33.3,
        "pricing_tiers": [
            {
                "name": "Lite",
                "min_credits": 100,
                "max_credits": 999,
                "unit_price": 30.00,
                "description": "For small businesses"
            },
            {
                "name": "Standard",
                "min_credits": 1000,
                "max_credits": 10000,
                "unit_price": 20.00,
                "description": "For growing businesses"
            },
            {
                "name": "Pro",
                "min_credits": 10001,
                "max_credits": 50000,
                "unit_price": 15.00,
                "description": "For established businesses"
            },
            {
                "name": "Enterprise",
                "min_credits": 50001,
                "max_credits": 999999,
                "unit_price": 10.00,
                "description": "For large enterprises"
            }
        ]
    }
}
```

### 2. Initiate Custom SMS Purchase
**POST** `/api/billing/payments/custom-sms/initiate/`

Initiates a custom SMS purchase with ZenoPay.

**Request Body:**
```json
{
    "credits": 5000,
    "buyer_email": "user@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
}
```

**Response (Success - 201):**
```json
{
    "success": true,
    "message": "Custom SMS purchase initiated successfully. Please complete payment on your mobile device.",
    "data": {
        "purchase_id": "550e8400-e29b-41d4-a716-446655440000",
        "credits": 5000,
        "unit_price": 20.00,
        "total_price": 100000.00,
        "active_tier": "Standard",
        "status": "processing",
        "payment_instructions": "Request in progress. You will receive a callback shortly",
        "timeout_seconds": 300,
        "created_at": "2024-12-01T10:00:00Z"
    }
}
```

### 3. Check Custom SMS Purchase Status
**GET** `/api/billing/payments/custom-sms/{purchase_id}/status/`

Checks the status of a custom SMS purchase.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "purchase_id": "550e8400-e29b-41d4-a716-446655440000",
        "credits": 5000,
        "unit_price": 20.00,
        "total_price": 100000.00,
        "status": "completed",
        "status_display": "Purchase Completed",
        "payment_reference": "MPESA123456789",
        "provider": "vodacom",
        "provider_name": "Vodacom M-Pesa",
        "created_at": "2024-12-01T10:00:00Z",
        "completed_at": "2024-12-01T10:30:00Z"
    }
}
```

---

## Subscription Management

### 1. List Billing Plans
**GET** `/api/billing/plans/`

Retrieves available subscription plans.

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Professional",
            "plan_type": "professional",
            "description": "Professional plan with advanced features",
            "price": "50000.00",
            "currency": "TZS",
            "billing_cycle": "monthly",
            "max_contacts": 10000,
            "max_campaigns": 100,
            "max_sms_per_month": 5000,
            "features": [
                "Advanced Analytics",
                "Priority Support",
                "Bulk SMS Tools",
                "Custom Sender IDs"
            ],
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "count": 1
}
```

### 2. Get Subscription Details
**GET** `/api/billing/subscription/`

Retrieves current subscription details for the tenant.

**Response (Success - 200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "plan": "550e8400-e29b-41d4-a716-446655440000",
    "plan_name": "Professional",
    "status": "active",
    "status_display": "Active",
    "current_period_start": "2024-11-01T00:00:00Z",
    "current_period_end": "2024-12-01T00:00:00Z",
    "cancel_at_period_end": false,
    "is_active": true,
    "created_at": "2024-11-01T00:00:00Z",
    "tenant": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Get Billing Overview
**GET** `/api/billing/overview/`

Retrieves comprehensive billing overview for the tenant.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "subscription": {
            "plan_name": "Professional",
            "status": "active",
            "current_period_end": "2024-12-01T00:00:00Z",
            "is_active": true
        },
        "sms_balance": {
            "credits": 1500,
            "total_purchased": 10000,
            "total_used": 8500
        },
        "recent_purchases": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "package_name": "Standard Package",
                "amount": "100000.00",
                "credits": 5000,
                "status": "completed",
                "created_at": "2024-12-01T10:00:00Z"
            }
        ],
        "usage_summary": {
            "this_month": {
                "credits": 500,
                "cost": 12500.00
            },
            "last_month": {
                "credits": 750,
                "cost": 18750.00
            }
        },
        "active_payments": 1
    }
}
```

---

## Data Models

### SMS Package
```json
{
    "id": "uuid",
    "name": "string",
    "package_type": "lite|standard|pro|enterprise|custom",
    "credits": "integer",
    "price": "decimal",
    "unit_price": "decimal",
    "is_popular": "boolean",
    "is_active": "boolean",
    "features": ["string"],
    "savings_percentage": "decimal",
    "default_sender_id": "string",
    "allowed_sender_ids": ["string"],
    "sender_id_restriction": "none|default_only|allowed_list|custom_only",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Payment Transaction
```json
{
    "id": "uuid",
    "order_id": "string",
    "invoice_number": "string",
    "amount": "decimal",
    "currency": "string",
    "status": "pending|completed|failed|cancelled",
    "payment_reference": "string",
    "provider": "string",
    "provider_name": "string",
    "created_at": "datetime",
    "completed_at": "datetime",
    "tenant": "uuid"
}
```

### SMS Balance
```json
{
    "id": "uuid",
    "credits": "integer",
    "total_purchased": "integer",
    "total_used": "integer",
    "last_updated": "datetime",
    "created_at": "datetime",
    "tenant": "uuid"
}
```

---

## Error Handling

### Standard Error Response
```json
{
    "success": false,
    "message": "Error description",
    "error_code": "ERROR_CODE",
    "details": {
        "field_name": ["Specific error message"]
    }
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Common Error Codes
- `INVALID_PACKAGE`: Package not found or inactive
- `INSUFFICIENT_BALANCE`: Not enough SMS credits
- `PAYMENT_FAILED`: Payment processing failed
- `PAYMENT_TIMEOUT`: Payment request timed out
- `INVALID_PHONE`: Invalid phone number format
- `TENANT_REQUIRED`: User not associated with tenant
- `RATE_LIMITED`: Too many requests

---

## Frontend Integration Guide

### 1. Payment Flow Integration

#### Step 1: Display Packages
```javascript
// Fetch available packages
const fetchPackages = async () => {
    const response = await fetch('/api/billing/sms/packages/', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    return data.results;
};
```

#### Step 2: Initiate Payment
```javascript
// Initiate payment for selected package
const initiatePayment = async (packageId, buyerInfo) => {
    const response = await fetch('/api/billing/payments/initiate/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            package_id: packageId,
            buyer_email: buyerInfo.email,
            buyer_name: buyerInfo.name,
            buyer_phone: buyerInfo.phone,
            mobile_money_provider: buyerInfo.provider
        })
    });
    return await response.json();
};
```

#### Step 3: Track Payment Progress
```javascript
// Poll payment status with progress updates
const trackPayment = async (transactionId) => {
    const pollInterval = setInterval(async () => {
        const response = await fetch(`/api/billing/payments/transactions/${transactionId}/progress/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        
        // Update UI with progress
        updatePaymentProgress(data.data);
        
        // Stop polling when completed or failed
        if (['completed', 'failed', 'cancelled'].includes(data.data.status)) {
            clearInterval(pollInterval);
            handlePaymentComplete(data.data);
        }
    }, 2000); // Poll every 2 seconds
};
```

### 2. Real-time Updates

#### WebSocket Integration (if available)
```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('wss://your-domain.com/ws/billing/');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'payment_update') {
        updatePaymentStatus(data.transaction_id, data.status);
    }
};
```

#### Polling for Updates
```javascript
// Alternative: Poll for updates
const pollForUpdates = () => {
    setInterval(async () => {
        const response = await fetch('/api/billing/payments/active/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        updateActivePayments(data.active_payments);
    }, 5000); // Poll every 5 seconds
};
```

### 3. Error Handling
```javascript
// Comprehensive error handling
const handleApiError = (error, response) => {
    if (response?.status === 401) {
        // Redirect to login
        window.location.href = '/login';
    } else if (response?.status === 403) {
        // Show permission error
        showError('You do not have permission to perform this action');
    } else if (response?.status === 400) {
        // Show validation errors
        const errorData = response.json();
        showValidationErrors(errorData.details);
    } else {
        // Show generic error
        showError('An unexpected error occurred. Please try again.');
    }
};
```

### 4. UI Components

#### Payment Progress Component
```javascript
const PaymentProgress = ({ transactionId }) => {
    const [progress, setProgress] = useState(null);
    
    useEffect(() => {
        const trackProgress = async () => {
            const response = await fetch(`/api/billing/payments/transactions/${transactionId}/progress/`);
            const data = await response.json();
            setProgress(data.data);
        };
        
        const interval = setInterval(trackProgress, 2000);
        return () => clearInterval(interval);
    }, [transactionId]);
    
    return (
        <div className="payment-progress">
            <div className="progress-bar">
                <div 
                    className="progress-fill" 
                    style={{ width: `${progress?.progress_percentage || 0}%` }}
                />
            </div>
            <p>{progress?.current_step}</p>
        </div>
    );
};
```

#### Package Selection Component
```javascript
const PackageSelector = ({ packages, onSelect }) => {
    return (
        <div className="package-grid">
            {packages.map(package => (
                <div 
                    key={package.id} 
                    className={`package-card ${package.is_popular ? 'popular' : ''}`}
                    onClick={() => onSelect(package)}
                >
                    <h3>{package.name}</h3>
                    <div className="credits">{package.credits} Credits</div>
                    <div className="price">TZS {package.price}</div>
                    <div className="unit-price">TZS {package.unit_price} per SMS</div>
                    {package.savings_percentage > 0 && (
                        <div className="savings">Save {package.savings_percentage}%</div>
                    )}
                </div>
            ))}
        </div>
    );
};
```

---

## Real-time Features

### 1. Payment Status Updates
The API provides real-time payment status updates through:
- **Progress Polling**: Regular status checks with detailed progress information
- **WebSocket Support**: Real-time updates (if WebSocket is implemented)
- **Webhook Integration**: Server-to-server notifications for payment completion

### 2. Live Balance Updates
SMS credit balance is updated in real-time when:
- Payments are completed
- SMS messages are sent
- Credits are manually adjusted

### 3. Usage Statistics
Real-time usage statistics are available for:
- Current balance
- Daily, weekly, monthly usage
- Usage trends and patterns
- Cost analysis

---

## Testing & Examples

### 1. cURL Examples

#### Get SMS Packages
```bash
curl -X GET "https://your-domain.com/api/billing/sms/packages/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

#### Initiate Payment
```bash
curl -X POST "https://your-domain.com/api/billing/payments/initiate/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "package_id": "550e8400-e29b-41d4-a716-446655440001",
    "buyer_email": "user@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
  }'
```

#### Check Payment Status
```bash
curl -X GET "https://your-domain.com/api/billing/payments/verify/MIFUMO-20241201-ABC12345/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. JavaScript Examples

#### Complete Payment Flow
```javascript
class BillingAPI {
    constructor(baseURL, token) {
        this.baseURL = baseURL;
        this.token = token;
    }
    
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    }
    
    // Get SMS packages
    async getPackages() {
        return await this.request('/api/billing/sms/packages/');
    }
    
    // Initiate payment
    async initiatePayment(packageId, buyerInfo) {
        return await this.request('/api/billing/payments/initiate/', {
            method: 'POST',
            body: JSON.stringify({
                package_id: packageId,
                ...buyerInfo
            })
        });
    }
    
    // Track payment progress
    async trackPayment(transactionId) {
        return await this.request(`/api/billing/payments/transactions/${transactionId}/progress/`);
    }
    
    // Get SMS balance
    async getBalance() {
        return await this.request('/api/billing/sms/balance/');
    }
}

// Usage
const billingAPI = new BillingAPI('https://your-domain.com', 'YOUR_JWT_TOKEN');

// Complete payment flow
async function purchasePackage(packageId, buyerInfo) {
    try {
        // 1. Initiate payment
        const payment = await billingAPI.initiatePayment(packageId, buyerInfo);
        console.log('Payment initiated:', payment);
        
        // 2. Track progress
        const trackInterval = setInterval(async () => {
            const progress = await billingAPI.trackPayment(payment.data.transaction_id);
            console.log('Payment progress:', progress);
            
            if (['completed', 'failed', 'cancelled'].includes(progress.data.status)) {
                clearInterval(trackInterval);
                console.log('Payment completed:', progress);
            }
        }, 2000);
        
    } catch (error) {
        console.error('Payment failed:', error);
    }
}
```

### 3. Postman Collection
A complete Postman collection is available with:
- All API endpoints
- Sample requests and responses
- Environment variables
- Test scripts
- Documentation

---

## Security & Best Practices

### 1. Authentication
- Always use HTTPS in production
- Store JWT tokens securely
- Implement token refresh mechanism
- Use short-lived tokens

### 2. Data Validation
- Validate all input data on the frontend
- Sanitize user inputs
- Use proper phone number validation
- Implement rate limiting

### 3. Error Handling
- Never expose sensitive information in error messages
- Log errors for debugging
- Implement proper fallback mechanisms
- Use user-friendly error messages

### 4. Payment Security
- Never store payment details
- Use secure payment providers
- Implement proper webhook verification
- Monitor for suspicious activities

### 5. API Usage
- Implement proper caching
- Use pagination for large datasets
- Implement request debouncing
- Monitor API usage and limits

---

## Support & Contact

For technical support or questions about the billing API:

- **Documentation**: This comprehensive guide
- **API Status**: Check system status page
- **Support Email**: support@mifumo.com
- **Developer Portal**: https://developers.mifumo.com

---

*This documentation is regularly updated. Please check for the latest version before implementation.*
