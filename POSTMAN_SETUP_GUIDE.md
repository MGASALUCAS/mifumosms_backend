# Postman Setup Guide - Mifumo WMS SMS API

## 🚀 **Quick Setup**

### 1. **Import Collection and Environment**

1. **Download Files**:
   - `Mifumo_WMS_SMS_API.postman_collection.json` - API Collection
   - `Mifumo_WMS_Environment.postman_environment.json` - Environment Variables

2. **Import to Postman**:
   - Open Postman
   - Click "Import" button
   - Select both JSON files
   - Click "Import"

### 2. **Configure Environment**

1. **Select Environment**:
   - Click the environment dropdown (top right)
   - Select "Mifumo WMS - Development"

2. **Update Base URL**:
   - If your server runs on a different port, update `base_url` variable
   - Default: `http://localhost:8000`

## 🔐 **Authentication Setup**

### Step 1: Login
1. Go to **Authentication > Login**
2. Update the request body with your credentials:
   ```json
   {
       "username": "your-username",
       "password": "your-password"
   }
   ```
3. Click **Send**
4. Copy the `access_token` from response

### Step 2: Set Tokens
1. Go to **Environment Variables**
2. Set `access_token` to the token from login response
3. Set `refresh_token` to the refresh token from login response
4. Set `token_expires_at` to current time + 1 hour

## 📱 **SMS Testing Workflow**

### Step 1: Test Connection
1. Go to **SMS - Utilities > Test Beem Connection**
2. Click **Send**
3. Verify connection is successful

### Step 2: Register Sender ID
1. Go to **SMS - Sender IDs > Create Sender ID**
2. Update the request body:
   ```json
   {
       "sender_id": "YOURCOMPANY",
       "sample_content": "Hello from Your Company! This is a sample message.",
       "provider": "beem"
   }
   ```
3. Click **Send**
4. Copy the `id` from response to `sender_id_uuid` variable

### Step 3: Validate Phone Numbers
1. Go to **SMS - Utilities > Validate Phone Number**
2. Update phone number in request body
3. Click **Send**
4. Verify phone number is valid

### Step 4: Send Test SMS
1. Go to **SMS - Send Messages > Send Single SMS**
2. Update the request body:
   ```json
   {
       "message": "Hello from Mifumo WMS! This is a test message.",
       "recipients": ["255700000001"],
       "sender_id": "YOURCOMPANY"
   }
   ```
3. Click **Send**
4. Copy the `message_id` from response to `message_id` variable

### Step 5: Check Delivery Status
1. Go to **SMS - Management > Get SMS Delivery Status**
2. The `message_id` variable should be automatically used
3. Click **Send**
4. Check the delivery status

## 📋 **Collection Structure**

### **Authentication**
- **Login** - Get JWT access token
- **Refresh Token** - Refresh expired token

### **SMS - Send Messages**
- **Send Single SMS** - Send individual SMS
- **Send Bulk SMS** - Send multiple SMS messages
- **Send Scheduled SMS** - Schedule SMS for future delivery

### **SMS - Management**
- **Get SMS Messages** - List all SMS messages
- **Get SMS Delivery Status** - Check specific message status
- **Get Delivery Reports** - View delivery reports

### **SMS - Sender IDs**
- **Get Sender IDs** - List registered sender IDs
- **Create Sender ID** - Register new sender ID
- **Update Sender ID** - Modify sender ID status

### **SMS - Templates**
- **Get SMS Templates** - List SMS templates
- **Create SMS Template** - Create new template
- **Send SMS with Template** - Use template for SMS

### **SMS - Utilities**
- **Test Beem Connection** - Test API connectivity
- **Get Beem Balance** - Check account balance
- **Validate Phone Number** - Validate phone format
- **Get SMS Statistics** - View usage statistics

### **SMS - Error Examples**
- **Missing Sender ID** - Example error when sender_id is missing
- **Invalid Sender ID** - Example error when sender_id is not registered
- **Invalid Phone Number** - Example error for invalid phone format

