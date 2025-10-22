# Custom SMS Purchase Frontend Integration Guide

## 🎯 Overview

This guide shows how to implement the custom SMS purchase feature as a **separate mechanism** from the regular SMS packages. Users can enter any amount starting from 100 SMS minimum, with real-time pricing calculation and validation.

## ✅ What's Already Implemented

### Backend Features
- ✅ Custom SMS purchase system with 100 SMS minimum validation
- ✅ Real-time pricing calculation with tier-based pricing
- ✅ Payment integration with ZenoPay
- ✅ Proper error handling and validation
- ✅ Custom packages removed from regular package list

### API Endpoints
- ✅ `POST /api/billing/payments/custom-sms/calculate/` - Real-time pricing
- ✅ `POST /api/billing/payments/custom-sms/initiate/` - Initiate purchase
- ✅ `GET /api/billing/payments/custom-sms/{purchase_id}/status/` - Check status

## 🚀 Frontend Implementation

### 1. Custom SMS Purchase Component

```javascript
// CustomSMSPurchase.jsx
import React, { useState, useEffect } from 'react';

const CustomSMSPurchase = ({ onPurchaseInitiated }) => {
  const [credits, setCredits] = useState('');
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [buyerInfo, setBuyerInfo] = useState({
    email: '',
    name: '',
    phone: ''
  });

  // Real-time pricing calculation
  const calculatePricing = async (creditsAmount) => {
    if (creditsAmount < 100) {
      setError('Minimum 100 SMS credits required');
      setPricing(null);
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/billing/payments/custom-sms/calculate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ credits: creditsAmount })
      });

      const data = await response.json();
      
      if (data.success) {
        setPricing(data.data);
      } else {
        setError(data.message || 'Failed to calculate pricing');
        setPricing(null);
      }
    } catch (err) {
      setError('Network error. Please try again.');
      setPricing(null);
    } finally {
      setLoading(false);
    }
  };

  // Handle credits input with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (credits && credits >= 100) {
        calculatePricing(parseInt(credits));
      } else if (credits && credits < 100) {
        setError('Minimum 100 SMS credits required');
        setPricing(null);
      } else {
        setError('');
        setPricing(null);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [credits]);

  // Handle purchase initiation
  const handlePurchase = async () => {
    if (!pricing) {
      setError('Please enter a valid amount');
      return;
    }

    if (!buyerInfo.email || !buyerInfo.name || !buyerInfo.phone) {
      setError('Please fill in all buyer information');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await fetch('/api/billing/payments/custom-sms/initiate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          credits: parseInt(credits),
          buyer_email: buyerInfo.email,
          buyer_name: buyerInfo.name,
          buyer_phone: buyerInfo.phone,
          mobile_money_provider: 'vodacom' // Default provider
        })
      });

      const data = await response.json();
      
      if (data.success) {
        onPurchaseInitiated(data.data);
        // Reset form
        setCredits('');
        setPricing(null);
        setBuyerInfo({ email: '', name: '', phone: '' });
      } else {
        setError(data.message || 'Purchase initiation failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="custom-sms-purchase">
      <h3>Or Enter Custom Amount</h3>
      
      {/* Credits Input */}
      <div className="form-group">
        <label htmlFor="credits">Number of SMS Credits</label>
        <input
          type="number"
          id="credits"
          value={credits}
          onChange={(e) => setCredits(e.target.value)}
          placeholder="e.g., 5000"
          min="100"
          className={error && credits < 100 ? 'error' : ''}
        />
        {credits && credits < 100 && (
          <div className="error-message">
            Minimum 100 credits required
          </div>
        )}
      </div>

      {/* Pricing Display */}
      {pricing && (
        <div className="pricing-display">
          <div className="pricing-info">
            <div className="tier-info">
              <span className="tier-name">{pricing.active_tier}</span>
              <span className="tier-range">
                ({pricing.tier_min_credits.toLocaleString()} - {pricing.tier_max_credits.toLocaleString()} credits)
              </span>
            </div>
            <div className="price-breakdown">
              <div className="unit-price">
                {pricing.credits.toLocaleString()} credits × {pricing.unit_price} TZS
              </div>
              <div className="total-price">
                Total: {pricing.total_price.toLocaleString()} TZS
              </div>
              {pricing.savings_percentage > 0 && (
                <div className="savings">
                  You save {pricing.savings_percentage}% compared to standard rate
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Buyer Information */}
      {pricing && (
        <div className="buyer-info">
          <h4>Buyer Information</h4>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                value={buyerInfo.email}
                onChange={(e) => setBuyerInfo({...buyerInfo, email: e.target.value})}
                placeholder="your@email.com"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                value={buyerInfo.name}
                onChange={(e) => setBuyerInfo({...buyerInfo, name: e.target.value})}
                placeholder="John Doe"
                required
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              id="phone"
              value={buyerInfo.phone}
              onChange={(e) => setBuyerInfo({...buyerInfo, phone: e.target.value})}
              placeholder="0744963858"
              pattern="^(07|06)\d{8}$"
              required
            />
            <small>Tanzanian mobile number (07XXXXXXXX or 06XXXXXXXX)</small>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Purchase Button */}
      {pricing && (
        <button
          onClick={handlePurchase}
          disabled={loading || !buyerInfo.email || !buyerInfo.name || !buyerInfo.phone}
          className="purchase-button"
        >
          {loading ? 'Processing...' : `Purchase ${pricing.credits.toLocaleString()} Credits`}
        </button>
      )}
    </div>
  );
};

export default CustomSMSPurchase;
```

