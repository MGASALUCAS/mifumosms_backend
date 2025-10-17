# Postman Payment System Testing Guide

## Overview
This guide will help you test the complete payment system using Postman, including mobile money integration and SMS credit purchasing.

## Prerequisites
1. **Postman installed** on your computer
2. **Django server running** on `http://127.0.0.1:8000`
3. **ZenoPay API configured** (for real payments)
4. **SMS packages created** in the database

## Setup Instructions

### 1. Import Collection and Environment
1. Open Postman
2. Click **Import** button
3. Import `Mifumo_Payment_System_Postman_Collection.json`
4. Import `Mifumo_Payment_System_Environment.json`
5. Select the **Mifumo Payment System Environment** from the environment dropdown

### 2. Environment Variables
The environment includes these variables:
- `base_url`: `http://127.0.0.1:8000`
- `jwt_token`: (will be set automatically after login)
- `refresh_token`: (will be set automatically after login)
- `package_id`: (will be set after getting packages)
- `transaction_id`: (will be set after initiating payment)
- `user_email`: `admin@mifumo.com`
- `user_password`: `admin123`
- `test_phone`: `0744963858`

## Testing Flow

### Step 1: Authentication
1. **Login - Get JWT Token**
   - Method: `POST`
   - URL: `{{base_url}}/api/auth/token/`
   - Body: 
     ```json
     {
       "email": "admin@mifumo.com",
       "password": "admin123"
     }
     ```
   - **Expected Response**: 200 OK with JWT tokens
   - **Action**: Copy the `access` token to the `jwt_token` environment variable

### Step 2: Get SMS Packages
1. **Get All SMS Packages**
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/sms/packages/`
   - Headers: `Authorization: Bearer {{jwt_token}}`
   - **Expected Response**: 200 OK with list of packages
   - **Action**: Copy a package ID to the `package_id` environment variable

### Step 3: Get Mobile Money Providers
1. **Get Mobile Money Providers**
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/providers/`
   - **Expected Response**: 200 OK with available providers
   - **Note**: This endpoint doesn't require authentication

### Step 4: Initiate Payment
1. **Initiate Payment - Lite Package**
   - Method: `POST`
   - URL: `{{base_url}}/api/billing/payments/initiate/`
   - Headers: `Authorization: Bearer {{jwt_token}}`
   - Body:
     ```json
     {
       "package_id": "{{package_id}}",
       "buyer_email": "admin@mifumo.com",
       "buyer_name": "Admin User",
       "buyer_phone": "0744963858",
       "mobile_money_provider": "vodacom"
     }
     ```
   - **Expected Response**: 201 Created with payment details
   - **Action**: Copy the `transaction_id` from response to environment variable

### Step 5: Check Payment Status
1. **Get Payment Status**
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/payments/transactions/{{transaction_id}}/status/`
   - Headers: `Authorization: Bearer {{jwt_token}}`
   - **Expected Response**: 200 OK with payment status

### Step 6: Check SMS Balance
1. **Get SMS Balance**
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/sms/balance/`
   - Headers: `Authorization: Bearer {{jwt_token}}`
   - **Expected Response**: 200 OK with current balance

### Step 7: Simulate Payment Completion (Webhook)
1. **Simulate ZenoPay Webhook - Success**
   - Method: `POST`
   - URL: `{{base_url}}/api/billing/payments/webhook/`
   - Body:
     ```json
     {
       "order_id": "{{transaction_id}}",
       "payment_status": "COMPLETED",
       "reference": "REF123456789",
       "transid": "TXN123456789",
       "channel": "MPESA-TZ",
       "msisdn": "255744963858"
     }
     ```
   - **Expected Response**: 200 OK
   - **Note**: This simulates ZenoPay sending a webhook when payment is completed

### Step 8: Verify SMS Credits Added
1. **Get SMS Balance** (again)
   - Method: `GET`
   - URL: `{{base_url}}/api/billing/sms/balance/`
   - Headers: `Authorization: Bearer {{jwt_token}}`
   - **Expected Response**: 200 OK with updated balance (should show credits added)

## Testing Different Scenarios

### Test 1: Vodacom M-Pesa Payment
- Use `"mobile_money_provider": "vodacom"`
- This should trigger M-Pesa push notification

### Test 2: Tigo Pesa Payment
- Use `"mobile_money_provider": "tigo"`
- This should trigger Tigo Pesa push notification

### Test 3: Airtel Money Payment
- Use `"mobile_money_provider": "airtel"`
- This should trigger Airtel Money push notification

### Test 4: Halotel Payment
- Use `"mobile_money_provider": "halotel"`
- This should trigger Halotel push notification

## Expected Responses

### Successful Payment Initiation
```json
{
  "success": true,
  "message": "Payment initiated successfully. Please complete payment on your mobile device.",
  "data": {
    "transaction_id": "uuid",
    "order_id": "MIFUMO-20241017-ABC12345",
    "amount": 150000.00,
    "currency": "TZS",
    "mobile_money_provider": "vodacom",
    "provider_name": "Vodacom",
    "credits": 5000,
    "package": {
      "name": "Lite",
      "credits": 5000,
      "price": 150000.00
    }
  }
}
```

### Mobile Money Providers
```json
{
  "success": true,
  "data": [
    {
      "code": "vodacom",
      "name": "Vodacom M-Pesa",
      "description": "Pay with M-Pesa via Vodacom",
      "icon": "vodacom-icon",
      "popular": true,
      "min_amount": 1000,
      "max_amount": 1000000
    }
  ]
}
```

### SMS Balance
```json
{
  "success": true,
  "data": {
    "credits": 50000,
    "tenant": "Mifumo WMS Default",
    "last_updated": "2024-10-17T14:30:00Z"
  }
}
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check if JWT token is valid
   - Try refreshing the token
   - Re-login if necessary

2. **404 Not Found**
   - Check if the endpoint URL is correct
   - Verify the server is running
   - Check if the package/transaction ID exists

3. **400 Bad Request**
   - Check the request body format
   - Verify all required fields are provided
   - Check if the package ID is valid

4. **500 Internal Server Error**
   - Check server logs
   - Verify ZenoPay configuration
   - Check database connectivity

### Debug Steps

1. **Check Server Logs**
   - Look at the Django server console for error messages
   - Check for any exceptions or warnings

2. **Verify Environment Variables**
   - Make sure all environment variables are set correctly
   - Check if the JWT token is not expired

3. **Test Individual Endpoints**
   - Test each endpoint separately
   - Verify authentication works
   - Check if packages are available

## Real Payment Testing

### For Real Payments (with ZenoPay)
1. Make sure ZenoPay API key is configured
2. Use a real phone number
3. Complete the payment on your mobile device
4. Wait for the webhook to be called automatically

### For Testing (without ZenoPay)
1. Use the webhook simulation endpoints
2. Manually trigger payment completion
3. Verify SMS credits are added

## Next Steps

After successful testing:
1. **Frontend Integration**: Use these endpoints in your frontend application
2. **Production Setup**: Configure ZenoPay for production
3. **Monitoring**: Set up logging and monitoring for payment flows
4. **Error Handling**: Implement proper error handling in your application

## Support

If you encounter any issues:
1. Check the server logs
2. Verify the API documentation
3. Test with curl commands
4. Check the database for data consistency
