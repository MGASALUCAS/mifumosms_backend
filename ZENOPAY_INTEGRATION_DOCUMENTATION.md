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
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
}
```

**Request Parameters**:
- `package_id` (required): UUID of the SMS package to purchase
- `buyer_email` (required): Customer email address
- `buyer_name` (required): Customer full name
- `buyer_phone` (required): Customer phone number in Tanzanian format
- `mobile_money_provider` (optional): Mobile money provider (default: "vodacom")
  - Valid options: `vodacom`, `halotel`, `tigo`, `airtel`

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
        "mobile_money_provider": "vodacom",
        "mobile_money_provider_display": "Vodacom M-Pesa",
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

```bash
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

### Simple JavaScript Integration

#### 1. Initiate Payment

```javascript
// POST /api/billing/payments/initiate/
const response = await fetch('/api/billing/payments/initiate/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        package_id: 'package-uuid',
        buyer_name: 'John Doe',
        buyer_email: 'john@example.com',
        buyer_phone: '0744963858',
        mobile_money_provider: 'vodacom'
    })
});

const data = await response.json();
console.log(data);
```

**Response:**
```json
{
    "success": true,
    "message": "Payment initiated successfully. Please complete payment on your mobile device.",
    "data": {
        "transaction_id": "uuid",
        "order_id": "MIFUMO-20241201-ABC12345",
        "amount": 1000.00,
        "status": "pending",
        "progress": {
            "step": 1,
            "total_steps": 4,
            "current_step": "Payment Initiated",
            "percentage": 25,
            "status_color": "blue"
        }
    }
}
```

#### 2. Check Payment Status

```javascript
// GET /api/billing/payments/transactions/{transaction_id}/status/
const checkStatus = async (transactionId) => {
    const response = await fetch(`/api/billing/payments/transactions/${transactionId}/status/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    return data;
};

// Poll every 5 seconds
const pollPayment = (transactionId) => {
    const interval = setInterval(async () => {
        const data = await checkStatus(transactionId);
        
        if (data.success) {
            updateProgressUI(data.data.progress);
            
            if (data.data.status === 'completed' || data.data.status === 'failed') {
                clearInterval(interval);
            }
        }
    }, 5000);
};
```

**Response:**
```json
{
    "success": true,
    "data": {
        "transaction_id": "uuid",
        "status": "completed",
        "payment_status": "SUCCESS",
        "amount": 1000.00,
        "progress": {
            "step": 4,
            "total_steps": 4,
            "current_step": "Payment Completed",
            "percentage": 100,
            "status_color": "green"
        }
    }
}
```

#### 3. Complete Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>ZenoPay Payment</title>
</head>
<body>
    <form id="paymentForm">
        <input type="text" id="buyerName" placeholder="Full Name" required>
        <input type="email" id="buyerEmail" placeholder="Email" required>
        <input type="tel" id="buyerPhone" placeholder="0744963858" required>
        <select id="mobileProvider">
            <option value="vodacom">Vodacom M-Pesa</option>
            <option value="halotel">Halotel</option>
            <option value="tigo">Tigo Pesa</option>
            <option value="airtel">Airtel Money</option>
        </select>
        <button type="submit">Pay with Mobile Money</button>
    </form>
    
    <div id="progress" style="display:none;">
        <div id="progressBar" style="width: 0%; height: 20px; background: blue;"></div>
        <div id="statusText">Processing...</div>
    </div>

    <script>
        const token = 'your-auth-token';
        let currentTransactionId = null;

        document.getElementById('paymentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                package_id: 'your-package-id',
                buyer_name: document.getElementById('buyerName').value,
                buyer_email: document.getElementById('buyerEmail').value,
                buyer_phone: document.getElementById('buyerPhone').value,
                mobile_money_provider: document.getElementById('mobileProvider').value || 'vodacom'
            };

            try {
                const response = await fetch('/api/billing/payments/initiate/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                
                if (data.success) {
                    currentTransactionId = data.data.transaction_id;
                    showProgress(data.data.progress);
                    startPolling();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                alert('Payment failed. Please try again.');
            }
        });

        function showProgress(progress) {
            document.getElementById('progress').style.display = 'block';
            updateProgress(progress);
        }

        function updateProgress(progress) {
            document.getElementById('progressBar').style.width = progress.percentage + '%';
            document.getElementById('statusText').textContent = progress.current_step;
        }

        function startPolling() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/billing/payments/transactions/${currentTransactionId}/status/`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        updateProgress(data.data.progress);
                        
                        if (data.data.status === 'completed') {
                            clearInterval(interval);
                            alert('Payment completed successfully!');
                        } else if (data.data.status === 'failed') {
                            clearInterval(interval);
                            alert('Payment failed. Please try again.');
                        }
                    }
                } catch (error) {
                    console.error('Status check failed:', error);
                }
            }, 5000);
        }
    </script>
