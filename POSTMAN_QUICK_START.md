# Postman Quick Start Guide

## 🚀 Quick Setup for Payment Testing

### 1. Import Files
1. Import `Mifumo_Payment_System_Postman_Collection.json`
2. Import `Mifumo_Payment_System_Environment.json`
3. Select the "Mifumo Payment System Environment"

### 2. Fixed Configuration
The user-tenant association has been fixed. Use these values:

**Environment Variables:**
- `base_url`: `http://127.0.0.1:8000`
- `user_email`: `admin@example.com`
- `user_password`: `admin123` (or whatever you set)
- `package_id`: `b4f12412-d0ae-4ece-b245-10aac43d73be` (Lite package)
- `test_phone`: `0757347863`

### 3. Testing Steps

#### Step 1: Login
- **Request**: `Login - Get JWT Token`
- **Method**: `POST`
- **URL**: `{{base_url}}/api/auth/login/`
- **Body**:
  ```json
  {
    "email": "admin@example.com",
    "password": "admin123"
  }
  ```
- **Expected**: 200 OK with JWT tokens
- **Action**: Copy the `access` token to `{{jwt_token}}` variable

#### Step 2: Get SMS Packages
- **Request**: `Get All SMS Packages`
- **Method**: `GET`
- **URL**: `{{base_url}}/api/billing/sms/packages/`
- **Headers**: `Authorization: Bearer {{jwt_token}}`
- **Expected**: 200 OK with packages list

#### Step 3: Get Mobile Money Providers
- **Request**: `Get Mobile Money Providers`
- **Method**: `GET`
- **URL**: `{{base_url}}/api/billing/payments/providers/`
- **Expected**: 200 OK with providers list

#### Step 4: Initiate Payment
- **Request**: `Initiate Payment - Lite Package`
- **Method**: `POST`
- **URL**: `{{base_url}}/api/billing/payments/initiate/`
- **Headers**: `Authorization: Bearer {{jwt_token}}`
- **Body**:
  ```json
  {
    "package_id": "b4f12412-d0ae-4ece-b245-10aac43d73be",
    "buyer_email": "admin@example.com",
    "buyer_name": "Admin User",
    "buyer_phone": "0757347863",
    "mobile_money_provider": "vodacom"
  }
  ```
- **Expected**: 201 Created with payment details
- **Action**: Copy `transaction_id` from response

#### Step 5: Check Payment Status
- **Request**: `Get Payment Status`
- **Method**: `GET`
- **URL**: `{{base_url}}/api/billing/payments/transactions/{{transaction_id}}/status/`
- **Headers**: `Authorization: Bearer {{jwt_token}}`
- **Expected**: 200 OK with status

#### Step 6: Check SMS Balance
- **Request**: `Get SMS Balance`
- **Method**: `GET`
- **URL**: `{{base_url}}/api/billing/sms/balance/`
- **Headers**: `Authorization: Bearer {{jwt_token}}`
- **Expected**: 200 OK with current balance

### 4. Expected Responses

#### Successful Login
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Successful Payment Initiation
```json
{
  "success": true,
  "message": "Payment initiated successfully. Please complete payment on your mobile device.",
  "data": {
    "transaction_id": "uuid-here",
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

### 5. Troubleshooting

#### If you get "User is not associated with any tenant":
- The user-tenant association has been fixed
- Make sure you're using `admin@example.com`
- The user is now associated with the "Mifumo WMS Default" tenant

#### If you get 401 Unauthorized:
- Check if the JWT token is valid
- Try refreshing the token
- Re-login if necessary

#### If you get 404 Not Found:
- Check if the server is running on `http://127.0.0.1:8000`
- Verify the endpoint URLs are correct

### 6. Package IDs for Testing

- **Lite**: `b4f12412-d0ae-4ece-b245-10aac43d73be` (5,000 credits - 150,000 TZS)
- **Standard**: `39551dd1-37de-452d-ad49-d0edb7cdf45a` (50,000 credits - 1,250,000 TZS)
- **Pro**: `8d0fbe04-5e80-4fe2-a7b8-f8551ad0de9e` (250,000 credits - 4,500,000 TZS)
- **Enterprise**: `620cab41-0dc5-4482-8167-35c9a11d4f67` (1,000,000 credits - 12,000,000 TZS)

### 7. Mobile Money Providers

- **vodacom**: Vodacom M-Pesa
- **tigo**: Tigo Pesa
- **airtel**: Airtel Money
- **halotel**: Halotel

### 8. Next Steps

After successful testing:
1. **Real Payment**: Use a real phone number to test actual mobile money payments
2. **Webhook Testing**: Use the webhook simulation to test payment completion
3. **Frontend Integration**: Use these endpoints in your frontend application

## 🎯 Success!

If all steps work correctly, you should see:
- ✅ Successful login with JWT token
- ✅ SMS packages listed
- ✅ Mobile money providers listed
- ✅ Payment initiated successfully
- ✅ Payment status checked
- ✅ SMS balance retrieved

The payment system is now ready for production use! 🚀
