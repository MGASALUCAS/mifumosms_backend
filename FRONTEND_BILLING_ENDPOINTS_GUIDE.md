# Frontend Billing History Endpoints Guide

## Overview
This guide provides all the billing history endpoints available for the frontend, with examples and response structures.

## Base URL
```
http://127.0.0.1:8000/api/billing/
```

---

## 1. Comprehensive Transaction History (RECOMMENDED)

### Endpoint
```
GET /api/billing/history/comprehensive/
```

### Description
**Primary endpoint for professional billing history display.** Combines all transaction types (purchases, payments, custom SMS) with rich formatting, icons, and professional styling.

### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |
| `status` | string | - | Filter by status (pending, completed, failed, etc.) |
| `transaction_type` | string | - | Filter by type (purchase, payment, custom) |

### Example Request
```javascript
// Get first page with all transactions
fetch('/api/billing/history/comprehensive/?page=1&page_size=20')

// Get only completed purchases
fetch('/api/billing/history/comprehensive/?status=completed&transaction_type=purchase')

// Get payment transactions only
fetch('/api/billing/history/comprehensive/?transaction_type=payment')
```

### Response Structure
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "uuid",
        "type": "purchase",
        "type_display": "SMS Package Purchase",
        "invoice_number": "INV-123456",
        "amount": 50000.00,
        "currency": "TZS",
        "status": "completed",
        "status_display": "Completed",
        "payment_method": "mpesa",
        "payment_method_display": "M-Pesa",
        "credits": 2000,
        "package_name": "Standard Package",
        "unit_price": 25.00,
        "created_at": "2025-10-20T10:00:00Z",
        "completed_at": "2025-10-20T10:05:00Z",
        "description": "Purchased 2000 SMS credits from Standard Package",
        "icon": "📦",
        "color": "blue"
      }
    ],
    "summary": {
      "total_transactions": 17,
      "total_amount": 250000.00,
      "total_credits": 10000,
      "currency": "TZS"
    },
    "pagination": {
      "count": 17,
      "next": "?page=2&page_size=20",
      "previous": null,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  }
}
```

### Transaction Types
| Type | Icon | Color | Description |
|------|------|-------|-------------|
| `purchase` | 📦 | blue | SMS Package Purchases |
| `payment` | 💳 | green | Payment Transactions |
| `custom` | ⚙️ | purple | Custom SMS Purchases |

### Payment Status Mapping
**Simplified Status System** - Direct mapping from ZenoPay:
- **`pending`** - Payment initiated, waiting for user action
- **`completed`** - Payment successful, credits added
- **`failed`** - Payment failed or cancelled
- **`cancelled`** - Payment cancelled by user
- **`expired`** - Payment expired (timeout)
- **`refunded`** - Payment refunded

**Note**: The confusing "processing" status has been removed. All payments are now either "pending" (waiting), "completed" (successful), or "failed" (unsuccessful).

---

## 2. Purchase History (Legacy)

### Endpoint
```
GET /api/billing/history/purchases/
```

### Description
Legacy endpoint for SMS package purchases only. Use comprehensive endpoint instead.

### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |
| `status` | string | - | Filter by status |

### Example Request
```javascript
fetch('/api/billing/history/purchases/?page=1&page_size=20')
```

---

## 3. Payment History

### Endpoint
```
GET /api/billing/history/payments/
```

### Description
Get payment transaction history only.

### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |
| `status` | string | - | Filter by status |

### Example Request
```javascript
fetch('/api/billing/history/payments/?page=1&page_size=20')
```

---

## 4. Usage History

### Endpoint
```
GET /api/billing/history/usage/
```

### Description
Get SMS usage history and statistics.

### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |
| `start_date` | string | - | Start date (YYYY-MM-DD) |
| `end_date` | string | - | End date (YYYY-MM-DD) |

### Example Request
```javascript
fetch('/api/billing/history/usage/?page=1&page_size=20&start_date=2025-10-01&end_date=2025-10-31')
```

---

## 5. Billing Summary

### Endpoint
```
GET /api/billing/history/summary/
```

### Description
Get billing summary statistics and overview.

### Example Request
```javascript
fetch('/api/billing/history/summary/')
```

### Response Structure
```json
{
  "success": true,
  "data": {
    "total_spent": 250000.00,
    "total_credits": 10000,
    "active_packages": 3,
    "pending_payments": 1,
    "currency": "TZS"
  }
}
```

---

## Frontend Implementation Examples

### 1. React Component Example

```javascript
import React, { useState, useEffect } from 'react';

