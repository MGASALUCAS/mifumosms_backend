# Complete Frontend JSON Scripts for Sender Name Requests

## 🚀 **Ready-to-Use JSON Scripts for Frontend Integration**

### **1. Authentication Scripts**

#### Login Request:
```javascript
// POST /api/auth/login/
const loginData = {
    "email": "user@example.com",
    "password": "password123"
};

fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        localStorage.setItem('accessToken', data.tokens.access);
        localStorage.setItem('refreshToken', data.tokens.refresh);
        console.log('Login successful:', data.user);
    } else {
        console.error('Login failed:', data.message);
    }
});
```

#### Login Success Response:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "is_active": true
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

### **2. Submit Sender Name Request Scripts**

#### Submit Request with FormData:
```javascript
// POST /api/messaging/sender-requests/submit/
function submitSenderRequest() {
    const formData = new FormData();
    formData.append('sender_name', 'MYCOMPANY');
    formData.append('use_case', 'This sender name will be used for customer notifications and marketing messages');

    // Add files if any
    const fileInput = document.getElementById('fileInput');
    for (let file of fileInput.files) {
        formData.append('supporting_documents', file);
    }

    fetch('http://127.0.0.1:8000/api/messaging/sender-requests/submit/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Request submitted:', data.data);
            // Update UI with success message
        } else {
            console.error('Submit failed:', data.message);
            // Show error message
        }
    });
}
```

#### Submit Success Response:
```json
{
  "success": true,
  "message": "Sender name request submitted successfully",
  "data": {
    "id": "69dfee8f-b470-4220-aaa2-5e472b130653",
    "sender_name": "MYCOMPANY",
    "use_case": "This sender name will be used for customer notifications",
    "status": "pending",
    "supporting_documents": [],
    "supporting_documents_count": 0,
    "created_at": "2025-10-13T22:30:00.000000Z",
    "updated_at": "2025-10-13T22:30:00.000000Z",
    "created_by": {
      "id": 1,
      "email": "admin2@mifumo.com",
      "first_name": "Admin",
      "last_name": "Mgasa"
    },
    "tenant": {
      "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
      "name": "Mifumo Admin"
    }
  }
}
```

#### Submit Validation Error Response:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "sender_name": [
      "Sender name must contain only alphanumeric characters",
      "Ensure this field has no more than 11 characters."
    ],
    "use_case": [
      "Use case description must be at least 10 characters long"
    ]
  }
}
```

---

### **3. List User Requests Scripts**

#### Get User Requests:
```javascript
// GET /api/messaging/sender-requests/
function loadUserRequests(page = 1, status = null) {
    let url = `http://127.0.0.1:8000/api/messaging/sender-requests/?page=${page}`;
    if (status) url += `&status=${status}`;

    fetch(url, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Requests loaded:', data.data.results);
            displayRequests(data.data.results);
            updatePagination(data.data);
        } else {
            console.error('Load failed:', data.message);
        }
    });
}
```

#### List Success Response:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "69dfee8f-b470-4220-aaa2-5e472b130653",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications",
        "status": "pending",
        "supporting_documents_count": 0,
        "created_at": "2025-10-13T22:30:00.000000Z",
        "created_by": {
          "id": 1,
          "email": "admin2@mifumo.com",
          "first_name": "Admin",
          "last_name": "Mgasa"
        }
      }
    ],
    "count": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

### **4. Statistics Scripts**

#### Get Statistics:
```javascript
// GET /api/messaging/sender-requests/stats/
function loadStatistics() {
    fetch('http://127.0.0.1:8000/api/messaging/sender-requests/stats/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Statistics:', data.data);
            displayStatistics(data.data);
        } else {
            console.error('Stats failed:', data.message);
        }
    });
}
```

#### Statistics Success Response:
```json
{
  "success": true,
  "data": {
    "total_requests": 8,
    "pending_requests": 6,
    "approved_requests": 1,
    "rejected_requests": 1,
    "requires_changes_requests": 0,
    "recent_activity": {
      "last_7_days": 2,
      "last_30_days": 8
    }
  }
}
```

---

### **5. Admin Dashboard Scripts**

#### Get Admin Dashboard:
```javascript
// GET /api/messaging/sender-requests/admin/dashboard/
function loadAdminDashboard() {
    fetch('http://127.0.0.1:8000/api/messaging/sender-requests/admin/dashboard/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Admin dashboard:', data.data);
            displayAdminDashboard(data.data);
        } else {
            console.error('Admin dashboard failed:', data.message);
        }
    });
}
```

#### Admin Dashboard Success Response:
```json
{
  "success": true,
  "data": {
    "stats": {
      "total_requests": 8,
      "pending_requests": 6,
      "approved_requests": 1,
      "rejected_requests": 1,
      "requires_changes_requests": 0
    },
    "recent_requests": [
      {
        "id": "69dfee8f-b470-4220-aaa2-5e472b130653",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications",
        "status": "pending",
        "created_at": "2025-10-13T22:30:00.000000Z",
        "created_by": {
          "id": 1,
          "email": "admin2@mifumo.com",
          "first_name": "Admin",
          "last_name": "Mgasa"
        }
      }
    ],
    "pending_requests": [
      {
        "id": "69dfee8f-b470-4220-aaa2-5e472b130653",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications",
        "status": "pending",
        "created_at": "2025-10-13T22:30:00.000000Z",
        "created_by": {
          "id": 1,
          "email": "admin2@mifumo.com",
          "first_name": "Admin",
          "last_name": "Mgasa"
        }
      }
    ],
    "tenant_name": "Mifumo Admin",
    "admin_user": "admin2@mifumo.com"
  }
}
```

---

### **6. Complete API Class for Frontend**

```javascript
class SenderRequestsAPI {
    constructor(baseURL = 'http://127.0.0.1:8000/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('accessToken');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('accessToken', token);
    }

