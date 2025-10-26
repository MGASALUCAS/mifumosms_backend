# Mifumo SMS API Documentation Index

Welcome to the comprehensive Mifumo SMS API documentation. This guide provides everything you need to integrate SMS functionality into your applications.

## 📚 Documentation Overview

### For External Developers (API Integration)
These documents are for developers who want to integrate the Mifumo SMS API into their applications:

| Document | Purpose | Audience |
|----------|---------|----------|
| **[API Integration Guide](API_INTEGRATION_GUIDE.md)** | Complete API reference with examples | External developers |
| **[API Quick Reference Card](API_QUICK_REFERENCE_CARD.md)** | Quick reference for endpoints and codes | Developers |
| **[API Testing Guide](API_TESTING_GUIDE.md)** | Step-by-step testing instructions | Developers |
| **[Webhook Integration Guide](WEBHOOK_INTEGRATION_GUIDE.md)** | Real-time notifications setup | Developers |

### For Internal Users (Settings Management)
These documents are for users managing their API keys and webhooks through the dashboard:

| Document | Purpose | Audience |
|----------|---------|----------|
| **[API Endpoints Reference](API_ENDPOINTS_REFERENCE.md)** | Settings page API endpoints | Frontend developers |
| **[Frontend Settings Integration Guide](FRONTEND_SETTINGS_INTEGRATION_GUIDE.md)** | Complete frontend integration | Frontend developers |

---

## 🚀 Quick Start

### 1. Get Your API Key
1. Register at [Mifumo SMS Dashboard](https://mifumosms.servehttp.com)
2. Go to Settings → API & Webhooks
3. Create a new API key
4. Copy your API key and secret

### 2. Send Your First SMS
```bash
curl -X POST "https://mifumosms.servehttp.com/api/integration/v1/sms/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "message": "Hello from Mifumo SMS!",
    "recipients": ["+255123456789"],
    "sender_id": "Taarifa-SMS"
  }'
```

### 3. Check Message Status
```bash
curl -X GET "https://mifumosms.servehttp.com/api/integration/v1/sms/status/MESSAGE_ID/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🔗 API Endpoints Summary

### SMS API (External Integration)
**Base URL:** `https://mifumosms.servehttp.com/api/integration/v1/`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/sms/send/` | Send SMS messages |
| `GET` | `/sms/status/{message_id}/` | Get message status |
| `GET` | `/sms/delivery-reports/` | Get delivery reports |
| `GET` | `/sms/balance/` | Get account balance |

### Settings API (User Management)
**Base URL:** `http://127.0.0.1:8001/api/auth/`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/settings/` | Get API settings |
| `POST` | `/keys/create/` | Create API key |
| `POST` | `/keys/{id}/revoke/` | Revoke API key |
| `POST` | `/keys/{id}/regenerate/` | Regenerate API key |
| `POST` | `/webhooks/create/` | Create webhook |
| `POST` | `/webhooks/{id}/toggle/` | Toggle webhook |
| `DELETE` | `/webhooks/{id}/delete/` | Delete webhook |

---

## 🛠️ Development Environments

### Production
- **Base URL:** `https://mifumosms.servehttp.com/api/integration/v1/`
- **Dashboard:** `https://mifumosms.servehttp.com`
- **Use for:** Live applications

### Development
- **Base URL:** `http://127.0.0.1:8001/api/integration/v1/`
- **Dashboard:** `http://127.0.0.1:8001`
- **Use for:** Testing and development

---

## 📋 Code Examples

### Python
```python
import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
response = requests.post(
    "https://mifumosms.servehttp.com/api/integration/v1/sms/send/",
    json={
        "message": "Hello from Python!",
        "recipients": ["+255123456789"]
    },
    headers=headers
)
print(response.json())
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const response = await axios.post(
  'https://mifumosms.servehttp.com/api/integration/v1/sms/send/',
  {
    message: 'Hello from Node.js!',
    recipients: ['+255123456789']
  },
  {
    headers: { 'Authorization': 'Bearer YOUR_API_KEY' }
  }
);
console.log(response.data);
```

### PHP
```php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'https://mifumosms.servehttp.com/api/integration/v1/sms/send/');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'message' => 'Hello from PHP!',
    'recipients' => ['+255123456789']
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer YOUR_API_KEY',
    'Content-Type: application/json'
]);
$response = curl_exec($ch);
curl_close($ch);
```

---

## 🔐 Authentication

All API requests require authentication using an API key:

```http
Authorization: Bearer YOUR_API_KEY_HERE
```

### Getting API Keys
1. **Dashboard Method:** Use the Settings → API & Webhooks page
2. **API Method:** Use the Settings API endpoints

---

## 📞 Webhooks

Set up webhooks to receive real-time notifications:

### Available Events
- `message.sent` - Message was sent
- `message.delivered` - Message was delivered
- `message.failed` - Message delivery failed

### Webhook Setup
1. Go to Settings → API & Webhooks
2. Click "Add Webhook"
3. Enter your webhook URL
4. Select events to receive
5. Save configuration

---

## 🚨 Error Handling

### Common Error Codes
- `AUTHENTICATION_REQUIRED` - Missing API key
- `INVALID_API_KEY` - Invalid or expired key
- `MISSING_MESSAGE` - Message text required
- `INVALID_PHONE_FORMAT` - Use E.164 format (+255XXXXXXXXX)
- `SMS_SEND_FAILED` - SMS sending failed

### Response Format
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "error_code": null,
  "details": null
}
```

---

## 📊 Rate Limits

| Operation | Limit |
|-----------|-------|
| SMS Sending | 100 requests/minute |
| Status Checks | 200 requests/minute |
| Delivery Reports | 50 requests/minute |
| Balance Checks | 20 requests/minute |

---

## 🆘 Support

- **Documentation:** This guide and linked documents
- **Email Support:** support@mifumosms.com
- **Status Page:** [https://status.mifumosms.com](https://status.mifumosms.com)
- **Dashboard:** [https://mifumosms.servehttp.com](https://mifumosms.servehttp.com)

---

## 📝 Changelog

### Version 1.0.0 (2024-01-01)
- Initial API release
- SMS sending and status checking
- Delivery reports and balance
- Webhook support
- User settings management

---

## 🤝 Contributing

Found an issue or want to improve the documentation? 
- Report issues via email: support@mifumosms.com
- Suggest improvements through the dashboard feedback form

---

*Last updated: January 2024*