### 2. CSS Styles

```css
/* CustomSMSPurchase.css */
.custom-sms-purchase {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 24px;
  margin-top: 24px;
}

.custom-sms-purchase h3 {
  margin: 0 0 20px 0;
  color: #495057;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #495057;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.15s ease-in-out;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-group input.error {
  border-color: #dc3545;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.pricing-display {
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
}

.tier-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tier-name {
  font-weight: 600;
  color: #007bff;
  font-size: 1.1rem;
}

.tier-range {
  color: #6c757d;
  font-size: 0.9rem;
}

.price-breakdown {
  border-top: 1px solid #e9ecef;
  padding-top: 12px;
}

.unit-price {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.total-price {
  font-size: 1.25rem;
  font-weight: 600;
  color: #28a745;
}

.savings {
  color: #fd7e14;
  font-size: 0.9rem;
  font-weight: 500;
  margin-top: 4px;
}

.buyer-info {
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
}

.buyer-info h4 {
  margin: 0 0 16px 0;
  color: #495057;
  font-size: 1.1rem;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 4px;
}

.purchase-button {
  width: 100%;
  background: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}

.purchase-button:hover:not(:disabled) {
  background: #218838;
}

.purchase-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

small {
  color: #6c757d;
  font-size: 0.8rem;
}
```

### 3. Integration with Main Package Selection

```javascript
// PackageSelection.jsx
import React, { useState } from 'react';
import CustomSMSPurchase from './CustomSMSPurchase';

const PackageSelection = () => {
  const [packages, setPackages] = useState([]);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [showCustomPurchase, setShowCustomPurchase] = useState(false);

  // Load regular packages (excluding custom)
  useEffect(() => {
    const loadPackages = async () => {
      try {
        const response = await fetch('/api/billing/sms/packages/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = await response.json();
        setPackages(data);
      } catch (error) {
        console.error('Failed to load packages:', error);
      }
    };
    loadPackages();
  }, []);

  const handleCustomPurchaseInitiated = (purchaseData) => {
    // Handle successful custom purchase initiation
    console.log('Custom purchase initiated:', purchaseData);
    // Redirect to payment page or show success message
  };

  return (
    <div className="package-selection">
      <h2>Choose a Package</h2>
      
      {/* Regular Packages Grid */}
      <div className="packages-grid">
        {packages.map(pkg => (
          <div 
            key={pkg.id} 
            className={`package-card ${pkg.is_popular ? 'popular' : ''}`}
            onClick={() => setSelectedPackage(pkg)}
          >
            {pkg.is_popular && <div className="popular-badge">Most Popular</div>}
            <h3>{pkg.name}</h3>
            <div className="price">{pkg.unit_price} TZS/SMS</div>
            <div className="credits">{pkg.credits.toLocaleString()} Credits</div>
            <div className="total-price">{pkg.price.toLocaleString()} TZS</div>
            <ul className="features">
              {pkg.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Custom Purchase Section */}
      <CustomSMSPurchase onPurchaseInitiated={handleCustomPurchaseInitiated} />
    </div>
  );
};

export default PackageSelection;
```

