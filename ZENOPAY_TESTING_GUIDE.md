# ZenoPay Payment Gateway Testing Guide

## Overview

This guide provides step-by-step instructions for testing the ZenoPay Mobile Money Tanzania integration using Postman. The integration includes user-friendly progress tracking and real-time payment status updates.

## Prerequisites

1. **Django Server Running**: Ensure your Django development server is running on `http://localhost:8000`
2. **Database Migrations**: Run migrations to create the new payment models
3. **ZenoPay API Key**: Obtain a test API key from ZenoPay
4. **Postman Installed**: Download and install Postman for API testing

## Setup Instructions

### 1. Database Setup

```bash
# Navigate to your Django project directory
cd e:\github\mifumosms_backend

# Create and run migrations for the new models
python manage.py makemigrations billing
python manage.py migrate

# Create a superuser if you haven't already
python manage.py createsuperuser
```

### 2. Environment Configuration

Create a `.env` file in your project root with the following variables:

```env
# ZenoPay Configuration
ZENOPAY_API_KEY=your_test_api_key_here
ZENOPAY_API_TIMEOUT=30
ZENOPAY_WEBHOOK_SECRET=your_webhook_secret_here

# Base URL for webhooks
BASE_URL=http://localhost:8000
```

### 3. Postman Setup

1. **Import Collection**: Import `ZenoPay_Payment_API.postman_collection.json`
2. **Import Environment**: Import `ZenoPay_Payment_Environment.postman_environment.json`
3. **Select Environment**: Make sure the "ZenoPay Payment Environment" is selected

## Testing Workflow

### Step 1: Authentication

1. **Login Request**:
   - Method: `POST`
   - URL: `{{base_url}}/api/auth/login/`
   - Body: 
     ```json
     {
         "email": "your_email@example.com",
         "password": "your_password"
     }
     ```

2. **Expected Response**:
   ```json
   {
       "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
       "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   }
   ```

3. **Auto-Configuration**: The JWT token will be automatically set in the environment variables.

### Step 2: Get SMS Packages

1. **Get Packages Request**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/sms/packages/`
   - Headers: `Authorization: Bearer {{jwt_token}}`

2. **Expected Response**:
   ```json
   [
       {
           "id": "123e4567-e89b-12d3-a456-426614174000",
           "name": "Starter Pack",
           "package_type": "lite",
           "credits": 100,
           "price": "1000.00",
           "unit_price": "10.00",
           "is_popular": true,
           "features": ["100 SMS Credits", "Email Support"],
           "savings_percentage": 66.7
       }
   ]
   ```

3. **Auto-Configuration**: The first package ID will be automatically set in the environment variables.

### Step 3: Check Current Balance

1. **Get Balance Request**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/sms/balance/`
   - Headers: `Authorization: Bearer {{jwt_token}}`

2. **Expected Response**:
   ```json
   {
       "id": "123e4567-e89b-12d3-a456-426614174000",
       "credits": 0,
       "total_purchased": 0,
       "total_used": 0,
       "last_updated": "2024-12-01T10:00:00Z",
       "created_at": "2024-12-01T10:00:00Z"
   }
   ```

### Step 4: Initiate Payment

1. **Initiate Payment Request**:
   - Method: `POST`
   - URL: `{{base_url}}/api/billing/payments/initiate/`
   - Headers: 
     - `Content-Type: application/json`
     - `Authorization: Bearer {{jwt_token}}`
   - Body:
     ```json
     {
         "package_id": "{{package_id}}",
         "buyer_email": "{{buyer_email}}",
         "buyer_name": "{{buyer_name}}",
         "buyer_phone": "{{buyer_phone}}"
     }
     ```

2. **Expected Response**:
   ```json
   {
       "success": true,
       "message": "Payment initiated successfully. Please complete payment on your mobile device.",
       "data": {
           "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
           "order_id": "MIFUMO-20241201-ABC12345",
           "zenopay_order_id": "3rer407fe-3ee8-4525-456f-ccb95de38250",
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

3. **Auto-Configuration**: The transaction ID will be automatically set in the environment variables.

### Step 5: Check Payment Status

1. **Check Status Request**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/transactions/{{transaction_id}}/status/`
   - Headers: `Authorization: Bearer {{jwt_token}}`

2. **Expected Response** (Pending):
   ```json
   {
       "success": true,
       "data": {
           "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
           "order_id": "MIFUMO-20241201-ABC12345",
           "status": "pending",
           "payment_status": "PENDING",
           "amount": 1000.00,
           "reference": "",
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
           },
           "updated_at": "2024-12-01T10:00:00Z"
       }
   }
   ```

### Step 6: Simulate Payment Completion (Webhook)

