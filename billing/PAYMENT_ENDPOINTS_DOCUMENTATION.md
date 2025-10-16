# Payment Endpoints Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Payment Management](#payment-management)
   - [SMS Billing](#sms-billing)
   - [Subscription Management](#subscription-management)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Integration Examples](#integration-examples)
7. [Security Considerations](#security-considerations)
8. [Testing](#testing)

---

## Overview

The Mifumo SMS billing system provides comprehensive payment processing capabilities through ZenoPay integration, SMS credit management, and subscription handling. The system supports mobile money payments in Tanzania and provides real-time payment tracking with user-friendly progress indicators.

### Key Features
- **ZenoPay Integration**: Mobile money payments via M-Pesa, Tigo Pesa, and Airtel Money
- **Real-time Payment Tracking**: Progress indicators and status updates
- **SMS Credit Management**: Package-based credit purchasing and usage tracking
- **Subscription Management**: Billing plans and tenant subscriptions
- **Webhook Support**: Automated payment status updates
- **Multi-tenant Architecture**: Isolated billing per tenant

---

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

**Note**: Users must be associated with a tenant to access billing functionality.

---

## API Endpoints

### Payment Management

#### 1. Initiate Payment
**POST** `/api/billing/payments/initiate/`

Initiates a new payment with ZenoPay for SMS package purchase.

**Request Body:**
```json
{
    "package_id": "uuid",
    "buyer_email": "user@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858"
}
```

**Response (Success - 201):**
```json
{
    "success": true,
    "message": "Payment initiated successfully. Please complete payment on your mobile device.",
    "data": {
        "transaction_id": "uuid",
        "order_id": "MIFUMO-20241201-ABC12345",
        "zenopay_order_id": "zenopay-uuid",
        "invoice_number": "INV-20241201-ABC12345",
        "amount": 1000.00,
        "credits": 100,
        "status": "pending",
        "payment_instructions": "Please check your phone for mobile money prompt",
        "progress": {
            "step": 1,
            "total_steps": 4,
            "current_step": "Payment Initiated",
            "next_step": "Complete Payment on Mobile",
            "completed_steps": ["Payment Initiated"],
            "remaining_steps": ["Complete Payment on Mobile", "Payment Verification", "Credits Added"]
        }
    }
}
```

#### 2. Check Payment Status
**GET** `/api/billing/payments/transactions/{transaction_id}/status/`

Checks payment status and updates progress.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "transaction_id": "uuid",
        "order_id": "MIFUMO-20241201-ABC12345",
        "status": "completed",
        "payment_status": "SUCCESS",
        "amount": 1000.00,
        "reference": "MPESA123456789",
        "progress": {
            "step": 4,
            "total_steps": 4,
            "current_step": "Payment Completed",
            "next_step": null,
            "completed_steps": ["Payment Initiated", "Complete Payment on Mobile", "Payment Verification", "Credits Added"],
            "remaining_steps": [],
            "percentage": 100,
            "status_color": "green",
            "status_icon": "check"
        },
        "updated_at": "2024-12-01T10:30:00Z"
    }
}
```

#### 3. Verify Payment
**GET** `/api/billing/payments/verify/{order_id}/`

Verifies payment status by order_id.

**Response (Success - 200):**
```json
{
    "success": true,
    "status": "completed",
    "amount": 1000.00,
    "transaction_reference": "MPESA123456789",
    "message": "Payment verified and completed successfully! Credits have been added to your account.",
    "last_checked": "2024-12-01T10:30:00Z"
}
```

#### 4. Get Payment Progress
**GET** `/api/billing/payments/transactions/{transaction_id}/progress/`

Gets detailed payment progress for user-friendly display.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "transaction_id": "uuid",
        "order_id": "MIFUMO-20241201-ABC12345",
        "invoice_number": "INV-20241201-ABC12345",
        "amount": 1000.00,
        "currency": "TZS",
        "status": "completed",
        "payment_status": "SUCCESS",
        "progress": {
            "step": 4,
            "total_steps": 4,
            "current_step": "Payment Completed",
            "next_step": null,
            "completed_steps": ["Payment Initiated", "Complete Payment on Mobile", "Payment Verification", "Credits Added"],
            "remaining_steps": [],
            "percentage": 100,
            "status_color": "green",
            "status_icon": "check"
        },
        "purchase": {
            "package_name": "Standard Package",
            "credits": 100,
            "unit_price": 10.00
        },
        "created_at": "2024-12-01T10:00:00Z",
        "updated_at": "2024-12-01T10:30:00Z",
        "completed_at": "2024-12-01T10:30:00Z"
    }
}
```

#### 5. Get Active Payments
**GET** `/api/billing/payments/active/`

Gets all active payment processes for the current user.

**Response (Success - 200):**
```json
{
    "success": true,
    "active_payments": {
        "transaction-uuid-1": {
            "transaction_id": "transaction-uuid-1",
            "order_id": "MIFUMO-20241201-ABC12345",
            "invoice_number": "INV-20241201-ABC12345",
            "amount": 1000.00,
            "status": "pending",
            "created_at": "2024-12-01T10:00:00Z",
            "updated_at": "2024-12-01T10:00:00Z",
            "timeout_in": 1500
        }
    },
    "expired_payments": [
        {
            "transaction_id": "transaction-uuid-2",
            "order_id": "MIFUMO-20241201-DEF67890",
            "amount": 500.00,
            "reason": "timeout"
        }
    ],
    "count": 1
}
```

#### 6. Cancel Payment
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

#### 7. Cleanup Payments
**POST** `/api/billing/payments/cleanup/`

Cleans up expired payment processes.

**Response (Success - 200):**
```json
{
    "success": true,
    "message": "Cleaned up 3 expired payment processes.",
    "cleaned_count": 3
}
```

#### 8. Payment Webhook
**POST** `/api/billing/payments/webhook/`

Handles ZenoPay webhook notifications.

**Request Body (from ZenoPay):**
```json
{
    "order_id": "zenopay-uuid",
    "payment_status": "COMPLETED",
    "reference": "MPESA123456789",
    "transid": "TXN123456789",
    "channel": "MPESA-TZ",
    "msisdn": "255744963858"
}
```

**Response (Success - 200):**
```json
{
    "success": true,
    "message": "Webhook processed successfully"
}
```

### SMS Billing

#### 1. List SMS Packages
**GET** `/api/billing/sms/packages/`

Lists available SMS packages for purchase.

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "uuid",
            "name": "Standard Package",
            "package_type": "standard",
            "credits": 100,
            "price": "1000.00",
            "unit_price": "10.00",
            "is_popular": true,
            "features": ["SMS Credits", "Priority Support"],
            "savings_percentage": 66.7
        }
    ]
}
```

#### 2. Get SMS Balance
**GET** `/api/billing/sms/balance/`

Gets current SMS credit balance for the tenant.

**Response (Success - 200):**
```json
{
    "id": "uuid",
    "credits": 150,
    "total_purchased": 500,
    "total_used": 350,
    "last_updated": "2024-12-01T10:30:00Z",
    "created_at": "2024-11-01T10:00:00Z"
}
```

#### 3. Create Purchase
**POST** `/api/billing/sms/purchase/`

Creates a new SMS credit purchase (legacy endpoint - use payment initiation instead).

**Request Body:**
```json
{
    "package_id": "uuid",
    "payment_method": "zenopay_mobile_money",
    "payment_reference": "optional"
}
```

#### 4. List Purchases
**GET** `/api/billing/sms/purchases/`

Lists purchase history for the tenant.

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "uuid",
            "invoice_number": "INV-20241201-ABC12345",
            "package": "uuid",
            "package_name": "Standard Package",
            "amount": "1000.00",
            "credits": 100,
            "unit_price": "10.00",
            "payment_method": "zenopay_mobile_money",
            "payment_method_display": "ZenoPay Mobile Money",
            "payment_reference": "",
            "status": "completed",
            "status_display": "Completed",
            "created_at": "2024-12-01T10:00:00Z",
            "completed_at": "2024-12-01T10:30:00Z"
        }
    ]
}
```

