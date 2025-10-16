# ZenoPay Payment Gateway Integration Documentation

## Overview

This document provides comprehensive documentation for the ZenoPay Mobile Money Tanzania payment gateway integration in the Mifumo WMS billing system. The integration includes user-friendly progress tracking and real-time payment status updates.

## Table of Contents

1. [Features](#features)
2. [API Endpoints](#api-endpoints)
3. [Payment Flow](#payment-flow)
4. [Progress Tracking](#progress-tracking)
5. [Webhook Integration](#webhook-integration)
6. [Error Handling](#error-handling)
7. [Frontend Integration](#frontend-integration)
8. [Configuration](#configuration)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Features

### Core Features
- **Mobile Money Integration**: Seamless integration with Tanzanian mobile money providers (M-Pesa, Tigo Pesa, Airtel Money)
- **Real-time Progress Tracking**: User-friendly progress indicators with step-by-step status updates
- **Webhook Support**: Automatic payment status updates via webhooks
- **Transaction Management**: Complete transaction lifecycle management
- **Error Handling**: Comprehensive error handling and user feedback
- **Security**: Secure API key authentication and webhook verification

### User Experience Features
- **Progress Indicators**: Visual progress bars showing payment stages
- **Status Updates**: Real-time status updates during payment processing
- **Error Messages**: Clear, actionable error messages
- **Retry Mechanisms**: Easy retry options for failed payments
- **Transaction History**: Complete transaction history and receipts

## API Endpoints

### 1. Initiate Payment
**Endpoint**: `POST /api/billing/payments/initiate/`

**Description**: Initiates a new payment transaction with ZenoPay for SMS package purchase.

**Request Body**:
```json
{
    "package_id": "uuid",
    "buyer_email": "user@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858"
}
```

**Response** (Success):
```json
{
    "success": true,
    "message": "Payment initiated successfully. Please complete payment on your mobile device.",
    "data": {
        "transaction_id": "uuid",
        "order_id": "MIFUMO-20241201-ABC12345",
        "zenopay_order_id": "uuid",
        "invoice_number": "INV-20241201-ABC12345",
        "amount": 1000.00,
        "credits": 100,
        "status": "pending",
        "payment_instructions": "Request in progress. You will receive a callback shortly",
        "progress": {
            "step": 1,
            "total_steps": 4,
            "current_step": "Payment Initiated",
            "next_step": "Complete Payment on Mobile",
            "completed_steps": ["Payment Initiated"],
            "remaining_steps": ["Complete Payment on Mobile", "Payment Verification", "Credits Added"],
            "percentage": 25,
            "status_color": "blue",
            "status_icon": "clock"
        }
    }
}
```

### 2. Check Payment Status
**Endpoint**: `GET /api/billing/payments/transactions/{transaction_id}/status/`

**Description**: Checks the current status of a payment transaction.

**Response**:
```json
{
    "success": true,
    "data": {
        "transaction_id": "uuid",
        "order_id": "MIFUMO-20241201-ABC12345",
        "status": "completed",
        "payment_status": "SUCCESS",
        "amount": 1000.00,
        "reference": "0936183435",
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

### 3. Get Payment Progress
**Endpoint**: `GET /api/billing/payments/transactions/{transaction_id}/progress/`

**Description**: Gets detailed progress information for user-friendly display.

**Response**:
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
            "package_name": "Starter Pack",
            "credits": 100,
            "unit_price": 10.00
        },
        "created_at": "2024-12-01T10:00:00Z",
        "updated_at": "2024-12-01T10:30:00Z",
        "completed_at": "2024-12-01T10:30:00Z"
    }
}
```

### 4. List Payment Transactions
**Endpoint**: `GET /api/billing/payments/transactions/`

**Description**: Lists all payment transactions for the authenticated tenant.

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `status`: Filter by status (pending, processing, completed, failed, cancelled)

**Response**:
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "order_id": "MIFUMO-20241201-ABC12345",
            "zenopay_order_id": "uuid",
            "invoice_number": "INV-20241201-ABC12345",
            "amount": 1000.00,
            "currency": "TZS",
            "buyer_email": "user@example.com",
            "buyer_name": "John Doe",
            "buyer_phone": "0744963858",
            "payment_method": "zenopay_mobile_money",
            "payment_method_display": "ZenoPay Mobile Money",
            "status": "completed",
            "status_display": "Completed",
            "zenopay_reference": "0936183435",
            "zenopay_transid": "CEJ3I3SETSN",
            "zenopay_channel": "MPESA-TZ",
            "zenopay_msisdn": "255744963858",
            "webhook_received": true,
            "created_at": "2024-12-01T10:00:00Z",
            "updated_at": "2024-12-01T10:30:00Z",
            "completed_at": "2024-12-01T10:30:00Z",
            "failed_at": null,
            "error_message": "",
            "purchase_data": {
                "id": "uuid",
                "package_name": "Starter Pack",
                "credits": 100,
                "unit_price": 10.00
            }
        }
    ]
}
```

### 5. Payment Webhook
**Endpoint**: `POST /api/billing/payments/webhook/`

**Description**: Handles webhook notifications from ZenoPay (internal use).

**Request Body** (from ZenoPay):
```json
{
    "order_id": "uuid",
    "payment_status": "COMPLETED",
    "reference": "0936183435",
    "metadata": {
        "product": "SMS Credits",
        "amount": "1000"
    }
}
```

## Payment Flow

### 1. Payment Initiation
1. User selects SMS package
2. User provides payment details (email, name, phone)
3. System creates payment transaction
4. System calls ZenoPay API to initiate payment
5. User receives payment instructions on mobile device

### 2. Payment Processing
1. User completes payment on mobile device
2. ZenoPay processes payment
3. System receives webhook notification
4. System updates transaction status
5. System adds SMS credits to tenant balance

### 3. Progress Tracking
The system provides real-time progress updates through 4 main stages:

1. **Payment Initiated** (25%)
   - Payment request created
   - ZenoPay order ID generated
   - User receives payment instructions

2. **Complete Payment on Mobile** (50%)
   - User completes payment on mobile device
   - Payment is being processed by ZenoPay

3. **Payment Verification** (75%)
   - Payment confirmed by ZenoPay
   - Transaction details updated

4. **Credits Added** (100%)
   - SMS credits added to tenant balance
   - Purchase completed successfully

## Progress Tracking

### Progress Object Structure
```json
{
    "step": 2,
    "total_steps": 4,
    "current_step": "Payment Processing",
    "next_step": "Payment Verification",
    "completed_steps": ["Payment Initiated", "Payment Processing"],
    "remaining_steps": ["Payment Verification", "Credits Added"],
    "percentage": 50,
    "status_color": "yellow",
    "status_icon": "sync"
}
```

### Status Colors and Icons
- **Blue**: Pending/In Progress (`clock`, `sync`)
- **Green**: Completed (`check`, `check-circle`)
- **Red**: Failed (`x`, `alert-circle`)
- **Yellow**: Processing (`sync`, `loading`)

## Webhook Integration

### Webhook URL
```
https://your-domain.com/api/billing/payments/webhook/
```

### Webhook Security
- Verify `x-api-key` header matches your ZenoPay API key
- Validate webhook payload structure
- Log all webhook requests for debugging

### Webhook Processing
1. Receive webhook notification
2. Validate webhook authenticity
3. Extract payment status and order ID
4. Update payment transaction status
5. Complete purchase if payment successful
6. Add SMS credits to tenant balance

## Error Handling

### Common Error Scenarios

#### 1. Invalid Phone Number
```json
{
    "success": false,
    "message": "Please provide a valid Tanzanian mobile number (e.g., 0744963858)"
}
```

#### 2. Payment Failed
```json
{
    "success": false,
    "message": "Payment failed",
    "error": "Insufficient funds in mobile wallet"
}
```

#### 3. Network Error
```json
{
    "success": false,
    "message": "Failed to initiate payment",
    "error": "Network error: Connection timeout"
}
```

### Error Recovery
- Automatic retry mechanisms for network errors
- Clear error messages for user action
- Fallback options for failed payments
- Support contact information

## Frontend Integration

### React/JavaScript Example

```javascript
// Initiate payment
const initiatePayment = async (packageId, buyerDetails) => {
    try {
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
        
        const data = await response.json();
        
        if (data.success) {
            // Show progress UI
            showPaymentProgress(data.data);
            
            // Start polling for status updates
            pollPaymentStatus(data.data.transaction_id);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Failed to initiate payment');
    }
};

// Poll payment status
const pollPaymentStatus = (transactionId) => {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/billing/payments/transactions/${transactionId}/status/`);
            const data = await response.json();
            
            if (data.success) {
                updateProgressUI(data.data.progress);
                
                if (data.data.status === 'completed' || data.data.status === 'failed') {
                    clearInterval(interval);
                }
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }, 5000); // Check every 5 seconds
};

// Progress UI component
const PaymentProgress = ({ progress }) => {
    return (
        <div className="payment-progress">
            <div className="progress-bar">
                <div 
                    className="progress-fill" 
                    style={{ width: `${progress.percentage}%` }}
                />
            </div>
            <div className="progress-steps">
                {progress.completed_steps.map((step, index) => (
                    <div key={index} className="step completed">
                        <i className={`icon ${progress.status_icon}`} />
                        {step}
                    </div>
                ))}
                <div className={`step current ${progress.status_color}`}>
                    <i className={`icon ${progress.status_icon}`} />
                    {progress.current_step}
                </div>
                {progress.remaining_steps.map((step, index) => (
                    <div key={index} className="step pending">
                        {step}
                    </div>
                ))}
            </div>
        </div>
    );
};
```

## Configuration

### Environment Variables
```bash
# ZenoPay Configuration
ZENOPAY_API_KEY=your_zenopay_api_key_here
ZENOPAY_API_TIMEOUT=30
ZENOPAY_WEBHOOK_SECRET=your_webhook_secret_here

# Base URL for webhooks
BASE_URL=https://your-domain.com
```

### Django Settings
```python
# ZenoPay Payment Gateway
ZENOPAY_API_KEY = config('ZENOPAY_API_KEY', default='')
ZENOPAY_API_TIMEOUT = config('ZENOPAY_API_TIMEOUT', default=30, cast=int)
ZENOPAY_WEBHOOK_SECRET = config('ZENOPAY_WEBHOOK_SECRET', default='')
```

## Testing

### Test Payment Flow
1. Use ZenoPay sandbox/test environment
2. Create test SMS packages
3. Test payment initiation
4. Simulate webhook notifications
5. Verify credit addition

### Test Data
```json
{
    "package_id": "test-package-uuid",
    "buyer_email": "test@example.com",
    "buyer_name": "Test User",
    "buyer_phone": "0744963858"
}
```

## Troubleshooting

### Common Issues

#### 1. Payment Not Initiated
- Check ZenoPay API key configuration
- Verify network connectivity
- Check request payload format

#### 2. Webhook Not Received
- Verify webhook URL is accessible
- Check webhook URL configuration
- Verify API key in webhook headers

#### 3. Credits Not Added
- Check webhook processing logs
- Verify transaction status
- Check tenant balance update logic

### Debug Logging
Enable debug logging to troubleshoot issues:

```python
LOGGING = {
    'loggers': {
        'billing.zenopay_service': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### Support Contacts
- **ZenoPay Support**: support@zenoapi.com
- **Mifumo Support**: support@mifumo.com
- **API Documentation**: https://zenoapi.com

## Security Considerations

1. **API Key Security**: Store ZenoPay API key securely
2. **Webhook Verification**: Always verify webhook authenticity
3. **HTTPS**: Use HTTPS for all webhook endpoints
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Input Validation**: Validate all input data
6. **Error Handling**: Don't expose sensitive information in errors

## Performance Optimization

1. **Async Processing**: Use async tasks for webhook processing
2. **Caching**: Cache frequently accessed data
3. **Database Indexing**: Index transaction lookup fields
4. **Connection Pooling**: Use connection pooling for API calls
5. **Monitoring**: Monitor API response times and error rates

## Monitoring and Analytics

### Key Metrics
- Payment success rate
- Average payment processing time
- Webhook delivery success rate
- Error rates by type
- User conversion rates

### Alerts
- High error rates
- Failed webhook deliveries
- Payment processing delays
- API timeout issues

---

This documentation provides a comprehensive guide for integrating and using the ZenoPay payment gateway in the Mifumo WMS billing system. For additional support or questions, please contact the development team.
