# Custom SMS Purchase Feature Guide

## Overview
The Custom SMS Purchase feature allows users to buy SMS credits in any amount (minimum 100 SMS) with automatic pricing tier calculation. This provides flexibility for users who need specific amounts that don't match the predefined packages.

## Features

### ✅ **Flexible Credit Amounts**
- **Minimum**: 100 SMS credits
- **Maximum**: No limit (uses Enterprise+ pricing for large amounts)
- **Automatic Pricing**: Calculates unit price based on credit amount

### ✅ **Automatic Tier Calculation**
- **Lite Tier**: 1 - 5,000 SMS → 30 TZS per SMS
- **Standard Tier**: 5,001 - 50,000 SMS → 25 TZS per SMS  
- **Pro Tier**: 50,001 - 250,000 SMS → 18 TZS per SMS
- **Enterprise Tier**: 250,001 - 1,000,000 SMS → 12 TZS per SMS
- **Enterprise+ Tier**: 1,000,001+ SMS → 12 TZS per SMS

### ✅ **ZenoPay Integration**
- Full payment processing with ZenoPay
- Mobile money provider support (Vodacom, Tigo, Airtel, Halotel)
- Webhook support for payment confirmation
- Real-time payment status checking

## API Endpoints

### 1. Calculate Custom SMS Pricing
**POST** `/api/billing/payments/custom-sms/calculate/`

Calculate pricing for a custom SMS purchase without creating the purchase.

**Request Body:**
```json
{
    "credits": 5000
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "credits": 5000,
        "unit_price": 30.00,
        "total_price": 150000.00,
        "active_tier": "Lite",
        "tier_min_credits": 1,
        "tier_max_credits": 5000,
        "savings_percentage": 0.0
    }
}
```

### 2. Initiate Custom SMS Purchase
**POST** `/api/billing/payments/custom-sms/initiate/`

Create and initiate a custom SMS purchase with payment processing.

**Request Body:**
```json
{
    "credits": 5000,
    "buyer_email": "user@example.com",
    "buyer_name": "John Doe",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Custom SMS purchase initiated successfully. Please complete payment on your mobile device.",
    "data": {
        "purchase_id": "uuid",
        "transaction_id": "uuid",
        "order_id": "CUSTOM-20241018-ABC12345",
        "zenopay_order_id": "uuid",
        "invoice_number": "INV-20241018-DEF67890",
        "credits": 5000,
        "unit_price": 30.00,
        "total_price": 150000.00,
        "active_tier": "Lite",
        "tier_min_credits": 1,
        "tier_max_credits": 5000,
        "status": "processing",
        "mobile_money_provider": "vodacom",
        "provider_name": "Vodacom",
        "payment_instructions": "Request in progress. You will receive a callback shortly",
        "reference": "",
        "buyer": {
            "name": "John Doe",
            "email": "user@example.com",
            "phone": "0744963858"
        }
    }
}
```

### 3. Check Custom SMS Purchase Status
**GET** `/api/billing/payments/custom-sms/{purchase_id}/status/`

Check the status of a custom SMS purchase.

**Response:**
```json
{
    "success": true,
    "data": {
        "purchase_id": "uuid",
        "credits": 5000,
        "unit_price": 30.00,
        "total_price": 150000.00,
        "active_tier": "Lite",
        "status": "completed",
        "created_at": "2024-10-18T20:45:00Z",
        "updated_at": "2024-10-18T20:46:00Z",
        "completed_at": "2024-10-18T20:46:00Z"
    }
}
```

## Frontend Integration Example

### HTML Form
```html
<div class="custom-sms-purchase">
    <h3>Or Enter Custom Amount</h3>
    
    <div class="form-group">
        <label for="credits">Number of SMS Credits</label>
        <input type="number" id="credits" name="credits" min="100" placeholder="e.g., 5000" required>
        <small class="help-text">Minimum 100 SMS credits</small>
    </div>
    
    <div class="pricing-display" id="pricing-display" style="display: none;">
        <div class="tier-info">
            <span class="tier-name" id="tier-name">Lite</span>
            <span class="tier-range" id="tier-range">1 – 5,000 SMS</span>
            <span class="unit-price" id="unit-price">TZS 30/SMS</span>
        </div>
        <div class="total-cost">
            <strong>Total Cost: <span id="total-cost">TZS 150,000</span></strong>
        </div>
    </div>
    
    <button id="calculate-btn" type="button">Calculate Price</button>
    <button id="purchase-btn" type="button" style="display: none;">Purchase SMS Credits</button>
</div>
```

