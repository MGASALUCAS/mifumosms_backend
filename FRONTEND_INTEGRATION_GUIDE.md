# Frontend Integration Guide - Mifumo SMS Backend

## 📋 Table of Contents
1. [Authentication & Setup](#authentication--setup)
2. [SMS Packages Management](#sms-packages-management)
3. [SMS Balance & Usage Tracking](#sms-balance--usage-tracking)
4. [Payment Integration](#payment-integration)
5. [SMS Sending & History](#sms-sending--history)
6. [Sender ID Management](#sender-id-management)
7. [Tenant Management](#tenant-management)
8. [Error Handling](#error-handling)
9. [Real-time Updates](#real-time-updates)
10. [API Response Examples](#api-response-examples)

---

## 🔐 Authentication & Setup

### JWT Token Authentication
All API requests require JWT authentication via the `Authorization` header.

```javascript
// Login and get tokens
const loginResponse = await fetch('/api/accounts/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access, refresh } = await loginResponse.json();

// Use access token for API requests
const apiHeaders = {
  'Authorization': `Bearer ${access}`,
  'Content-Type': 'application/json'
};
```

### Token Refresh
```javascript
const refreshToken = async (refreshToken) => {
  const response = await fetch('/api/accounts/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken })
  });
  return response.json();
};
```

---

## 📦 SMS Packages Management

### Get Available SMS Packages
```javascript
const getSMSPackages = async () => {
  const response = await fetch('/api/billing/sms/packages/', {
    headers: apiHeaders
  });
  return response.json();
};

// Response structure:
{
  "success": true,
  "results": [
    {
      "id": "uuid",
      "name": "Lite",
      "package_type": "lite",
      "credits": 5000,
      "price": "150000.00",
      "unit_price": "30.00",
      "is_popular": false,
      "is_active": true,
      "features": ["Instant top-up", "Basic delivery reports"],
      "savings_percentage": 0.0,
      "default_sender_id": "MIFUMO",
      "allowed_sender_ids": ["MIFUMO", "SMS", "INFO"],
      "sender_id_restriction": "allowed_list"
    }
  ]
}
```

### Package Types Available
- **Real User Test Package**: 5 credits, 250 TZS, 50 TZS/SMS
- **Lite**: 5000 credits, 150,000 TZS, 30 TZS/SMS
- **Standard**: 50,000 credits, 1,250,000 TZS, 25 TZS/SMS (Popular)
- **Pro**: 250,000 credits, 4,500,000 TZS, 18 TZS/SMS
- **Enterprise**: 1,000,000 credits, 12,000,000 TZS, 12 TZS/SMS

---

## 💰 SMS Balance & Usage Tracking

### Get Current Balance
```javascript
const getSMSBalance = async () => {
  const response = await fetch('/api/billing/sms/balance/', {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "id": "uuid",
    "tenant": "Company Name",
    "credits": 5000,
    "total_purchased": 10000,
    "total_used": 5000,
    "last_updated": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Get Usage Statistics
```javascript
const getUsageStatistics = async () => {
  const response = await fetch('/api/billing/sms/usage/statistics/', {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "data": {
    "current_balance": 5000,
    "total_usage": {
      "credits": 5000,
      "cost": 125000.0,
      "period": "all_time"
    },
    "monthly_usage": {
      "credits": 1000,
      "cost": 25000.0,
      "period": "monthly"
    },
    "weekly_usage": {
      "credits": 200,
      "cost": 5000.0,
      "period": "weekly"
    },
    "daily_usage": [
      {
        "date": "2024-01-15",
        "credits": 50,
        "cost": 1250.0
      }
    ]
  }
}
```

---

## 💳 Payment Integration

### Get Mobile Money Providers
```javascript
const getPaymentProviders = async () => {
  const response = await fetch('/api/billing/payments/providers/', {
    headers: apiHeaders
  });
  return response.json();
};

// Response:
{
  "success": true,
  "providers": [
    {
      "code": "vodacom",
      "name": "Vodacom M-Pesa",
      "description": "Pay with M-Pesa via Vodacom",
      "icon": "vodacom-icon",
      "popular": true,
      "is_active": true,
      "min_amount": 1000,
      "max_amount": 1000000
    }
  ]
}
```

### Initiate Package Purchase
```javascript
const purchasePackage = async (packageId, paymentMethod) => {
  const response = await fetch('/api/billing/payments/initiate/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      package_id: packageId,
      mobile_money_provider: paymentMethod
    })
  });
  return response.json();
};

// Response:
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

### Custom SMS Purchase
```javascript
const calculateCustomPricing = async (credits) => {
  const response = await fetch('/api/billing/payments/custom-sms/calculate/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({ credits })
  });
  return response.json();
};

const initiateCustomPurchase = async (credits, paymentMethod) => {
  const response = await fetch('/api/billing/payments/custom-sms/initiate/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      credits,
      mobile_money_provider: paymentMethod
    })
  });
  return response.json();
};
```

### Check Payment Status
```javascript
const checkPaymentStatus = async (orderId) => {
  const response = await fetch(`/api/billing/payments/verify/${orderId}/`, {
    headers: apiHeaders
  });
  return response.json();
};

const getPaymentProgress = async (transactionId) => {
  const response = await fetch(`/api/billing/payments/transactions/${transactionId}/progress/`, {
    headers: apiHeaders
  });
  return response.json();
};
```

---

## 📱 SMS Sending & History

### Send SMS
```javascript
const sendSMS = async (recipients, message, senderId) => {
  const response = await fetch('/api/messaging/sms/send/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      recipients: recipients, // Array of phone numbers
      message: message,
      sender_id: senderId
    })
  });
  return response.json();
};

// Response:
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

### Get SMS History
```javascript
const getSMSHistory = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/messaging/sms/messages/?${params}`, {
    headers: apiHeaders
  });
  return response.json();
};

// Filters available:
// - status: sent, delivered, failed, pending
// - sender_id: specific sender ID
// - search: search in phone numbers or message content
// - ordering: -created_at, created_at, -sent_at, sent_at
```

### Get Purchase History
```javascript
const getPurchaseHistory = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/billing/sms/purchases/history/?${params}`, {
    headers: apiHeaders
  });
  return response.json();
};

// Filters available:
// - status: pending, completed, failed, cancelled, refunded
// - start_date: YYYY-MM-DD
// - end_date: YYYY-MM-DD
// - page: page number
// - page_size: items per page
```

---

## 🏷️ Sender ID Management

### Get Sender IDs
```javascript
const getSenderIDs = async () => {
  const response = await fetch('/api/messaging/sender-ids/', {
    headers: apiHeaders
  });
  return response.json();
};
```

### Request New Sender ID
```javascript
const requestSenderID = async (senderId, businessName, contactPhone) => {
  const response = await fetch('/api/messaging/sender-ids/request/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      requested_sender_id: senderId,
      business_name: businessName,
      contact_phone: contactPhone,
      purpose: "Marketing and notifications"
    })
  });
  return response.json();
};
```

### Check Sender ID Status
```javascript
const getSenderIDStatus = async (requestId) => {
  const response = await fetch(`/api/messaging/sender-ids/${requestId}/status/`, {
    headers: apiHeaders
  });
  return response.json();
};
```

---

## 🏢 Tenant Management

### Get Tenant Information
```javascript
const getTenantInfo = async () => {
  const response = await fetch('/api/tenants/profile/', {
    headers: apiHeaders
  });
  return response.json();
};
```

### Update Tenant Profile
```javascript
const updateTenantProfile = async (profileData) => {
  const response = await fetch('/api/tenants/profile/', {
    method: 'PUT',
    headers: apiHeaders,
    body: JSON.stringify(profileData)
  });
  return response.json();
};
```

---

## ⚠️ Error Handling

### Common Error Responses
```javascript
// Validation Error
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "field_name": ["This field is required."]
  }
}

// Authentication Error
{
  "success": false,
  "error": "Authentication credentials were not provided."
}

// Insufficient Credits
{
  "success": false,
  "error": "Insufficient credits for SMS sending",
  "error_type": "insufficient_credits",
  "required_credits": 5,
  "available_credits": 2
}

// Payment Error
{
  "success": false,
  "error": "Payment failed",
  "error_type": "payment_failed",
  "transaction_id": "uuid"
}
```

### Error Handling Implementation
```javascript
const handleApiError = (error, response) => {
  if (response.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  } else if (response.status === 403) {
    // Show permission error
    showError('You do not have permission to perform this action');
  } else if (response.status === 400) {
    // Show validation errors
    const errorData = response.json();
    showValidationErrors(errorData.details);
  } else if (response.status === 500) {
    // Show server error
    showError('Server error. Please try again later.');
  }
};
```

---

## 🔄 Real-time Updates

### Polling for Balance Updates
```javascript
const pollBalance = () => {
  setInterval(async () => {
    const balance = await getSMSBalance();
    updateBalanceDisplay(balance.data);
  }, 30000); // Poll every 30 seconds
};
```

### Polling for Payment Status
```javascript
const pollPaymentStatus = (orderId, onComplete) => {
  const interval = setInterval(async () => {
    const status = await checkPaymentStatus(orderId);
    if (status.data.status === 'completed') {
      clearInterval(interval);
      onComplete(status.data);
    } else if (status.data.status === 'failed') {
      clearInterval(interval);
      showError('Payment failed');
    }
  }, 5000); // Poll every 5 seconds
};
```

---

## 📊 Dashboard Integration

### Billing Overview
```javascript
const getBillingOverview = async () => {
  const response = await fetch('/api/billing/overview/', {
    headers: apiHeaders
  });
  return response.json();
};

// Response includes:
// - Current subscription
// - SMS balance
// - Usage statistics
// - Recent purchases
// - Active payments
```

### Usage Analytics
```javascript
const getUsageAnalytics = async (period = 'monthly') => {
  const response = await fetch(`/api/billing/sms/usage/statistics/?period=${period}`, {
    headers: apiHeaders
  });
  return response.json();
};
```

---

## 🎨 UI Component Examples

### SMS Package Card
```jsx
const SMSPackageCard = ({ package, onSelect }) => (
  <div className={`package-card ${package.is_popular ? 'popular' : ''}`}>
    {package.is_popular && <div className="popular-badge">Popular</div>}
    <h3>{package.name}</h3>
    <div className="credits">{package.credits.toLocaleString()} SMS</div>
    <div className="price">TZS {parseFloat(package.price).toLocaleString()}</div>
    <div className="unit-price">TZS {package.unit_price}/SMS</div>
    {package.savings_percentage > 0 && (
      <div className="savings">{package.savings_percentage}% OFF</div>
    )}
    <ul className="features">
      {package.features.map(feature => (
        <li key={feature}>{feature}</li>
      ))}
    </ul>
    <button onClick={() => onSelect(package)}>Select Package</button>
  </div>
);
```

### Balance Display
```jsx
const BalanceDisplay = ({ balance }) => (
  <div className="balance-card">
    <h3>SMS Balance</h3>
    <div className="credits">{balance.credits.toLocaleString()}</div>
    <div className="usage">
      <span>Used: {balance.total_used.toLocaleString()}</span>
      <span>Purchased: {balance.total_purchased.toLocaleString()}</span>
    </div>
  </div>
);
```

### Payment Status
```jsx
const PaymentStatus = ({ payment }) => (
  <div className={`payment-status ${payment.status}`}>
    <div className="status">{payment.status}</div>
    <div className="amount">TZS {payment.amount.toLocaleString()}</div>
    <div className="credits">{payment.credits} SMS</div>
    {payment.status === 'pending' && (
      <div className="instructions">
        {payment.payment_instructions.message}
      </div>
    )}
  </div>
);
```

---

## 🔧 Configuration

### API Base URL
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

### Request Interceptor
```javascript
// Axios interceptor for automatic token refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const newTokens = await refreshToken(refreshToken);
          localStorage.setItem('access_token', newTokens.access);
          // Retry original request
          return axios.request(error.config);
        } catch (refreshError) {
          // Redirect to login
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 📱 Mobile Responsiveness

### Breakpoints
```css
/* Mobile First Approach */
.package-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .package-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .package-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## 🚀 Performance Tips

1. **Cache API responses** for packages and balance
2. **Implement pagination** for large lists
3. **Use loading states** for better UX
4. **Debounce search inputs** to reduce API calls
5. **Implement optimistic updates** for better perceived performance

---

## 📞 Support

For technical support or questions about the API:
- Email: support@mifumo.com
- Documentation: [API Documentation](./BILLING_API_DOCUMENTATION.md)
- Status Page: [status.mifumo.com](https://status.mifumo.com)

---

*Last updated: January 2024*
