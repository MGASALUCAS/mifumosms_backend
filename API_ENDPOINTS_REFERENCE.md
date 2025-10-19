# API Endpoints Reference - Quick Lookup

## 🔐 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/accounts/register/` | User registration | No |
| POST | `/api/accounts/login/` | User login | No |
| POST | `/api/accounts/token/refresh/` | Refresh JWT token | No |
| POST | `/api/accounts/logout/` | User logout | Yes |
| GET | `/api/accounts/profile/` | Get user profile | Yes |
| PUT | `/api/accounts/profile/` | Update user profile | Yes |

---

## 📦 SMS Packages Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/billing/sms/packages/` | List all SMS packages | Yes |
| GET | `/api/billing/sms/packages/{id}/` | Get specific package | Yes |

### Package Types Available:
- **Real User Test Package**: 5 credits, 250 TZS, 50 TZS/SMS
- **Lite**: 5000 credits, 150,000 TZS, 30 TZS/SMS
- **Standard**: 50,000 credits, 1,250,000 TZS, 25 TZS/SMS (Popular)
- **Pro**: 250,000 credits, 4,500,000 TZS, 18 TZS/SMS
- **Enterprise**: 1,000,000 credits, 12,000,000 TZS, 12 TZS/SMS

---

## 💰 SMS Balance & Usage Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/billing/sms/balance/` | Get current SMS balance | Yes |
| GET | `/api/billing/sms/usage/statistics/` | Get usage statistics | Yes |
| GET | `/api/billing/sms/usage/records/` | Get usage records | Yes |

---

## 💳 Payment Endpoints

### Mobile Money Providers
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/billing/payments/providers/` | Get available payment providers | Yes |

### Package Purchases
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/billing/payments/initiate/` | Initiate package purchase | Yes |
| GET | `/api/billing/payments/verify/{order_id}/` | Verify payment status | Yes |
| GET | `/api/billing/payments/transactions/{id}/progress/` | Get payment progress | Yes |
| POST | `/api/billing/payments/transactions/{id}/cancel/` | Cancel payment | Yes |
| GET | `/api/billing/payments/active/` | Get active payments | Yes |

### Custom SMS Purchases
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/billing/payments/custom-sms/calculate/` | Calculate custom pricing | Yes |
| POST | `/api/billing/payments/custom-sms/initiate/` | Initiate custom purchase | Yes |
| GET | `/api/billing/payments/custom-sms/{id}/status/` | Check custom purchase status | Yes |

---

## 📱 SMS Sending Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/messaging/sms/send/` | Send SMS message | Yes |
| GET | `/api/messaging/sms/messages/` | Get SMS history | Yes |
| GET | `/api/messaging/sms/messages/{id}/` | Get specific SMS | Yes |
| GET | `/api/messaging/sms/delivery-reports/` | Get delivery reports | Yes |

---

## 🏷️ Sender ID Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/messaging/sender-ids/` | Get available sender IDs | Yes |
| POST | `/api/messaging/sender-ids/request/` | Request new sender ID | Yes |
| GET | `/api/messaging/sender-ids/{id}/` | Get specific sender ID | Yes |
| GET | `/api/messaging/sender-ids/{id}/status/` | Check request status | Yes |
| PUT | `/api/messaging/sender-ids/{id}/` | Update sender ID | Yes |
| DELETE | `/api/messaging/sender-ids/{id}/` | Delete sender ID | Yes |

---

## 🏢 Tenant Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tenants/profile/` | Get tenant profile | Yes |
| PUT | `/api/tenants/profile/` | Update tenant profile | Yes |
| GET | `/api/tenants/members/` | Get tenant members | Yes |
| POST | `/api/tenants/members/invite/` | Invite new member | Yes |
| PUT | `/api/tenants/members/{id}/` | Update member role | Yes |
| DELETE | `/api/tenants/members/{id}/` | Remove member | Yes |

---

