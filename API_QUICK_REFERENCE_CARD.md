# Mifumo SMS API - Quick Reference

## Base URL
```
https://mifumosms.servehttp.com/api/integration/v1/
```

## Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### Send SMS
```http
POST /sms/send/
Content-Type: application/json

{
  "message": "Hello World!",
  "recipients": ["+255123456789"],
  "sender_id": "Taarifa-SMS"
}
```

### Get Message Status
```http
GET /sms/status/{message_id}/
```

### Get Delivery Reports
```http
GET /sms/delivery-reports/?page=1&per_page=50
```

### Get Balance
```http
GET /sms/balance/
```

---

## Response Format
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

## Common Error Codes
- `AUTHENTICATION_REQUIRED` - Missing API key
- `INVALID_API_KEY` - Invalid or expired key
- `MISSING_MESSAGE` - Message text required
- `INVALID_PHONE_FORMAT` - Use E.164 format (+255XXXXXXXXX)
- `SMS_SEND_FAILED` - SMS sending failed

---

## Phone Number Format
✅ `+255123456789` (E.164 format)  
❌ `0712345678` (Local format)

---

## Rate Limits
- SMS Sending: 100/min
- Status Checks: 200/min
- Reports: 50/min
- Balance: 20/min