#### 5. Purchase History
**GET** `/api/billing/sms/purchases/history/`

Gets detailed purchase history with filtering.

**Query Parameters:**
- `status`: Filter by purchase status
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

#### 6. Usage Statistics
**GET** `/api/billing/sms/usage/statistics/`

Gets SMS usage statistics for billing.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "current_balance": 150,
        "total_usage": {
            "credits": 350,
            "cost": 8750.00
        },
        "monthly_usage": {
            "credits": 100,
            "cost": 2500.00
        },
        "weekly_usage": {
            "credits": 25,
            "cost": 625.00
        }
    }
}
```

### Subscription Management

#### 1. List Billing Plans
**GET** `/api/billing/plans/`

Lists available subscription plans.

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "uuid",
            "name": "Professional",
            "plan_type": "professional",
            "description": "Professional plan with advanced features",
            "price": "50000.00",
            "currency": "TZS",
            "billing_cycle": "monthly",
            "max_contacts": 10000,
            "max_campaigns": 100,
            "max_sms_per_month": 5000,
            "features": ["Advanced Analytics", "Priority Support"],
            "is_active": true
        }
    ]
}
```

#### 2. Get Subscription
**GET** `/api/billing/subscription/`

Gets current subscription details.

**Response (Success - 200):**
```json
{
    "id": "uuid",
    "plan": "uuid",
    "plan_name": "Professional",
    "status": "active",
    "status_display": "Active",
    "current_period_start": "2024-11-01T00:00:00Z",
    "current_period_end": "2024-12-01T00:00:00Z",
    "cancel_at_period_end": false,
    "is_active": true,
    "created_at": "2024-11-01T00:00:00Z"
}
```