1. **Webhook Request**:
   - Method: `POST`
   - URL: `{{base_url}}/api/billing/payments/webhook/`
   - Headers:
     - `Content-Type: application/json`
     - `x-api-key: {{zenopay_api_key}}`
   - Body:
     ```json
     {
         "order_id": "3rer407fe-3ee8-4525-456f-ccb95de38250",
         "payment_status": "COMPLETED",
         "reference": "0936183435",
         "metadata": {
             "product": "SMS Credits",
             "amount": "1000"
         }
     }
     ```

2. **Expected Response**:
   ```json
   {
       "success": true,
       "message": "Webhook processed successfully"
   }
   ```

### Step 7: Verify Payment Completion

1. **Check Status Again**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/transactions/{{transaction_id}}/status/`

2. **Expected Response** (Completed):
   ```json
   {
       "success": true,
       "data": {
           "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
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

### Step 8: Verify Credits Added

1. **Check Balance Again**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/sms/balance/`

2. **Expected Response**:
   ```json
   {
       "id": "123e4567-e89b-12d3-a456-426614174000",
       "credits": 100,
       "total_purchased": 100,
       "total_used": 0,
       "last_updated": "2024-12-01T10:30:00Z",
       "created_at": "2024-12-01T10:00:00Z"
   }
   ```

## Advanced Testing Scenarios

### 1. Test Payment Progress Tracking

Use the **Get Payment Progress** endpoint to test the detailed progress tracking:

- Method: `GET`
- URL: `{{base_url}}/api/billing/payments/transactions/{{transaction_id}}/progress/`

This endpoint provides comprehensive progress information including:
- Step-by-step progress
- Visual indicators (colors, icons)
- Completion percentage
- Purchase details

### 2. Test Error Scenarios

#### Invalid Phone Number
```json
{
    "package_id": "{{package_id}}",
    "buyer_email": "test@example.com",
    "buyer_name": "Test User",
    "buyer_phone": "123456789"  // Invalid format
}
```

Expected Error:
```json
{
    "success": false,
    "message": "Please provide a valid Tanzanian mobile number (e.g., 0744963858)"
}
```

#### Invalid Package ID
```json
{
    "package_id": "invalid-uuid",
    "buyer_email": "test@example.com",
    "buyer_name": "Test User",
    "buyer_phone": "0744963858"
}
```

Expected Error:
```json
{
    "success": false,
    "message": "Invalid or inactive package"
}
```

### 3. Test Payment Failure

Simulate a failed payment by sending a webhook with failed status:

```json
{
    "order_id": "3rer407fe-3ee8-4525-456f-ccb95de38250",
    "payment_status": "FAILED",
    "reference": "0936183435",
    "metadata": {
        "error": "Insufficient funds"
    }
}
```

### 4. Test Transaction History

1. **List All Transactions**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/transactions/`

2. **Filter by Status**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/transactions/?status=completed`

3. **Pagination**:
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/transactions/?page=1&page_size=10`

## Monitoring and Debugging

### 1. Check Django Logs

Monitor the Django console for logs:
```bash
python manage.py runserver
```

Look for:
- ZenoPay API requests and responses
- Webhook processing logs
- Error messages
- Transaction updates

### 2. Database Verification

Check the database to verify data:

```sql
-- Check payment transactions
SELECT * FROM payment_transactions ORDER BY created_at DESC;

-- Check purchases
SELECT * FROM sms_purchases ORDER BY created_at DESC;

-- Check SMS balances
SELECT * FROM sms_balances;
```

### 3. API Response Validation

Verify that all API responses include:
- Proper HTTP status codes
- Consistent response format
- Progress tracking data
- Error handling

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify JWT token is valid
   - Check token expiration
   - Ensure proper Authorization header format

2. **ZenoPay API Errors**:
   - Verify API key is correct
   - Check network connectivity
   - Validate request payload format

3. **Webhook Issues**:
   - Ensure webhook URL is accessible
   - Check x-api-key header
   - Verify JSON payload format

4. **Database Issues**:
   - Run migrations
   - Check database connectivity
   - Verify model relationships

### Debug Mode

Enable debug logging in Django settings:

```python
LOGGING = {
    'loggers': {
        'billing.zenopay_service': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'billing.views_payment': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Success Criteria

A successful test should demonstrate:

1. ✅ Payment initiation creates transaction record
2. ✅ ZenoPay API integration works
3. ✅ Progress tracking updates correctly
4. ✅ Webhook processing updates transaction status
5. ✅ SMS credits are added to tenant balance
6. ✅ Error handling works for invalid inputs
7. ✅ Transaction history is properly maintained
8. ✅ API responses are consistent and user-friendly

## Next Steps

After successful testing:

1. **Production Setup**: Configure production ZenoPay API key
2. **Webhook Security**: Implement proper webhook verification
3. **Monitoring**: Set up logging and monitoring
4. **Frontend Integration**: Implement frontend progress tracking
5. **Documentation**: Update API documentation
6. **Testing**: Set up automated tests

---

This testing guide provides comprehensive instructions for validating the ZenoPay payment gateway integration. Follow the steps carefully and verify each response to ensure the integration works correctly.