## 🔧 API Integration Examples

### 1. Calculate Pricing

```javascript
const calculateCustomPricing = async (credits) => {
  const response = await fetch('/api/billing/payments/custom-sms/calculate/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ credits })
  });
  
  return await response.json();
};

// Usage
const pricing = await calculateCustomPricing(5000);
console.log(pricing.data);
// {
//   credits: 5000,
//   unit_price: 30.00,
//   total_price: 150000.00,
//   active_tier: "Lite",
//   tier_min_credits: 1,
//   tier_max_credits: 4999,
//   savings_percentage: 0.0
// }
```

### 2. Initiate Purchase

```javascript
const initiateCustomPurchase = async (purchaseData) => {
  const response = await fetch('/api/billing/payments/custom-sms/initiate/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(purchaseData)
  });
  
  return await response.json();
};

// Usage
const result = await initiateCustomPurchase({
  credits: 5000,
  buyer_email: 'customer@example.com',
  buyer_name: 'John Doe',
  buyer_phone: '0744963858',
  mobile_money_provider: 'vodacom'
});
```

## 📱 Mobile Money Provider Options

```javascript
const MOBILE_MONEY_PROVIDERS = [
  { code: 'vodacom', name: 'Vodacom M-Pesa', icon: 'vodacom-icon' },
  { code: 'tigo', name: 'Tigo Pesa', icon: 'tigo-icon' },
  { code: 'airtel', name: 'Airtel Money', icon: 'airtel-icon' },
  { code: 'halotel', name: 'Halotel', icon: 'halotel-icon' }
];
```

## ✅ Validation Rules

### Credits Validation
- **Minimum**: 100 SMS credits
- **Maximum**: No limit (but consider practical limits)
- **Real-time validation**: Shows error immediately if below minimum

### Phone Number Validation
- **Format**: 07XXXXXXXX or 06XXXXXXXX (10 digits)
- **International**: 255XXXXXXXX (12 digits with country code)
- **Backend validation**: Server validates and converts to local format

### Email Validation
- **Format**: Standard email format
- **Required**: Must be provided for payment processing

## 🎨 UI/UX Best Practices

1. **Real-time Feedback**: Show pricing as user types
2. **Clear Error Messages**: Specific validation messages
3. **Loading States**: Show loading during API calls
4. **Responsive Design**: Works on mobile and desktop
5. **Accessibility**: Proper labels and keyboard navigation

## 🧪 Testing

### Test Custom Purchase Flow

```bash
# Test pricing calculation
curl -X POST https://mifumosms.servehttp.com/api/billing/payments/custom-sms/calculate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"credits": 5000}'

# Test purchase initiation
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

## 🚀 Deployment Checklist

- [ ] Remove any existing "Custom" packages from database
- [ ] Deploy backend changes
- [ ] Update frontend to use new custom purchase component
- [ ] Test pricing calculation endpoint
- [ ] Test purchase initiation endpoint
- [ ] Verify error handling works correctly
- [ ] Test on mobile devices

## 📋 Summary

The custom SMS purchase feature is now implemented as a **separate mechanism** from regular packages:

1. ✅ **Custom packages removed** from regular package list
2. ✅ **Real-time pricing calculation** with tier-based pricing
3. ✅ **100 SMS minimum validation** with clear error messages
4. ✅ **Complete payment integration** with ZenoPay
5. ✅ **Comprehensive frontend components** ready for integration

Users can now enter any amount starting from 100 SMS minimum, see real-time pricing, and complete their purchase through the custom purchase mechanism.
