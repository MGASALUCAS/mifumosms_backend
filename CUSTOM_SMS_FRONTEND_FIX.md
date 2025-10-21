# Custom SMS Payment Frontend Fix

## Issue Analysis

The 400 Bad Request error occurs because the frontend is sending incomplete data to the custom SMS payment initiation endpoint.

### Current Frontend Code (INCORRECT):
```javascript
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

### Required Backend Fields:
The endpoint requires these fields:
- `credits` (integer, minimum 100)
- `buyer_email` (string, valid email)
- `buyer_name` (string, max 100 characters)
- `buyer_phone` (string, Tanzanian mobile number)
- `mobile_money_provider` (string, optional, default: 'vodacom')

## Solution

### 1. Update Frontend Function
```javascript
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

### 2. Usage Example
```javascript
// Example usage
const buyerInfo = {
  email: 'customer@example.com',
  name: 'John Doe',
  phone: '0744963858'  // Tanzanian format: 07XXXXXXXX or 06XXXXXXXX
};

const result = await initiateCustomPurchase(5000, 'vodacom', buyerInfo);
```

### 3. Phone Number Validation
The backend validates Tanzanian mobile numbers in these formats:
- `07XXXXXXXX` (10 digits starting with 07 or 06)
- `255XXXXXXXX` (12 digits with country code)
- International format `+255XXXXXXXX` is also accepted

### 4. Minimum Credits Validation
- Minimum 100 SMS credits required
- No maximum limit (but consider practical limits)

## Message Segment Information

### How SMS Segments Work:
- **Plain text only**: 160 characters per segment
- **Maximum segments**: 200 per message
- **Calculation**: `(message_length + 159) // 160`

### Example:
- 1-160 characters = 1 SMS segment
- 161-320 characters = 2 SMS segments
- 321-480 characters = 3 SMS segments
- And so on...

### Frontend Validation (Optional):
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

## Complete Working Example

```javascript
// Complete custom SMS purchase flow
async function purchaseCustomSMS(credits, paymentMethod, buyerInfo) {
  try {
    // Validate credits
    if (credits < 100) {
      throw new Error('Minimum 100 SMS credits required');
    }
    
    // Validate phone number format
    const phoneRegex = /^(07|06)\d{8}$|^255(07|06)\d{8}$/;
    if (!phoneRegex.test(buyerInfo.phone)) {
      throw new Error('Please provide a valid Tanzanian mobile number');
    }
    
    // Initiate purchase
    const result = await initiateCustomPurchase(credits, paymentMethod, buyerInfo);
    
    if (result.success) {
      console.log('Purchase initiated:', result.data);
      // Show payment instructions to user
      return result.data;
    } else {
      throw new Error(result.message || 'Purchase initiation failed');
    }
  } catch (error) {
    console.error('Purchase error:', error);
    throw error;
  }
}

// Usage
const buyerInfo = {
  email: 'customer@example.com',
  name: 'John Doe',
  phone: '0744963858'
};

purchaseCustomSMS(5000, 'vodacom', buyerInfo)
  .then(data => {
    console.log('Payment instructions:', data.payment_instructions);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

## Error Handling

The endpoint returns these error responses:

### 400 Bad Request (Validation Error):
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "buyer_email": ["This field is required."],
    "buyer_name": ["This field is required."],
    "buyer_phone": ["This field is required."]
  }
}
```

### 400 Bad Request (Credits Too Low):
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "credits": ["Minimum 100 SMS credits required for custom purchase."]
  }
}
```

### 400 Bad Request (Invalid Phone):
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "buyer_phone": ["Please provide a valid Tanzanian mobile number (e.g., 0744963858)"]
  }
}
```

## Testing

Test with this complete request:
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

This should return a 201 Created response with payment instructions.