    getHeaders(includeContentType = true) {
        const headers = {
            'Authorization': `Bearer ${this.token}`
        };

        if (includeContentType) {
            headers['Content-Type'] = 'application/json';
        }

        return headers;
    }

    async handleResponse(response) {
        const data = await response.json();

        if (response.ok) {
            return { success: true, data: data.data || data, message: data.message };
        } else {
            return {
                success: false,
                message: data.message || data.detail || 'An error occurred',
                errors: data.errors || null
            };
        }
    }

    // Submit Sender Name Request
    async submitRequest(formData) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/submit/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }

    // Get User Requests
    async getRequests(page = 1, status = null, search = null) {
        try {
            let url = `${this.baseURL}/messaging/sender-requests/?page=${page}`;

            if (status) url += `&status=${status}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;

            const response = await fetch(url, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }

    // Get Statistics
    async getStatistics() {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/stats/`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }

    // Get Admin Dashboard
    async getAdminDashboard() {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/admin/dashboard/`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }

    // Get Request Details
    async getRequestDetails(requestId) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/${requestId}/`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }

    // Update Request
    async updateRequest(requestId, updateData) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/${requestId}/update/`, {
                method: 'PUT',
                headers: this.getHeaders(),
                body: JSON.stringify(updateData)
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }

    // Delete Request
    async deleteRequest(requestId) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/${requestId}/delete/`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return { success: false, message: 'Network error: ' + error.message };
        }
    }
}

// Initialize the API
const senderRequestsAPI = new SenderRequestsAPI();
```

---

### **7. Frontend Usage Examples**

```javascript
// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    const token = localStorage.getItem('accessToken');
    if (token) {
        senderRequestsAPI.setToken(token);
        loadUserRequests();
        loadStatistics();
    } else {
        // Redirect to login or show login form
        console.log('User not authenticated');
    }
});

// Submit new request
async function submitNewRequest() {
    const formData = new FormData();
    formData.append('sender_name', document.getElementById('senderName').value);
    formData.append('use_case', document.getElementById('useCase').value);

    // Add files
    const fileInput = document.getElementById('fileInput');
    for (let file of fileInput.files) {
        formData.append('supporting_documents', file);
    }

    const result = await senderRequestsAPI.submitRequest(formData);

    if (result.success) {
        alert('Request submitted successfully!');
        loadUserRequests(); // Refresh the list
    } else {
        alert('Error: ' + result.message);
    }
}

// Load user requests
async function loadUserRequests() {
    const result = await senderRequestsAPI.getRequests();

    if (result.success) {
        displayRequests(result.data.results);
    } else {
        console.error('Error loading requests:', result.message);
    }
}

// Load statistics
async function loadStatistics() {
    const result = await senderRequestsAPI.getStatistics();

    if (result.success) {
        displayStatistics(result.data);
    } else {
        console.error('Error loading statistics:', result.message);
    }
}

// Display requests in UI
function displayRequests(requests) {
    const container = document.getElementById('requestsList');
    if (!container) return;

    if (requests.length === 0) {
        container.innerHTML = '<p>No requests found</p>';
        return;
    }

    const html = requests.map(request => `
        <div class="request-item">
            <h3>${request.sender_name}</h3>
            <p class="status-${request.status}">${request.status}</p>
            <p>${request.use_case.substring(0, 100)}...</p>
            <p>Created: ${new Date(request.created_at).toLocaleDateString()}</p>
            <button onclick="viewRequest('${request.id}')">View Details</button>
        </div>
    `).join('');

    container.innerHTML = html;
}

// Display statistics in UI
function displayStatistics(stats) {
    const container = document.getElementById('statsContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="stat-item">
            <h3>${stats.total_requests}</h3>
            <p>Total Requests</p>
        </div>
        <div class="stat-item">
            <h3>${stats.pending_requests}</h3>
            <p>Pending</p>
        </div>
        <div class="stat-item">
            <h3>${stats.approved_requests}</h3>
            <p>Approved</p>
        </div>
        <div class="stat-item">
            <h3>${stats.rejected_requests}</h3>
            <p>Rejected</p>
        </div>
    `;
}
```

---

### **8. Status Badge CSS**

```css
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-pending {
    background: #fef3c7;
    color: #d97706;
}

.status-approved {
    background: #d1fae5;
    color: #059669;
}

.status-rejected {
    background: #fee2e2;
    color: #dc2626;
}

.status-requires-changes {
    background: #e0e7ff;
    color: #3730a3;
}
```

---

## 🎯 **Summary**

These JSON scripts provide everything you need to integrate sender name requests into your frontend:

✅ **Complete API calls** with proper authentication
✅ **All JSON responses** for every endpoint
✅ **Error handling** for all scenarios
✅ **File upload support** with FormData
✅ **Status management** with color-coded badges
✅ **Pagination support** for large lists
✅ **Admin dashboard** functionality
✅ **Statistics display** with visual cards

The API is fully functional and tested - all users can submit sender name requests! 🚀