</body>
</html>
```

### React Integration

```jsx
import React, { useState } from 'react';

const ZenoPayPayment = ({ authToken }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState(null);
    const [transactionId, setTransactionId] = useState(null);

    const initiatePayment = async (formData) => {
        setIsLoading(true);
        
        try {
            const response = await fetch('/api/billing/payments/initiate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                setTransactionId(data.data.transaction_id);
                setProgress(data.data.progress);
                startPolling(data.data.transaction_id);
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('Payment failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const startPolling = (txId) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/api/billing/payments/transactions/${txId}/status/`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    setProgress(data.data.progress);
                    
                    if (data.data.status === 'completed' || data.data.status === 'failed') {
                        clearInterval(interval);
                    }
                }
            } catch (error) {
                console.error('Status check failed:', error);
            }
        }, 5000);
    };

    return (
        <div>
            {!progress ? (
                <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    initiatePayment({
                        package_id: 'your-package-id',
                        buyer_name: formData.get('name'),
                        buyer_email: formData.get('email'),
                        buyer_phone: formData.get('phone'),
                        mobile_money_provider: formData.get('mobile_provider') || 'vodacom'
                    });
                }}>
                    <input name="name" placeholder="Full Name" required />
                    <input name="email" type="email" placeholder="Email" required />
                    <input name="phone" type="tel" placeholder="0744963858" required />
                    <select name="mobile_provider" defaultValue="vodacom">
                        <option value="vodacom">Vodacom M-Pesa</option>
                        <option value="halotel">Halotel</option>
                        <option value="tigo">Tigo Pesa</option>
                        <option value="airtel">Airtel Money</option>
                    </select>
                    <button type="submit" disabled={isLoading}>
                        {isLoading ? 'Processing...' : 'Pay with Mobile Money'}
                    </button>
                </form>
            ) : (
                <div>
                    <div style={{ width: '100%', height: '20px', background: '#eee' }}>
                        <div style={{ 
                            width: `${progress.percentage}%`, 
                            height: '100%', 
                            background: 'blue' 
                        }} />
                    </div>
                    <p>{progress.current_step}</p>
                </div>
            )}
        </div>
    );
};

export default ZenoPayPayment;
```

### Key Points

1. **Authentication**: Include `Authorization: Bearer ${token}` header
2. **Phone Format**: Use Tanzanian format (07XXXXXXXX or 2557XXXXXXXX)
3. **Mobile Money Provider**: Choose from vodacom, halotel, tigo, airtel (default: vodacom)
4. **Polling**: Check status every 5 seconds until completed/failed
5. **Progress**: Show visual progress bar and current step
6. **Error Handling**: Display user-friendly error messages
7. **Package ID**: Must be a valid UUID from available packages

### Error Handling

#### Common Error Responses

**Invalid Package ID:**
```json
{
    "success": false,
    "message": "Invalid package ID format: custom. Please select a valid package."
}
```

**Package Not Found:**
```json
{
    "success": false,
    "message": "Package not found or inactive. Please select a valid package."
}
```

**Missing Fields:**
```json
{
    "success": false,
    "message": "Missing required fields: package_id, buyer_email, buyer_name, buyer_phone"
}
```

**Invalid Mobile Money Provider:**
```json
{
    "success": false,
    "message": "Invalid mobile money provider. Choose from: vodacom, halotel, tigo, airtel"
}
```

#### Getting Available Packages

```javascript
// GET /api/billing/sms/packages/
const response = await fetch('/api/billing/sms/packages/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const data = await response.json();
console.log('Available packages:', data.results);
```

**Response:**
```json
{
    "count": 4,
    "results": [
        {
            "id": "3e0d5e81-e373-4248-846c-44b90f38c3ba",
            "name": "Lite",
            "package_type": "lite",
            "credits": 5000,
            "price": "150000.00",
            "unit_price": "30.00",
            "is_popular": false,
            "is_active": true
        }
    ]
}
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
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
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

- **ZenoPay Support**: [support@zenoapi.com](mailto:support@zenoapi.com)
- **Mifumo Support**: [support@mifumo.com](mailto:support@mifumo.com)
- **API Documentation**: [https://zenoapi.com](https://zenoapi.com)

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
