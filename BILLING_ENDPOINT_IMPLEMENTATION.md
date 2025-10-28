# Billing Endpoint Implementation

## Overview

A new billing information endpoint has been implemented to provide comprehensive billing data for the Settings page in the frontend application.

## Endpoint Details

### URL
```
GET /api/billing/info/
```

### Authentication
Requires JWT authentication. Include the bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Response Structure

The endpoint returns the following information:

### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "current_plan": {
      "id": "uuid",
      "name": "Professional",
      "price": 99.00,
      "currency": "TZS",
      "billing_cycle": "monthly",
      "plan_type": "professional",
      "max_messages": 10000,
      "status": "active",
      "is_active": true,
      "features": ["API Access", "Priority Support", "Advanced Analytics"],
      "current_period_start": "2024-03-01T00:00:00Z",
      "current_period_end": "2024-04-01T00:00:00Z"
    },
    "usage_this_month": {
      "messages_sent": 7245,
      "limit": 10000,
      "percentage_used": 72.45,
      "cost": 181125.00,
      "next_billing_date": "2024-04-01T00:00:00Z",
      "next_billing_amount": 99.00
    },
    "payment_method": {
      "type": "zenopay_mobile_money",
      "payment_method_display": "ZenoPay Mobile Money",
      "last_transaction_date": "2024-03-10T12:30:00Z",
      "last_transaction_amount": 50000.00
    },
    "sms_balance": {
      "credits": 2755,
      "total_purchased": 10000,
      "total_used": 7245,
      "last_updated": "2024-03-15T10:00:00Z"
    }
  }
}
```

## Response Fields Explained

### Current Plan
- **id**: Unique identifier for the plan
- **name**: Plan display name (e.g., "Professional", "Basic", "Enterprise")
- **price**: Monthly subscription price
- **currency**: Currency code (e.g., "TZS")
- **billing_cycle**: Subscription billing cycle ("monthly" or "yearly")
- **plan_type**: Type of plan ("professional", "basic", "enterprise", etc.)
- **max_messages**: Maximum messages allowed per month
- **status**: Subscription status ("active", "cancelled", "past_due", "suspended")
- **is_active**: Boolean indicating if subscription is currently active
- **features**: Array of plan features
- **current_period_start**: Start date of current billing period
- **current_period_end**: End date of current billing period (next billing date)

### Usage This Month
- **messages_sent**: Number of SMS messages sent in the current month
- **limit**: Total message limit for the current plan
- **percentage_used**: Percentage of limit used (0-100)
- **cost**: Total cost of messages sent this month
- **next_billing_date**: Next billing date (same as current_period_end from subscription)
- **next_billing_amount**: Amount to be charged on next billing date

### Payment Method
- **type**: Payment method type (e.g., "zenopay_mobile_money", "mpesa", "credit_card")
- **payment_method_display**: Human-readable payment method name
- **last_transaction_date**: Date of most recent completed payment
- **last_transaction_amount**: Amount of most recent transaction

### SMS Balance
- **credits**: Current SMS credit balance
- **total_purchased**: Total credits purchased since account creation
- **total_used**: Total credits used since account creation
- **last_updated**: Last time the balance was updated

## Prepaid Users

For users without a subscription (prepaid users), the response will show:

```json
{
  "current_plan": {
    "name": "Prepaid",
    "price": 0.00,
    "currency": "TZS",
    "billing_cycle": "prepaid",
    "plan_type": "prepaid",
    "max_messages": null,
    "status": "active",
    "is_active": true,
    "features": ["Pay as you go", "No monthly commitment"]
  },
  "usage_this_month": {
    "messages_sent": 150,
    "limit": null,
    "percentage_used": 0,
    "cost": 3750.00,
    "next_billing_date": null,
    "next_billing_amount": 0.00
  }
}
```

## Error Responses

### No Tenant Associated (400 Bad Request)
```json
{
  "success": false,
  "message": "User is not associated with any tenant. Please contact support."
}
```

### Server Error (500 Internal Server Error)
```json
{
  "success": false,
  "message": "Failed to retrieve billing information",
  "error": "Error details here"
}
```

## Frontend Integration

This endpoint is designed to be used with the Settings page billing section. Here's an example of how to fetch and use the data:

```javascript
// Fetch billing information
async function fetchBillingInfo() {
  try {
    const response = await fetch('/api/billing/info/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch billing info');
    }
    
    const data = await response.json();
    
    if (data.success) {
      const { current_plan, usage_this_month, payment_method, sms_balance } = data.data;
      
      // Update UI with billing data
      updateCurrentPlan(current_plan);
      updateUsageStats(usage_this_month);
      updatePaymentMethod(payment_method);
      updateSMSBalance(sms_balance);
    }
  } catch (error) {
    console.error('Error fetching billing info:', error);
  }
}
```

## Usage Statistics Calculation

The endpoint calculates monthly usage by:
1. Getting the start of the current month
2. Querying UsageRecord model for all records created after month_start
3. Summing up credits_used and cost
4. Calculating percentage based on plan's max_sms_per_month limit

## Testing

You can test this endpoint using:

```bash
# Using curl
curl -X GET "http://localhost:8000/api/billing/info/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json"

# Using Python requests
import requests

headers = {
    'Authorization': 'Bearer <your_token>',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/billing/info/', headers=headers)
print(response.json())
```

## Related Endpoints

- `/api/billing/overview/` - General billing overview
- `/api/billing/subscription/` - Subscription details
- `/api/billing/sms/balance/` - SMS credit balance
- `/api/billing/sms/usage/statistics/` - Detailed usage statistics
