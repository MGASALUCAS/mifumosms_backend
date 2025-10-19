# 🎯 Frontend API Endpoints Summary

## 🚀 **Ready for Frontend Implementation**

All APIs are production-ready with comprehensive documentation and test coverage.

## 📋 **Quick Reference - All Endpoints**

### **Authentication**
```javascript
// All requests require JWT token
headers: {
  'Authorization': 'Bearer <jwt_token>',
  'Content-Type': 'application/json'
}
```

---

## 💰 **Billing API Endpoints**

### **SMS Packages**
```javascript
// Get all SMS packages
GET /api/billing/sms/packages/

// Get SMS balance
GET /api/billing/sms/balance/
```

### **Purchase Management**
```javascript
// Get purchase history
GET /api/billing/sms/purchases/

// Get detailed purchase history with filters
GET /api/billing/sms/purchases/history/?status=completed&start_date=2024-01-01&page=1
```

### **Custom SMS Pricing**
```javascript
// Calculate custom SMS pricing
POST /api/billing/payments/custom-sms/calculate/
Body: { "credits": 5000 }

// Initiate custom SMS purchase
POST /api/billing/payments/custom-sms/initiate/
Body: { "credits": 5000, "mobile_money_provider": "vodacom", "phone_number": "255712345678" }

// Check custom SMS purchase status
GET /api/billing/payments/custom-sms/{purchase_id}/status/
```

### **Payment Processing**
```javascript
// Get mobile money providers
GET /api/billing/payments/providers/

// Initiate payment
POST /api/billing/payments/initiate/
Body: { "package_id": "uuid", "mobile_money_provider": "vodacom", "phone_number": "255712345678" }

// Verify payment
GET /api/billing/payments/verify/{order_id}/

// Get payment progress
GET /api/billing/payments/transactions/{transaction_id}/progress/

// Get active payments
GET /api/billing/payments/active/

// Cancel payment
POST /api/billing/payments/transactions/{transaction_id}/cancel/
```

### **Usage & Statistics**
```javascript
// Get usage statistics
GET /api/billing/sms/usage/statistics/?start_date=2024-01-01&end_date=2024-12-31

// Get billing overview
GET /api/billing/overview/
```

### **Subscription Management**
```javascript
// Get billing plans
GET /api/billing/plans/

// Get subscription details
GET /api/billing/subscription/
```

---

## 📱 **Sender ID Management Endpoints**

### **Sender ID Requests**
```javascript
// Get sender ID requests
GET /api/messaging/sender-id-requests/

// Create sender ID request
POST /api/messaging/sender-id-requests/
Body: {
  "request_type": "custom",
  "requested_sender_id": "MYCOMPANY",
  "sample_content": "Hello from MyCompany!",
  "business_justification": "Customer communications",
  "sms_package": "uuid"
}

// Get sender ID request details
GET /api/messaging/sender-id-requests/{request_id}/

// Update sender ID request
PUT /api/messaging/sender-id-requests/{request_id}/

// Delete sender ID request
DELETE /api/messaging/sender-id-requests/{request_id}/
```

### **Default Sender ID**
```javascript
// Request default sender ID (auto-approved)
POST /api/messaging/sender-id-requests/default/
```

### **Available Sender IDs**
```javascript
// Get available sender IDs
GET /api/messaging/sender-id-requests/available/

// Get sender ID request status
GET /api/messaging/sender-id-requests/status/
```

### **Sender ID Usage**
```javascript
// Get sender ID usage
GET /api/messaging/sender-id-usage/

// Attach sender ID to SMS package
POST /api/messaging/sender-id-usage/
Body: { "sender_id_request": "uuid", "sms_package": "uuid" }

// Detach sender ID from SMS package
POST /api/messaging/sender-id-usage/{usage_id}/detach/
```

### **Admin Review (Admin Only)**
```javascript
// Review sender ID request
PUT /api/messaging/sender-id-requests/{request_id}/review/
Body: { "status": "approved" } // or "rejected" with "rejection_reason"
```

---

## 🏢 **Tenant Management Endpoints**

