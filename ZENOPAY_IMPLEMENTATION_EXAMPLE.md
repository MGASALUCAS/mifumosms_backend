# ZenoPay Implementation Example

## Environment Variables Setup

Add these variables to your existing `.env` file:

```env
# ZenoPay Payment Gateway Configuration
ZENOPAY_API_KEY=your_zenopay_api_key_here
ZENOPAY_API_TIMEOUT=30
ZENOPAY_WEBHOOK_SECRET=your_webhook_secret_here

# Base URL for webhooks (update with your domain)
BASE_URL=http://localhost:8000
```

## Implementation Steps

### 1. Database Migration

```bash
# Create and run migrations for the new payment models
python manage.py makemigrations billing
python manage.py migrate
```

### 2. Test the Integration

```bash
# Run the test script to verify everything works
python test_zenopay_integration.py
```

### 3. Postman Testing

1. **Import Collection**: Import `ZenoPay_Payment_API.postman_collection.json`
2. **Import Environment**: Import `ZenoPay_Payment_Environment.postman_environment.json`
3. **Update Environment Variables**:
   - Set `base_url` to your server URL
   - Set `zenopay_api_key` to your actual API key
   - Update `buyer_email`, `buyer_name`, `buyer_phone` as needed

### 4. API Testing Flow

#### Step 1: Authentication
```http
POST {{base_url}}/api/auth/login/
Content-Type: application/json

{
    "email": "your_email@example.com",
    "password": "your_password"
}
```

#### Step 2: Get SMS Packages
```http
GET {{base_url}}/api/billing/sms/packages/
Authorization: Bearer {{jwt_token}}
```

#### Step 3: Initiate Payment
```http
POST {{base_url}}/api/billing/payments/initiate/
Content-Type: application/json
Authorization: Bearer {{jwt_token}}

{
    "package_id": "{{package_id}}",
    "buyer_email": "{{buyer_email}}",
    "buyer_name": "{{buyer_name}}",
    "buyer_phone": "{{buyer_phone}}"
}
```

#### Step 4: Check Payment Status
```http
GET {{base_url}}/api/billing/payments/transactions/{{transaction_id}}/status/
Authorization: Bearer {{jwt_token}}
```

#### Step 5: Simulate Webhook (for testing)
```http
POST {{base_url}}/api/billing/payments/webhook/
Content-Type: application/json
x-api-key: {{zenopay_api_key}}

{
    "order_id": "{{zenopay_order_id}}",
    "payment_status": "COMPLETED",
    "reference": "0936183435",
    "metadata": {
        "product": "SMS Credits",
        "amount": "1000"
    }
}
```

## Sample Implementation Code

### Frontend Integration Example (JavaScript)

```javascript
// Payment initiation
async function initiatePayment(packageId, buyerDetails) {
    try {
        const response = await fetch('/api/billing/payments/initiate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
            },
            body: JSON.stringify({
                package_id: packageId,
                ...buyerDetails
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show progress UI
            showPaymentProgress(data.data);
            
            // Start polling for status updates
            pollPaymentStatus(data.data.transaction_id);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Failed to initiate payment');
    }
}

// Progress tracking
function showPaymentProgress(paymentData) {
    const progress = paymentData.progress;
    
    // Update progress bar
    document.getElementById('progress-bar').style.width = `${progress.percentage}%`;
    
    // Update status text
    document.getElementById('current-step').textContent = progress.current_step;
    
    // Update status color
    document.getElementById('status-indicator').className = `status-${progress.status_color}`;
    
    // Show completed steps
    const completedSteps = document.getElementById('completed-steps');
    completedSteps.innerHTML = progress.completed_steps
        .map(step => `<div class="step completed">${step}</div>`)
        .join('');
    
    // Show remaining steps
    const remainingSteps = document.getElementById('remaining-steps');
    remainingSteps.innerHTML = progress.remaining_steps
        .map(step => `<div class="step pending">${step}</div>`)
        .join('');
}

// Status polling
function pollPaymentStatus(transactionId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/billing/payments/transactions/${transactionId}/status/`);
            const data = await response.json();
            
            if (data.success) {
                updateProgressUI(data.data.progress);
                
                if (data.data.status === 'completed' || data.data.status === 'failed') {
                    clearInterval(interval);
                }
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }, 5000); // Check every 5 seconds
}
```

### Backend Usage Example

```python
# In your views or services
from billing.zenopay_service import zenopay_service
from billing.models import PaymentTransaction, Purchase

def process_payment(package_id, buyer_details):
    # Create payment transaction
    transaction = PaymentTransaction.objects.create(
        tenant=request.user.tenant,
        user=request.user,
        zenopay_order_id=zenopay_service.generate_order_id(),
        order_id=f"MIFUMO-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
        invoice_number=f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
        amount=package.price,
        currency='TZS',
        buyer_email=buyer_details['email'],
        buyer_name=buyer_details['name'],
        buyer_phone=buyer_details['phone'],
        payment_method='zenopay_mobile_money',
        webhook_url=f"{settings.BASE_URL}/api/billing/payments/webhook/"
    )
    
    # Initiate payment with ZenoPay
    payment_response = zenopay_service.create_payment(
        order_id=transaction.zenopay_order_id,
        buyer_email=buyer_details['email'],
        buyer_name=buyer_details['name'],
        buyer_phone=buyer_details['phone'],
        amount=package.price,
        webhook_url=transaction.webhook_url
    )
    
    if payment_response['success']:
        return {
            'success': True,
            'transaction_id': str(transaction.id),
            'progress': get_payment_progress(transaction)
        }
    else:
        transaction.mark_as_failed(payment_response.get('error'))
        return {
            'success': False,
            'error': payment_response.get('error')
        }
```

## Testing Checklist

### ✅ Pre-Implementation
- [ ] Add ZenoPay variables to `.env` file
- [ ] Run database migrations
- [ ] Test with Python script
- [ ] Verify API key works

### ✅ Postman Testing
- [ ] Import collection and environment
- [ ] Update environment variables
- [ ] Test authentication flow
- [ ] Test payment initiation
- [ ] Test status checking
- [ ] Test webhook simulation

### ✅ Production Ready
- [ ] Use production ZenoPay API key
- [ ] Configure HTTPS webhook URL
- [ ] Set up monitoring
- [ ] Test with real mobile payments

## Common Issues & Solutions

### Issue: "ZenoPay API key not configured"
**Solution**: Add `ZENOPAY_API_KEY=your_key_here` to your `.env` file

### Issue: "Webhook URL not accessible"
**Solution**: Update `BASE_URL` in `.env` to your public domain

### Issue: "Phone number validation failed"
**Solution**: Use format `0744963858` or `255744963858`

### Issue: "Transaction not found"
**Solution**: Ensure you're using the correct transaction ID from the initiate payment response

## Next Steps

1. **Add to .env**: Copy the environment variables above
2. **Run Migrations**: `python manage.py migrate`
3. **Test Integration**: Use the provided Postman collection
4. **Deploy**: Update webhook URL for production
5. **Monitor**: Check logs for any issues

The integration is ready to use once you add the environment variables to your `.env` file!