#### 3. Get Billing Overview
**GET** `/api/billing/overview/`

Gets comprehensive billing overview for the tenant.

**Response (Success - 200):**
```json
{
    "success": true,
    "data": {
        "subscription": {
            "plan_id": "uuid",
            "plan_name": "Professional",
            "status": "active",
            "current_period_end": "2024-12-01T23:59:59Z",
            "is_active": true
        },
        "usage": {
            "total_credits": 12345,
            "total_cost": 456.78
        }
    }
}
```

#### 4. List Usage Records
**GET** `/api/billing/usage/`

Lists usage records for the tenant.

**Response (Success - 200):**
```json
{
    "results": [
        {
            "id": "uuid",
            "credits_used": 1,
            "cost": "25.00",
            "created_at": "2024-12-01T10:30:00Z"
        }
    ]
}
```

---

## Data Models

### PaymentTransaction
```python
{
    "id": "uuid",
    "tenant": "tenant_id",
    "user": "user_id",
    "zenopay_order_id": "string",
    "zenopay_reference": "string",
    "zenopay_transid": "string",
    "zenopay_channel": "string",
    "zenopay_msisdn": "string",
    "order_id": "string",
    "invoice_number": "string",
    "amount": "decimal",
    "currency": "string",
    "buyer_email": "email",
    "buyer_name": "string",
    "buyer_phone": "string",
    "payment_method": "string",
    "payment_reference": "string",
    "status": "string",
    "webhook_url": "url",
    "webhook_received": "boolean",
    "webhook_data": "json",
    "created_at": "datetime",
    "updated_at": "datetime",
    "completed_at": "datetime",
    "failed_at": "datetime",
    "metadata": "json",
    "error_message": "text"
}
```

### Purchase
```python
{
    "id": "uuid",
    "tenant": "tenant_id",
    "user": "user_id",
    "package": "package_id",
    "payment_transaction": "transaction_id",
    "invoice_number": "string",
    "amount": "decimal",
    "credits": "integer",
    "unit_price": "decimal",
    "payment_method": "string",
    "payment_reference": "string",
    "status": "string",
    "created_at": "datetime",
    "completed_at": "datetime",
    "updated_at": "datetime"
}
```

### SMSPackage
```python
{
    "id": "uuid",
    "name": "string",
    "package_type": "string",
    "credits": "integer",
    "price": "decimal",
    "unit_price": "decimal",
    "is_popular": "boolean",
    "is_active": "boolean",
    "features": "json",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

---

## Error Handling

### Common Error Codes
- `PAYMENT_NOT_FOUND` - Payment not found
- `PAYMENT_EXPIRED` - Payment session expired
- `PAYMENT_VERIFICATION_FAILED` - Payment verification failed
- `INVALID_PHONE_FORMAT` - Invalid phone number format
- `MISSING_PHONE_NUMBER` - Phone number required
- `INVALID_CONTENT_ID` - Invalid package ID
- `NO_SUBSCRIPTION` - No subscription found
- `SUBSCRIPTION_MISSING_PLAN` - Subscription exists but has no plan assigned

### Error Response Format
```json
{
    "success": false,
    "message": "Error description",
    "error_code": "ERROR_CODE",
    "detail": "Additional error details"
}
```

---

## Integration Examples

### Frontend Integration (JavaScript)

```javascript
// Payment initiation
const initiatePayment = async (packageId, buyerDetails) => {
    const response = await fetch('/api/billing/payments/initiate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            package_id: packageId,
            ...buyerDetails
        })
    });
    return response.json();
};