### **Tenant Operations**
```javascript
// Get user's tenants
GET /api/tenants/

// Create new tenant
POST /api/tenants/
Body: {
  "name": "My Company",
  "subdomain": "mycompany",
  "timezone": "Africa/Dar_es_Salaam",
  "business_name": "My Company Ltd",
  "business_type": "Technology",
  "phone_number": "+255712345678",
  "email": "contact@mycompany.com",
  "address": "123 Main St, Dar es Salaam"
}

// Get tenant details
GET /api/tenants/{tenant_id}/

// Update tenant
PUT /api/tenants/{tenant_id}/

// Delete tenant
DELETE /api/tenants/{tenant_id}/
```

### **Tenant Switching**
```javascript
// Switch current tenant
POST /api/tenants/switch/
Body: { "tenant_id": "uuid" }
```

### **Domain Management**
```javascript
// Get tenant domains
GET /api/tenants/{tenant_id}/domains/

// Add custom domain
POST /api/tenants/{tenant_id}/domains/
Body: { "domain": "mycompany.com", "is_primary": false }

// Update domain
PUT /api/tenants/{tenant_id}/domains/{domain_id}/

// Delete domain
DELETE /api/tenants/{tenant_id}/domains/{domain_id}/
```

### **Member Management**
```javascript
// Get tenant members
GET /api/tenants/{tenant_id}/members/

// Invite new member
POST /api/tenants/{tenant_id}/members/
Body: { "email": "newuser@example.com", "role": "agent" }

// Update member role/status
PUT /api/tenants/{tenant_id}/members/{membership_id}/

// Remove member
DELETE /api/tenants/{tenant_id}/members/{membership_id}/
```

### **Invitations**
```javascript
// Accept invitation
GET /api/tenants/invite/{token}/
```

---

## 🎨 **Frontend Implementation Guide**

### **1. State Management Structure**
```javascript
// Redux/Context State Structure
const state = {
  auth: {
    user: null,
    token: null,
    isAuthenticated: false
  },
  tenant: {
    current: null,
    available: [],
    switching: false
  },
  billing: {
    packages: [],
    balance: null,
    purchases: [],
    usage: null,
    overview: null
  },
  senderIds: {
    requests: [],
    available: [],
    usage: []
  },
  payments: {
    providers: [],
    active: [],
    history: []
  }
}
```

### **2. API Service Layer**
```javascript
// api/billing.js
export const billingAPI = {
  getPackages: () => api.get('/billing/sms/packages/'),
  getBalance: () => api.get('/billing/sms/balance/'),
  getPurchases: (params) => api.get('/billing/sms/purchases/', { params }),
  calculatePricing: (credits) => api.post('/billing/payments/custom-sms/calculate/', { credits }),
  initiatePurchase: (data) => api.post('/billing/payments/custom-sms/initiate/', data),
  getUsageStats: (params) => api.get('/billing/sms/usage/statistics/', { params }),
  getOverview: () => api.get('/billing/overview/')
}

// api/senderIds.js
export const senderIdAPI = {
  getRequests: () => api.get('/messaging/sender-id-requests/'),
  createRequest: (data) => api.post('/messaging/sender-id-requests/', data),
  getAvailable: () => api.get('/messaging/sender-id-requests/available/'),
  getStatus: () => api.get('/messaging/sender-id-requests/status/'),
  attachToPackage: (data) => api.post('/messaging/sender-id-usage/', data)
}

// api/tenants.js
export const tenantAPI = {
  getTenants: () => api.get('/tenants/'),
  createTenant: (data) => api.post('/tenants/', data),
  switchTenant: (tenantId) => api.post('/tenants/switch/', { tenant_id: tenantId }),
  getMembers: (tenantId) => api.get(`/tenants/${tenantId}/members/`),
  inviteMember: (tenantId, data) => api.post(`/tenants/${tenantId}/members/`, data)
}
```

### **3. React Components Structure**
```javascript
// components/billing/
├── SMSPackages.jsx
├── SMSBalance.jsx
├── PurchaseHistory.jsx
├── CustomPricing.jsx
├── PaymentFlow.jsx
├── UsageStatistics.jsx
└── BillingOverview.jsx

// components/senderIds/
├── SenderIdRequests.jsx
├── SenderIdForm.jsx
├── AvailableSenderIds.jsx
└── SenderIdUsage.jsx

// components/tenants/
├── TenantList.jsx
├── TenantForm.jsx
├── TenantSwitcher.jsx
├── MemberManagement.jsx
└── DomainManagement.jsx
```

