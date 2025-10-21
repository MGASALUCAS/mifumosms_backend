# Billing History API Documentation

This document provides comprehensive documentation for the billing history endpoints in the Mifumo SMS backend.

## Base URL
- **Local**: `http://127.0.0.1:8000/api/billing/history/`
- **Production**: `https://your-domain.com/api/billing/history/`

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Get comprehensive billing history |
| `/summary/` | GET | Get billing history summary with charts |
| `/purchases/` | GET | Get detailed purchase history |
| `/payments/` | GET | Get detailed payment transaction history |
| `/usage/` | GET | Get detailed usage history |

---

## 1. Comprehensive Billing History

**Endpoint**: `GET /api/billing/history/`

**Description**: Get comprehensive billing history including purchases, payments, usage records, and custom purchases.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date filter (YYYY-MM-DD) |
| `end_date` | string | No | End date filter (YYYY-MM-DD) |

### Response

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_purchased": 150000.00,
      "total_credits_purchased": 5000,
      "total_usage_cost": 125000.00,
      "total_credits_used": 4500,
      "current_balance": 500,
      "total_purchases": 3,
      "total_payments": 3,
      "total_usage_records": 45
    },
    "purchases": [
      {
        "id": "uuid",
        "invoice_number": "INV-001",
        "package_name": "Standard Package",
        "amount": 50000.00,
        "credits": 2000,
        "status": "completed",
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "payments": [
      {
        "id": "uuid",
        "order_id": "ORD-001",
        "amount": 50000.00,
        "currency": "TZS",
        "payment_method": "mpesa",
        "status": "completed",
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "usage_records": [
      {
        "id": "uuid",
        "credits_used": 1,
        "cost": 25.00,
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "custom_purchases": [
      {
        "id": "uuid",
        "credits": 1000,
        "unit_price": 25.00,
        "total_price": 25000.00,
        "active_tier": "Standard",
        "status": "completed",
        "created_at": "2025-01-15T10:30:00Z"
      }
    ]
  }
}
```

---

## 2. Billing History Summary

**Endpoint**: `GET /api/billing/history/summary/`

**Description**: Get billing history summary with statistics and charts data for analytics.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | No | Time period (7d, 30d, 90d, 1y). Default: 30d |
| `start_date` | string | No | Start date filter (YYYY-MM-DD) |
| `end_date` | string | No | End date filter (YYYY-MM-DD) |

### Response

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_purchased": 150000.00,
      "total_credits_purchased": 5000,
      "total_usage_cost": 125000.00,
      "total_credits_used": 4500,
      "current_balance": 500,
      "total_purchases": 3,
      "total_payments": 3,
      "total_usage_records": 45,
      "period": "30d",
      "start_date": "2025-01-01",
      "end_date": "2025-01-31"
    },
    "charts": {
      "monthly_usage": [
        {
          "month": "2025-01",
          "credits": 1000,
          "cost": 25000.00
        },
        {
          "month": "2025-02",
          "credits": 1200,
          "cost": 30000.00
        }
      ],
      "payment_methods": [
        {
          "method": "mpesa",
          "count": 2,
          "amount": 100000.00
        },
        {
          "method": "tigopesa",
          "count": 1,
          "amount": 50000.00
        }
      ]
    }
  }
}
```

---

## 3. Detailed Purchase History

**Endpoint**: `GET /api/billing/history/purchases/`

**Description**: Get detailed purchase history with pagination and filtering.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by purchase status (pending, completed, failed, cancelled, expired, refunded) |
| `start_date` | string | No | Start date filter (YYYY-MM-DD) |
| `end_date` | string | No | End date filter (YYYY-MM-DD) |
| `page` | integer | No | Page number (default: 1) |
| `page_size` | integer | No | Items per page (default: 20) |

### Response

```json
{
  "success": true,
  "data": {
    "purchases": [
      {
        "id": "uuid",
        "invoice_number": "INV-001",
        "package": "uuid",
        "package_name": "Standard Package",
        "tenant": "Test Organization",
        "amount": 50000.00,
        "credits": 2000,
        "unit_price": 25.00,
        "payment_method": "mpesa",
        "payment_method_display": "M-Pesa",
        "payment_reference": "MP123456789",
        "status": "completed",
        "status_display": "Completed",
        "created_at": "2025-01-15T10:30:00Z",
        "completed_at": "2025-01-15T10:35:00Z"
      }
    ],
    "pagination": {
      "count": 10,
      "next": "?page=2&page_size=20",
      "previous": null,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

---

## 4. Detailed Payment History

**Endpoint**: `GET /api/billing/history/payments/`

**Description**: Get detailed payment transaction history with pagination and filtering.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by payment status (pending, processing, completed, failed, cancelled, expired, refunded) |
| `payment_method` | string | No | Filter by payment method (zenopay_mobile_money, mpesa, tigopesa, airtelmoney, bank_transfer, credit_card) |
| `start_date` | string | No | Start date filter (YYYY-MM-DD) |
| `end_date` | string | No | End date filter (YYYY-MM-DD) |
| `page` | integer | No | Page number (default: 1) |
| `page_size` | integer | No | Items per page (default: 20) |

### Response

```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "uuid",
        "order_id": "ORD-001",
        "zenopay_order_id": "ZP123456789",
        "invoice_number": "INV-001",
        "amount": 50000.00,
        "currency": "TZS",
        "buyer_email": "user@example.com",
        "buyer_name": "John Doe",
        "buyer_phone": "0744963858",
        "payment_method": "mpesa",
        "payment_method_display": "M-Pesa",
        "status": "completed",
        "status_display": "Completed",
        "zenopay_reference": "REF123456789",
        "zenopay_transid": "TXN123456789",
        "zenopay_channel": "MPESA-TZ",
        "zenopay_msisdn": "255744963858",
        "webhook_received": true,
        "created_at": "2025-01-15T10:30:00Z",
        "updated_at": "2025-01-15T10:35:00Z",
        "completed_at": "2025-01-15T10:35:00Z",
        "failed_at": null,
        "error_message": "",
        "purchase_data": {
          "id": "uuid",
          "package_name": "Standard Package",
          "credits": 2000,
          "unit_price": 25.00
        }
      }
    ],
    "pagination": {
      "count": 10,
      "next": "?page=2&page_size=20",
      "previous": null,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

---

## 5. Detailed Usage History

**Endpoint**: `GET /api/billing/history/usage/`

**Description**: Get detailed usage history with pagination and filtering.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date filter (YYYY-MM-DD) |
| `end_date` | string | No | End date filter (YYYY-MM-DD) |
| `page` | integer | No | Page number (default: 1) |
| `page_size` | integer | No | Items per page (default: 20) |

### Response

```json
{
  "success": true,
  "data": {
    "usage_records": [
      {
        "id": "uuid",
        "credits_used": 1,
        "cost": 25.00,
        "created_at": "2025-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "count": 100,
      "next": "?page=2&page_size=20",
      "previous": null,
      "page": 1,
      "page_size": 20,
      "total_pages": 5
    }
  }
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "success": false,
  "message": "User is not associated with any tenant.",
  "error": "Validation error details"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Failed to retrieve billing history",
  "error": "Error details"
}
```

---

## Usage Examples

### Get billing history for the last 30 days
```bash
curl -H "Authorization: Bearer <token>" \
     "http://127.0.0.1:8000/api/billing/history/summary/?period=30d"
```

### Get purchase history with pagination
```bash
curl -H "Authorization: Bearer <token>" \
     "http://127.0.0.1:8000/api/billing/history/purchases/?page=1&page_size=10"
```

### Get payment history filtered by status
```bash
curl -H "Authorization: Bearer <token>" \
     "http://127.0.0.1:8000/api/billing/history/payments/?status=completed"
```

### Get usage history for specific date range
```bash
curl -H "Authorization: Bearer <token>" \
     "http://127.0.0.1:8000/api/billing/history/usage/?start_date=2025-01-01&end_date=2025-01-31"
```

---

## Frontend Integration

### React/JavaScript Example

```javascript
// Get billing history summary
const getBillingSummary = async (period = '30d') => {
  try {
    const response = await fetch(`/api/billing/history/summary/?period=${period}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Use data.summary for statistics
      // Use data.charts for chart data
      return data.data;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Error fetching billing summary:', error);
    throw error;
  }
};

// Get purchase history with pagination
const getPurchaseHistory = async (page = 1, pageSize = 20, filters = {}) => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...filters
    });
    
    const response = await fetch(`/api/billing/history/purchases/?${params}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      return {
        purchases: data.data.purchases,
        pagination: data.data.pagination
      };
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Error fetching purchase history:', error);
    throw error;
  }
};
```

---

## Notes

1. **Authentication**: All endpoints require valid JWT authentication.
2. **Tenant Isolation**: All data is filtered by the authenticated user's tenant.
3. **Pagination**: Use `page` and `page_size` parameters for paginated results.
4. **Date Filters**: Use `start_date` and `end_date` in YYYY-MM-DD format.
5. **Error Handling**: Always check the `success` field in responses.
6. **Rate Limiting**: Be mindful of API rate limits when making multiple requests.

For more information about the billing system, see the main [BILLING_API_DOCUMENTATION.md](BILLING_API_DOCUMENTATION.md).
