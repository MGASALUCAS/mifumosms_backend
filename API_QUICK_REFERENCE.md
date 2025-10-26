# Mifumo SMS API - Quick Reference Guide

## 🚀 **Quick Start**

### 1. Get Your API Key
```bash
# Visit the dashboard
http://127.0.0.1:8001/api/integration/dashboard/
```

### 2. Send Your First SMS
```bash
curl -X POST "http://127.0.0.1:8001/api/integration/v1/sms/send/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_KEY" \
-d '{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789"]
}'
```

---

## 📱 **SMS API**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/sms/send/` | POST | Send SMS |
| `/v1/sms/status/{id}/` | GET | Get message status |
| `/v1/sms/delivery-reports/` | GET | Get delivery reports |
| `/v1/sms/balance/` | GET | Get account balance |

### **Send SMS Payload**
```json
{
  "message": "Your message here",
  "recipients": ["+255123456789"],
  "sender_id": "MIFUMO"
}
```

---

## 👥 **Contacts API**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/contacts/create/` | POST | Create contact |
| `/v1/contacts/{id}/` | GET | Get contact |
| `/v1/contacts/{id}/update/` | PUT | Update contact |
| `/v1/contacts/{id}/delete/` | DELETE | Delete contact |
| `/v1/contacts/search/` | GET | Search contacts |

### **Create Contact Payload**
```json
{
  "name": "John Doe",
  "phone_number": "+255123456789",
  "email": "john@example.com",
  "tags": ["customer"]
}
```

---

## 🏷️ **Segments API**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/contacts/segments/create/` | POST | Create segment |
| `/v1/contacts/segments/{id}/` | GET | Get segment |
| `/v1/contacts/segments/{id}/update/` | PUT | Update segment |
| `/v1/contacts/segments/{id}/delete/` | DELETE | Delete segment |

---

## 🔑 **Authentication**

All requests require:
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

---

## 📊 **Response Format**

### **Success Response**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { /* response data */ },
  "error_code": null,
  "details": null
}
```

### **Error Response**
```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "error_code": "ERROR_CODE",
  "details": "Additional details"
}
```

---

## 🚨 **Common Error Codes**

| Code | Description |
|------|-------------|
| `INVALID_CREDENTIALS` | Invalid API key |
| `INVALID_PHONE` | Invalid phone format |
| `INSUFFICIENT_BALANCE` | Low account balance |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

---

## 📞 **Phone Number Format**

Use E.164 format:
- ✅ `+255123456789`
- ❌ `0751234567`
- ❌ `255123456789`

---

## 🔗 **Webhooks**

Set up webhooks for real-time notifications:
```json
{
  "message": "Hello!",
  "recipients": ["+255123456789"],
  "webhook_url": "https://your-domain.com/webhook"
}
```

---

## 📈 **Rate Limits**

- SMS: 100/minute
- API: 1000/hour
- Contacts: 500/hour

---

## 🆘 **Need Help?**

- **Dashboard**: http://127.0.0.1:8001/api/integration/dashboard/
- **Documentation**: http://127.0.0.1:8001/api/integration/documentation/
- **Support**: support@mifumosms.com