### **4. Error Handling**
```javascript
// utils/errorHandler.js
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return { type: 'validation', message: data.message, errors: data };
      case 401:
        return { type: 'auth', message: 'Please log in again' };
      case 403:
        return { type: 'permission', message: 'You don\'t have permission to perform this action' };
      case 404:
        return { type: 'not_found', message: 'Resource not found' };
      default:
        return { type: 'server', message: 'Server error occurred' };
    }
  } else if (error.request) {
    // Network error
    return { type: 'network', message: 'Network error. Please check your connection.' };
  } else {
    // Other error
    return { type: 'unknown', message: 'An unexpected error occurred' };
  }
};
```

### **5. Real-time Updates**
```javascript
// hooks/useWebSocket.js
export const useWebSocket = (url, onMessage) => {
  const [socket, setSocket] = useState(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    setSocket(ws);
    return () => ws.close();
  }, [url, onMessage]);
  
  return socket;
};

// Usage for real-time updates
const useBillingUpdates = () => {
  const dispatch = useDispatch();
  
  useWebSocket('ws://localhost:8000/ws/billing/', (data) => {
    switch (data.type) {
      case 'balance_updated':
        dispatch(updateBalance(data.balance));
        break;
      case 'payment_completed':
        dispatch(addPurchase(data.purchase));
        break;
      case 'usage_updated':
        dispatch(updateUsage(data.usage));
        break;
    }
  });
};
```

---

## 🔧 **Common Patterns**

### **1. API Response Handling**
```javascript
const handleAPIResponse = async (apiCall) => {
  try {
    const response = await apiCall();
    return {
      success: true,
      data: response.data.data || response.data,
      message: response.data.message
    };
  } catch (error) {
    return {
      success: false,
      error: handleAPIError(error)
    };
  }
};
```

### **2. Loading States**
```javascript
const useAsyncState = (initialState) => {
  const [state, setState] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const execute = async (asyncFunction) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await asyncFunction();
      setState(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return [state, loading, error, execute];
};
```

### **3. Form Validation**
```javascript
const validateSenderId = (senderId) => {
  if (!senderId) return 'Sender ID is required';
  if (senderId.length > 11) return 'Sender ID cannot exceed 11 characters';
  if (!/^[A-Z0-9\s\-]+$/.test(senderId)) {
    return 'Sender ID can only contain letters, numbers, spaces, and hyphens';
  }
  return null;
};
```

---

## 📱 **Mobile App Considerations**

### **1. Offline Support**
```javascript
// Store critical data locally
const useOfflineData = () => {
  const [offlineData, setOfflineData] = useState(null);
  
  useEffect(() => {
    // Load from local storage
    const stored = localStorage.getItem('billing_data');
    if (stored) {
      setOfflineData(JSON.parse(stored));
    }
  }, []);
  
  const updateOfflineData = (data) => {
    setOfflineData(data);
    localStorage.setItem('billing_data', JSON.stringify(data));
  };
  
  return [offlineData, updateOfflineData];
};
```

### **2. Push Notifications**
```javascript
// Register for push notifications
const registerForPushNotifications = async () => {
  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    // Register with your push service
    const token = await getPushToken();
    // Send token to your backend
    await api.post('/notifications/register/', { token });
  }
};
```

---

## 🚀 **Deployment Checklist**

- ✅ All APIs tested and working
- ✅ Authentication implemented
- ✅ Error handling complete
- ✅ Rate limiting configured
- ✅ CORS configured
- ✅ Database migrations ready
- ✅ Documentation complete
- ✅ Frontend integration guide ready

## 📞 **Support**

For frontend implementation support:
- Check the detailed API documentation files
- Review the test cases for expected behavior
- Use the provided error handling patterns
- Test with the provided sample data

**The API is production-ready and fully documented for frontend implementation!** 🎉