## 🔧 **Environment Variables**

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `base_url` | API base URL | `http://localhost:8000` |
| `access_token` | JWT access token | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| `refresh_token` | JWT refresh token | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| `token_expires_at` | Token expiration time | `2024-01-01T12:00:00.000Z` |
| `message_id` | SMS message ID | `123e4567-e89b-12d3-a456-426614174000` |
| `sender_id_uuid` | Sender ID UUID | `123e4567-e89b-12d3-a456-426614174001` |
| `template_id` | Template ID | `123e4567-e89b-12d3-a456-426614174002` |
| `test_phone_1` | Test phone number 1 | `255700000001` |
| `test_phone_2` | Test phone number 2 | `255700000002` |
| `test_phone_3` | Test phone number 3 | `255700000003` |
| `sender_id_1` | Test sender ID 1 | `MIFUMO` |
| `sender_id_2` | Test sender ID 2 | `YOURCOMPANY` |

## 📝 **Request Examples**

### **Send Single SMS**
```json
{
    "message": "Hello from Mifumo WMS! This is a test message.",
    "recipients": ["255700000001", "255700000002"],
    "sender_id": "YOURCOMPANY",
    "encoding": 0
}
```

### **Send Bulk SMS**
```json
{
    "messages": [
        {
            "message": "Welcome to Mifumo WMS!",
            "recipients": ["255700000001"],
            "sender_id": "YOURCOMPANY"
        },
        {
            "message": "Your account is activated.",
            "recipients": ["255700000002"],
            "sender_id": "YOURCOMPANY"
        }
    ]
}
```

### **Send Scheduled SMS**
```json
{
    "message": "This is a scheduled message.",
    "recipients": ["255700000001"],
    "sender_id": "YOURCOMPANY",
    "schedule_time": "2024-12-25T10:00:00Z"
}
```

### **Create Sender ID**
```json
{
    "sender_id": "YOURCOMPANY",
    "sample_content": "Hello from Your Company! This is a sample message.",
    "provider": "beem"
}
```

### **Create SMS Template**
```json
{
    "name": "Welcome Message",
    "category": "TRANSACTIONAL",
    "language": "en",
    "message": "Welcome to Mifumo WMS, {{customer_name}}! Your account is now active.",
    "variables": ["customer_name"]
}
```

## 🚨 **Error Handling**

### **Common Error Responses**

#### **Missing Sender ID**
```json
{
    "success": false,
    "message": "Sender ID is required"
}
```

#### **Invalid Sender ID**
```json
{
    "success": false,
    "message": "Sender ID \"INVALID\" is not registered or not active"
}
```

#### **Invalid Phone Number**
```json
{
    "success": false,
    "message": "Validation error",
    "errors": {
        "recipients": [
            "Invalid phone numbers: invalid-phone"
        ]
    }
}
```

#### **Authentication Error**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## 🔄 **Auto Token Refresh**

The collection includes automatic token refresh functionality:

1. **Pre-request Script**: Automatically checks if token is expired
2. **Auto Refresh**: Refreshes token using refresh_token
3. **Seamless**: Updates environment variables automatically

## 📊 **Testing Checklist**

### **Basic Functionality**
- [ ] Login and get access token
- [ ] Test Beem connection
- [ ] Register sender ID
- [ ] Validate phone number
- [ ] Send single SMS
- [ ] Check delivery status

### **Advanced Features**
- [ ] Send bulk SMS
- [ ] Send scheduled SMS
- [ ] Create SMS template
- [ ] Send SMS with template
- [ ] Get SMS statistics
- [ ] Handle error scenarios

### **Error Scenarios**
- [ ] Test missing sender ID
- [ ] Test invalid sender ID
- [ ] Test invalid phone number
- [ ] Test expired token
- [ ] Test invalid authentication

## 🎯 **Best Practices**

1. **Always test connection first**
2. **Register sender IDs before sending SMS**
3. **Validate phone numbers before sending**
4. **Use environment variables for dynamic data**
5. **Test error scenarios**
6. **Monitor delivery status**
7. **Keep tokens secure**

## 🆘 **Troubleshooting**

### **Connection Issues**
- Check if server is running
- Verify base_url is correct
- Check network connectivity

### **Authentication Issues**
- Verify credentials are correct
- Check if tokens are expired
- Ensure JWT is properly formatted

### **SMS Issues**
- Verify sender ID is registered and active
- Check phone number format
- Ensure Beem API credentials are configured
- Check account balance

### **Error Messages**
- Read error responses carefully
- Check validation errors
- Verify required fields are provided

## 📞 **Support**

For technical support:
- **Email**: support@mifumo.com
- **Documentation**: Check API documentation
- **Issues**: Report bugs via GitHub

---

**Happy Testing! 🚀**