// Check payment status
const checkPaymentStatus = async (transactionId) => {
    const response = await fetch(`/api/billing/payments/transactions/${transactionId}/status/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};

// Verify payment
const verifyPayment = async (orderId) => {
    const response = await fetch(`/api/billing/payments/verify/${orderId}/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};

// Get active payments
const getActivePayments = async () => {
    const response = await fetch('/api/billing/payments/active/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};

// Cancel payment
const cancelPayment = async (transactionId) => {
    const response = await fetch(`/api/billing/payments/transactions/${transactionId}/cancel/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};
```

### Payment Flow Example

```javascript
// Complete payment flow
const completePaymentFlow = async (packageId, buyerDetails) => {
    try {
        // 1. Initiate payment
        const initiateResponse = await initiatePayment(packageId, buyerDetails);
        if (!initiateResponse.success) {
            throw new Error(initiateResponse.message);
        }
        
        const { transaction_id, order_id } = initiateResponse.data;
        
        // 2. Poll for payment status
        const pollInterval = setInterval(async () => {
            const statusResponse = await checkPaymentStatus(transaction_id);
            
            if (statusResponse.success) {
                const { status, progress } = statusResponse.data;
                
                // Update UI with progress
                updatePaymentProgress(progress);
                
                if (status === 'completed') {
                    clearInterval(pollInterval);
                    showSuccessMessage('Payment completed successfully!');
                } else if (status === 'failed' || status === 'expired') {
                    clearInterval(pollInterval);
                    showErrorMessage('Payment failed or expired');
                }
            }
        }, 5000); // Check every 5 seconds
        
        // 3. Timeout after 30 minutes
        setTimeout(() => {
            clearInterval(pollInterval);
            showErrorMessage('Payment timeout');
        }, 30 * 60 * 1000);
        
    } catch (error) {
        console.error('Payment flow error:', error);
        showErrorMessage(error.message);
    }
};
```

---

## Security Considerations

1. **Authentication Required** - All endpoints require user authentication
2. **Tenant Isolation** - Users can only access their own payments and data
3. **Input Validation** - Comprehensive validation of all inputs
4. **Rate Limiting** - Consider implementing rate limiting for production
5. **Webhook Security** - Verify webhook authenticity in production
6. **Phone Number Validation** - Tanzanian mobile number format validation
7. **HTTPS Only** - All API calls should use HTTPS in production

---

## Testing

### Test Scenarios
1. **Valid Payment Flows**
   - Successful payment initiation
   - Payment completion via webhook
   - Payment verification

2. **Error Conditions**
   - Invalid package ID
   - Invalid phone number format
   - Network errors
   - Timeout scenarios

3. **Edge Cases**
   - Duplicate payment attempts
   - Expired payment sessions
   - Webhook processing failures
   - Database transaction rollbacks

### Test Data
```json
{
    "valid_package_id": "use actual package ID from database",
    "valid_phone": "0744963858",
    "valid_email": "test@example.com",
    "valid_name": "Test User"
}
```

---

## Database Migrations

Run the following commands to apply database changes:

```bash
python manage.py makemigrations billing
python manage.py migrate
```

---

## Monitoring and Logging

### Key Metrics to Monitor
1. Payment success rates
2. Failed payment reasons
3. Webhook processing times
4. Cleanup job performance
5. User payment patterns

### Log Levels
- **INFO**: Normal operations, payment status changes
- **WARNING**: Non-critical issues, expired payments
- **ERROR**: Payment failures, webhook errors
- **DEBUG**: Detailed request/response data (development only)

---

## Support

For technical support or questions about the payment system, please contact the development team or refer to the main project documentation.