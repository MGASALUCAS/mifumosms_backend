# Complete Mifumo SMS System Documentation

## 🎯 Overview
This comprehensive documentation covers the complete Mifumo SMS system, including custom SMS payments, message segment calculation, dashboard metrics, and frontend integration. Everything you need to run the system smoothly.

---

## 📱 Custom SMS Payment System

### Problem Solved
The 400 Bad Request error in custom SMS payments was caused by incomplete frontend data. The backend requires buyer information that wasn't being sent.

### ✅ Solution Implemented

#### Backend Requirements (Working Correctly)
- **Minimum Credits**: 100 SMS credits required
- **Message Segments**: 160 characters per segment, max 200 segments
- **Phone Validation**: Tanzanian mobile numbers (07XXXXXXXX, 06XXXXXXXX)
- **Required Fields**: credits, buyer_email, buyer_name, buyer_phone, mobile_money_provider

#### Frontend Fix Required
```javascript
// OLD CODE (causing 400 error)
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

// NEW CODE (correct implementation)
const initiateCustomPurchase = async (credits, paymentMethod, buyerInfo) => {
  const response = await fetch('/api/billing/payments/custom-sms/initiate/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      credits,
      mobile_money_provider: paymentMethod,
      buyer_email: buyerInfo.email,
      buyer_name: buyerInfo.name,
      buyer_phone: buyerInfo.phone
    })
  });
  return response.json();
};
```

#### Usage Example
```javascript
// Complete working example
const buyerInfo = {
  email: 'customer@example.com',
  name: 'John Doe',
  phone: '0744963858'  // Tanzanian format
};

const result = await initiateCustomPurchase(5000, 'vodacom', buyerInfo);
if (result.success) {
  console.log('Payment instructions:', result.data.payment_instructions);
} else {
  console.error('Error:', result.message);
}
```

---

## 📊 Dashboard Metrics Configuration

Based on your dashboard image, here are the exact metrics you want to display:

### Top-Level Metrics (4 Cards)
1. **Total Messages** - "Last 30 days"
2. **Active Contacts** - "Engaged this month" 
3. **Campaign Success** - "Delivery rate"
4. **Sender ID** - "Registered"

### API Endpoints for Dashboard
```javascript
// Get dashboard metrics
const getDashboardMetrics = async () => {
  const response = await fetch('/api/messaging/dashboard/metrics/', {
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};

// Expected response structure
{
  "success": true,
  "data": {
    "total_messages": {
      "value": 750,
      "change": "+12.5%",
      "change_type": "positive",
      "description": "Last 30 days"
    },
    "active_contacts": {
      "value": 450,
      "change": "+5.6%",
      "change_type": "positive", 
      "description": "Engaged this month"
    },
    "campaign_success": {
      "value": "94.2%",
      "change": "+2.1%",
      "change_type": "positive",
      "description": "Delivery rate"
    },
    "sender_ids": {
      "value": 3,
      "change": "+1",
      "change_type": "positive",
      "description": "Registered"
    }
  }
}
```

### Frontend Dashboard Implementation
```javascript
// Dashboard component implementation
const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await getDashboardMetrics();
        if (data.success) {
          setMetrics(data.data);
        }
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };
    
    fetchMetrics();
  }, []);
  
  if (!metrics) return <div>Loading...</div>;
  
  return (
    <div className="dashboard">
      <h1>Welcome to Mifumo WMS! 👋</h1>
      <p>Monitor your communication platform performance in real-time.</p>
      
      <div className="metrics-grid">
        <MetricCard
          title="Total Messages"
          value={metrics.total_messages.value}
          change={metrics.total_messages.change}
          description={metrics.total_messages.description}
        />
        <MetricCard
          title="Active Contacts"
          value={metrics.active_contacts.value}
          change={metrics.active_contacts.change}
          description={metrics.active_contacts.description}
        />
        <MetricCard
          title="Campaign Success"
          value={metrics.campaign_success.value}
          change={metrics.campaign_success.change}
          description={metrics.campaign_success.description}
        />
        <MetricCard
          title="Sender ID"
          value={metrics.sender_ids.value}
          change={metrics.sender_ids.change}
          description={metrics.sender_ids.description}
        />
      </div>
    </div>
  );
};
```

---

## 📝 Message Segment Calculation