## 📊 Billing & Analytics Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/billing/overview/` | Get billing overview | Yes |
| GET | `/api/billing/sms/purchases/` | Get purchase history | Yes |
| GET | `/api/billing/sms/purchases/history/` | Get detailed purchase history | Yes |
| GET | `/api/billing/sms/purchases/{id}/` | Get specific purchase | Yes |
| GET | `/api/billing/plans/` | Get billing plans | Yes |
| GET | `/api/billing/subscription/` | Get current subscription | Yes |

---

## 🔍 Query Parameters Reference

### Pagination
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Filtering
- `status`: Filter by status
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `search`: Search term

### Ordering
- `ordering`: Sort field (prefix with `-` for descending)

### Examples:
```
GET /api/billing/sms/purchases/?page=1&page_size=10&status=completed
GET /api/messaging/sms/messages/?ordering=-created_at&search=test
GET /api/billing/sms/usage/statistics/?start_date=2024-01-01&end_date=2024-01-31
```

---

## 📋 Request/Response Examples

### Login Request
```json
POST /api/accounts/login/
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Login Response
```json
{
  "success": true,
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true
  }
}
```

### Send SMS Request
```json
POST /api/messaging/sms/send/
{
  "recipients": ["+255123456789"],
  "message": "Hello from Mifumo SMS!",
  "sender_id": "MIFUMO"
}
```

### Send SMS Response
```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "recipients_count": 1,
    "credits_required": 1,
    "estimated_cost": 25.00,
    "status": "queued"
  }
}
```

### Purchase Package Request
```json
POST /api/billing/payments/initiate/
{
  "package_id": "uuid",
  "mobile_money_provider": "vodacom"
}
```

### Purchase Package Response
```json
{
  "success": true,
  "data": {
    "transaction_id": "uuid",
    "order_id": "MIFUMO-20240115-ABC123",
    "amount": 150000.00,
    "credits": 5000,
    "provider": "vodacom",
    "provider_name": "Vodacom M-Pesa",
    "payment_instructions": {
      "step": "dial",
      "message": "Dial *150*00# to pay 150,000 TZS",
      "reference": "MIFUMO-20240115-ABC123"
    },
    "expires_at": "2024-01-15T11:00:00Z"
  }
}
```

---

## ⚠️ Error Response Format

### Standard Error Response
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "validation_error",
  "details": {
    "field_name": ["This field is required."]
  }
}
```

### Common Error Types
- `validation_error`: Input validation failed
- `authentication_error`: Authentication required
- `permission_error`: Insufficient permissions
- `not_found`: Resource not found
- `insufficient_credits`: Not enough SMS credits
- `payment_failed`: Payment processing failed
- `rate_limit_exceeded`: Too many requests

---

## 🔄 Status Codes Reference

| Code | Description | When Used |
|------|-------------|-----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation errors, invalid input |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 🚀 Rate Limits

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 5 requests | 1 minute |
| SMS Sending | 100 requests | 1 minute |
| Payment | 10 requests | 1 minute |
| General API | 1000 requests | 1 hour |

---

## 📱 Mobile Money Providers

| Code | Name | Min Amount | Max Amount | Status |
|------|------|------------|------------|--------|
| `vodacom` | Vodacom M-Pesa | 1,000 TZS | 1,000,000 TZS | Active |
| `tigo` | Tigo Pesa | 1,000 TZS | 500,000 TZS | Active |
| `airtel` | Airtel Money | 1,000 TZS | 500,000 TZS | Active |
| `halotel` | Halotel Money | 1,000 TZS | 500,000 TZS | Active |

---

## 🔧 Development Tips

1. **Always check the `success` field** in responses
2. **Handle errors gracefully** with proper user feedback
3. **Implement retry logic** for failed requests
4. **Use pagination** for large data sets
5. **Cache frequently accessed data** like packages and balance
6. **Implement loading states** for better UX
7. **Validate inputs** before sending requests

---

*Last updated: January 2024*