const BillingHistory = () => {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 20,
    status: '',
    transaction_type: ''
  });

  useEffect(() => {
    fetchBillingHistory();
  }, [filters]);

  const fetchBillingHistory = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams(filters);
      const response = await fetch(`/api/billing/history/comprehensive/?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setTransactions(data.data.transactions);
        setSummary(data.data.summary);
      }
    } catch (error) {
      console.error('Error fetching billing history:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderTransaction = (transaction) => (
    <div key={transaction.id} className={`transaction-card ${transaction.color}`}>
      <div className="transaction-icon">{transaction.icon}</div>
      <div className="transaction-details">
        <h3>{transaction.type_display}</h3>
        <p>{transaction.description}</p>
        <div className="transaction-meta">
          <span className="amount">{transaction.amount} {transaction.currency}</span>
          <span className={`status status-${transaction.status}`}>
            {transaction.status_display}
          </span>
          <span className="date">
            {new Date(transaction.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="billing-history">
      <div className="summary-cards">
        <div className="summary-card">
          <h3>Total Transactions</h3>
          <p>{summary.total_transactions}</p>
        </div>
        <div className="summary-card">
          <h3>Total Amount</h3>
          <p>{summary.total_amount} {summary.currency}</p>
        </div>
        <div className="summary-card">
          <h3>Total Credits</h3>
          <p>{summary.total_credits}</p>
        </div>
      </div>

      <div className="filters">
        <select 
          value={filters.transaction_type} 
          onChange={(e) => setFilters({...filters, transaction_type: e.target.value})}
        >
          <option value="">All Types</option>
          <option value="purchase">Purchases</option>
          <option value="payment">Payments</option>
          <option value="custom">Custom</option>
        </select>
        
        <select 
          value={filters.status} 
          onChange={(e) => setFilters({...filters, status: e.target.value})}
        >
          <option value="">All Status</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div className="transactions-list">
        {loading ? (
          <div>Loading...</div>
        ) : (
          transactions.map(renderTransaction)
        )}
      </div>
    </div>
  );
};

export default BillingHistory;
```

### 2. Vue.js Component Example

```vue
<template>
  <div class="billing-history">
    <div class="summary-cards">
      <div class="summary-card">
        <h3>Total Transactions</h3>
        <p>{{ summary.total_transactions }}</p>
      </div>
      <div class="summary-card">
        <h3>Total Amount</h3>
        <p>{{ summary.total_amount }} {{ summary.currency }}</p>
      </div>
      <div class="summary-card">
        <h3>Total Credits</h3>
        <p>{{ summary.total_credits }}</p>
      </div>
    </div>

    <div class="filters">
      <select v-model="filters.transaction_type">
        <option value="">All Types</option>
        <option value="purchase">Purchases</option>
        <option value="payment">Payments</option>
        <option value="custom">Custom</option>
      </select>
      
      <select v-model="filters.status">
        <option value="">All Status</option>
        <option value="completed">Completed</option>
        <option value="pending">Pending</option>
        <option value="failed">Failed</option>
      </select>
    </div>

    <div class="transactions-list">
      <div 
        v-for="transaction in transactions" 
        :key="transaction.id"
        :class="`transaction-card ${transaction.color}`"
      >
        <div class="transaction-icon">{{ transaction.icon }}</div>
        <div class="transaction-details">
          <h3>{{ transaction.type_display }}</h3>
          <p>{{ transaction.description }}</p>
          <div class="transaction-meta">
            <span class="amount">{{ transaction.amount }} {{ transaction.currency }}</span>
            <span :class="`status status-${transaction.status}`">
              {{ transaction.status_display }}
            </span>
            <span class="date">
              {{ formatDate(transaction.created_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      transactions: [],
      summary: {},
      loading: true,
      filters: {
        page: 1,
        page_size: 20,
        status: '',
        transaction_type: ''
      }
    }
  },
  watch: {
    filters: {
      handler() {
        this.fetchBillingHistory();
      },
      deep: true
    }
  },
  mounted() {
    this.fetchBillingHistory();
  },
  methods: {
    async fetchBillingHistory() {
      try {
        this.loading = true;
        const params = new URLSearchParams(this.filters);
        const response = await fetch(`/api/billing/history/comprehensive/?${params}`);
        const data = await response.json();
        
        if (data.success) {
          this.transactions = data.data.transactions;
          this.summary = data.data.summary;
        }
      } catch (error) {
        console.error('Error fetching billing history:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString();
    }
  }
}
</script>
```

### 3. Vanilla JavaScript Example

```javascript
class BillingHistory {
  constructor() {
    this.transactions = [];
    this.summary = {};
    this.filters = {
      page: 1,
      page_size: 20,
      status: '',
      transaction_type: ''
    };
    this.init();
  }

  async init() {
    await this.fetchBillingHistory();
    this.render();
    this.setupEventListeners();
  }

  async fetchBillingHistory() {
    try {
      const params = new URLSearchParams(this.filters);
      const response = await fetch(`/api/billing/history/comprehensive/?${params}`);
      const data = await response.json();
      
      if (data.success) {
        this.transactions = data.data.transactions;
        this.summary = data.data.summary;
      }
    } catch (error) {
      console.error('Error fetching billing history:', error);
    }
  }

  render() {
    const container = document.getElementById('billing-history');
    container.innerHTML = `
      <div class="summary-cards">
        <div class="summary-card">
          <h3>Total Transactions</h3>
          <p>${this.summary.total_transactions || 0}</p>
        </div>
        <div class="summary-card">
          <h3>Total Amount</h3>
          <p>${this.summary.total_amount || 0} ${this.summary.currency || 'TZS'}</p>
        </div>
        <div class="summary-card">
          <h3>Total Credits</h3>
          <p>${this.summary.total_credits || 0}</p>
        </div>
      </div>

      <div class="filters">
        <select id="transaction-type-filter">
          <option value="">All Types</option>
          <option value="purchase">Purchases</option>
          <option value="payment">Payments</option>
          <option value="custom">Custom</option>
        </select>
        
        <select id="status-filter">
          <option value="">All Status</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div class="transactions-list">
        ${this.transactions.map(transaction => this.renderTransaction(transaction)).join('')}
      </div>
    `;
  }

  renderTransaction(transaction) {
    return `
      <div class="transaction-card ${transaction.color}">
        <div class="transaction-icon">${transaction.icon}</div>
        <div class="transaction-details">
          <h3>${transaction.type_display}</h3>
          <p>${transaction.description}</p>
          <div class="transaction-meta">
            <span class="amount">${transaction.amount} ${transaction.currency}</span>
            <span class="status status-${transaction.status}">${transaction.status_display}</span>
            <span class="date">${new Date(transaction.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    document.getElementById('transaction-type-filter').addEventListener('change', (e) => {
      this.filters.transaction_type = e.target.value;
      this.fetchBillingHistory().then(() => this.render());
    });

    document.getElementById('status-filter').addEventListener('change', (e) => {
      this.filters.status = e.target.value;
      this.fetchBillingHistory().then(() => this.render());
    });
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new BillingHistory();
});
```

---

## CSS Styling Example

```css
.billing-history {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.summary-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
  text-transform: uppercase;
}

.summary-card p {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.transaction-card {
  display: flex;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid;
}

.transaction-card.blue { border-left-color: #3b82f6; }
.transaction-card.green { border-left-color: #10b981; }
.transaction-card.purple { border-left-color: #8b5cf6; }

.transaction-icon {
  font-size: 24px;
  margin-right: 15px;
}

.transaction-details {
  flex: 1;
}

.transaction-details h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.transaction-details p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.transaction-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.transaction-meta .amount {
  font-weight: bold;
  color: #333;
}

.transaction-meta .status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-completed { background: #d1fae5; color: #065f46; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-failed { background: #fee2e2; color: #991b1b; }

.transaction-meta .date {
  color: #666;
  font-size: 12px;
}
```

---

## Error Handling

```javascript
const handleApiError = (error, response) => {
  if (!response.ok) {
    switch (response.status) {
      case 400:
        console.error('Bad Request:', error.message);
        break;
      case 401:
        console.error('Unauthorized - Please login');
        break;
      case 403:
        console.error('Forbidden - Insufficient permissions');
        break;
      case 404:
        console.error('Not Found - Endpoint not available');
        break;
      case 500:
        console.error('Server Error - Please try again later');
        break;
      default:
        console.error('Unknown Error:', error.message);
    }
  }
};
```

---

## Authentication Headers

Make sure to include authentication headers in your requests:

```javascript
const fetchWithAuth = async (url, options = {}) => {
  const token = localStorage.getItem('authToken'); // or however you store tokens
  
  return fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
};

// Usage
const response = await fetchWithAuth('/api/billing/history/comprehensive/');
```

---

## Summary

**Primary Endpoint**: `/api/billing/history/comprehensive/`
- ✅ **Most comprehensive** - includes all transaction types
- ✅ **Professional formatting** - icons, colors, descriptions
- ✅ **Rich filtering** - by type, status, date
- ✅ **Summary statistics** - totals and counts
- ✅ **Pagination support** - for large datasets

Use this endpoint for the best user experience and most professional billing history display.