### How It Works
- **Plain text only**: 160 characters per segment
- **Maximum segments**: 200 per message
- **Formula**: `(message_length + 159) // 160`

### Examples
- 1-160 characters = 1 SMS segment
- 161-320 characters = 2 SMS segments  
- 321-480 characters = 3 SMS segments
- 32,000 characters = 200 segments (maximum)

### Frontend Validation (Optional)
```javascript
function calculateSMSegments(message) {
  return Math.ceil(message.length / 160);
}

function validateMessageLength(message) {
  const segments = calculateSMSegments(message);
  if (segments > 200) {
    throw new Error(`Message too long. Requires ${segments} segments, maximum is 200.`);
  }
  return segments;
}
```

---

## 🔧 Complete API Integration

### Authentication
```javascript
// Get JWT token
const getAuthToken = async (email, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  return data.access_token;
};

// Set up API headers
const apiHeaders = {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
};
```

### SMS Sending
```javascript
const sendSMS = async (recipients, message, senderId) => {
  const response = await fetch('/api/messaging/sms/send/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      recipients,
      message,
      sender_id: senderId
    })
  });
  return response.json();
};
```

### Custom SMS Purchase
```javascript
const purchaseCustomSMS = async (credits, paymentMethod, buyerInfo) => {
  const response = await fetch('/api/billing/payments/custom-sms/initiate/', {
    method: 'POST',
    headers: apiHeaders,
    body: JSON.stringify({
      credits,
      mobile_money_provider: paymentMethod,
      buyer_email: buyerInfo.email,
      buyer_name: buyerInfo.name,
      buyer_phone: buyerInfo.phone
    })
  });
  return response.json();
};
```

---

## 🚨 Error Handling

### Common Error Responses
```javascript
// 400 Bad Request - Missing required fields
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "buyer_email": ["This field is required."],
    "buyer_name": ["This field is required."],
    "buyer_phone": ["This field is required."]
  }
}

// 400 Bad Request - Credits too low
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "credits": ["Minimum 100 SMS credits required for custom purchase."]
  }
}

// 400 Bad Request - Invalid phone
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "buyer_phone": ["Please provide a valid Tanzanian mobile number (e.g., 0744963858)"]
  }
}
```

### Frontend Error Handling
```javascript
const handleApiError = (error, response) => {
  if (response?.errors) {
    // Validation errors
    Object.keys(response.errors).forEach(field => {
      console.error(`${field}: ${response.errors[field][0]}`);
    });
  } else if (response?.message) {
    // General error message
    console.error(response.message);
  } else {
    // Network or other errors
    console.error('An unexpected error occurred:', error);
  }
};
```

---

## 🧪 Testing

### Test Custom SMS Purchase
```bash
curl -X POST https://mifumosms.servehttp.com/api/billing/payments/custom-sms/initiate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "credits": 5000,
    "buyer_email": "test@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
  }'
```

### Test Dashboard Metrics
```bash
curl -X GET https://mifumosms.servehttp.com/api/messaging/dashboard/metrics/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 📋 Quick Reference

### Required Frontend Changes
1. ✅ Update `initiateCustomPurchase` function to include buyer info
2. ✅ Add proper error handling for validation errors
3. ✅ Implement dashboard metrics display
4. ✅ Add message segment calculation (optional)

### Backend Status
- ✅ Custom SMS payment endpoint working
- ✅ Message segment calculation working
- ✅ Minimum 100 SMS validation working
- ✅ Phone number validation working
- ✅ Dashboard metrics API working

### Files Updated
- ✅ `FRONTEND_INTEGRATION_GUIDE.md` - Updated with correct function
- ✅ `BILLING_API_DOCUMENTATION.md` - Updated request format
- ✅ `CUSTOM_SMS_FRONTEND_FIX.md` - Complete fix guide
- ✅ `COMPLETE_SYSTEM_DOCUMENTATION.md` - This comprehensive guide

---

## 🎯 Next Steps

1. **Frontend Team**: Update the `initiateCustomPurchase` function with buyer information
2. **Frontend Team**: Implement dashboard metrics display as shown above
3. **Testing**: Test the custom SMS purchase flow end-to-end
4. **Deployment**: Deploy the updated frontend code

---

*This documentation provides everything needed to run the Mifumo SMS system smoothly. All backend functionality is working correctly - the only changes needed are on the frontend side.*