### JavaScript Integration
```javascript
// Calculate pricing when credits change
document.getElementById('credits').addEventListener('input', function() {
    const credits = parseInt(this.value);
    if (credits >= 100) {
        calculateCustomPricing(credits);
    } else {
        hidePricingDisplay();
    }
});

async function calculateCustomPricing(credits) {
    try {
        const response = await fetch('/api/billing/payments/custom-sms/calculate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({ credits: credits })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPricing(data.data);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Failed to calculate pricing');
    }
}

function displayPricing(pricing) {
    document.getElementById('tier-name').textContent = pricing.active_tier;
    document.getElementById('tier-range').textContent = 
        `${pricing.tier_min_credits.toLocaleString()} – ${pricing.tier_max_credits.toLocaleString()} SMS`;
    document.getElementById('unit-price').textContent = `TZS ${pricing.unit_price}/SMS`;
    document.getElementById('total-cost').textContent = `TZS ${pricing.total_price.toLocaleString()}`;
    
    document.getElementById('pricing-display').style.display = 'block';
    document.getElementById('purchase-btn').style.display = 'block';
}

async function initiateCustomPurchase() {
    const credits = parseInt(document.getElementById('credits').value);
    const buyerEmail = document.getElementById('buyer-email').value;
    const buyerName = document.getElementById('buyer-name').value;
    const buyerPhone = document.getElementById('buyer-phone').value;
    const provider = document.getElementById('mobile-provider').value;
    
    try {
        const response = await fetch('/api/billing/payments/custom-sms/initiate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({
                credits: credits,
                buyer_email: buyerEmail,
                buyer_name: buyerName,
                buyer_phone: buyerPhone,
                mobile_money_provider: provider
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to payment completion page
            window.location.href = `/payment-status/${data.data.purchase_id}`;
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Failed to initiate purchase');
    }
}
```

## Database Schema

### CustomSMSPurchase Model
```python
class CustomSMSPurchase(models.Model):
    id = models.UUIDField(primary_key=True)
    tenant = models.ForeignKey('tenants.Tenant')
    user = models.ForeignKey(User)
    
    # Purchase details
    credits = models.PositiveIntegerField()  # Minimum 100
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tier information
    active_tier = models.CharField(max_length=50)
    tier_min_credits = models.PositiveIntegerField()
    tier_max_credits = models.PositiveIntegerField()
    
    # Payment
    payment_transaction = models.OneToOneField('PaymentTransaction')
    status = models.CharField(max_length=20)  # pending, processing, completed, failed, cancelled
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

## Admin Interface

The custom SMS purchases are available in the Django admin interface:
- **Path**: `/admin/billing/customsmspurchase/`
- **Features**: List view, search, filtering, detailed view
- **Bulk Actions**: Mark as completed, mark as failed

## Pricing Examples

| Credits | Tier | Unit Price | Total Price | Savings |
|---------|------|------------|-------------|---------|
| 100 | Lite | 30 TZS | 3,000 TZS | 0% |
| 1,000 | Lite | 30 TZS | 30,000 TZS | 0% |
| 5,000 | Lite | 30 TZS | 150,000 TZS | 0% |
| 10,000 | Standard | 25 TZS | 250,000 TZS | 16.7% |
| 50,000 | Standard | 25 TZS | 1,250,000 TZS | 16.7% |
| 100,000 | Pro | 18 TZS | 1,800,000 TZS | 40% |
| 500,000 | Enterprise | 12 TZS | 6,000,000 TZS | 60% |
| 1,000,000 | Enterprise | 12 TZS | 12,000,000 TZS | 60% |

## Error Handling

### Validation Errors
- **Minimum Credits**: "Minimum 100 SMS credits required for custom purchase"
- **Invalid Phone**: "Please provide a valid Tanzanian mobile number (e.g., 0744963858)"
- **Missing Fields**: "Validation failed" with specific field errors

### Payment Errors
- **Payment Initiation Failed**: "Failed to initiate custom SMS purchase"
- **Payment Verification Failed**: "Payment verification failed"
- **Network Errors**: "Network error occurred. Please check your connection and try again"

## Security Features

- ✅ **Authentication Required**: All endpoints require valid authentication
- ✅ **Tenant Isolation**: Users can only access their own purchases
- ✅ **Input Validation**: Comprehensive validation for all inputs
- ✅ **Payment Verification**: Double verification with ZenoPay API
- ✅ **Webhook Security**: API key validation for webhooks

## Testing

### Test Custom Pricing Calculation
```bash
curl -X POST "http://localhost:8000/api/billing/payments/custom-sms/calculate/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"credits": 5000}'
```

### Test Custom Purchase Initiation
```bash
curl -X POST "http://localhost:8000/api/billing/payments/custom-sms/initiate/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "credits": 5000,
    "buyer_email": "test@example.com",
    "buyer_name": "Test User",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
  }'
```

## Support

For technical support or questions about custom SMS purchases:
1. Check the API response for specific error messages
2. Verify authentication and permissions
3. Ensure minimum 100 SMS credits requirement
4. Check ZenoPay API connectivity

---

*Last updated: October 2024*
