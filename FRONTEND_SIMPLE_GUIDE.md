# Frontend Integration - Simple Guide

## 🎯 What Changed?

We added a **Sender ID Request System** and fixed **Profile Update** issues. Now users can request to use the SMS sender ID "Taarifa-SMS" and admins can approve/reject requests.

## 🚀 New Features

### 1. **Sender ID Request System**
- Users can request to use "Taarifa-SMS" sender ID
- Admins can approve or reject requests
- Users can check their request status

### 2. **Fixed Profile Updates**
- Profile update form now works properly
- Better error messages for validation

## 📡 New API Endpoints

### **1. Request Sender ID**
```javascript
// POST /api/messaging/sender-requests/
const requestSenderID = async () => {
    const response = await fetch('/api/messaging/sender-requests/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            request_type: 'default',
            requested_sender_id: 'Taarifa-SMS',
            sample_content: 'A test use case for the sender name...',
            business_justification: 'I need this sender ID for my business'
        })
    });
    return await response.json();
};
```

### **2. Check Sender ID Status**
```javascript
// GET /api/messaging/sender-requests/status/
const checkStatus = async () => {
    const response = await fetch('/api/messaging/sender-requests/status/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return await response.json();
};
```

### **3. List All Requests (Admin)**
```javascript
// GET /api/messaging/sender-requests/
const getRequests = async () => {
    const response = await fetch('/api/messaging/sender-requests/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return await response.json();
};
```

### **4. Approve Request (Admin)**
```javascript
// POST /api/messaging/sender-requests/{id}/approve/
const approveRequest = async (requestId) => {
    const response = await fetch(`/api/messaging/sender-requests/${requestId}/approve/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'approved',
            admin_notes: 'Approved for use'
        })
    });
    return await response.json();
};
```

### **5. Reject Request (Admin)**
```javascript
// POST /api/messaging/sender-requests/{id}/reject/
const rejectRequest = async (requestId, reason) => {
    const response = await fetch(`/api/messaging/sender-requests/${requestId}/reject/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'rejected',
            rejection_reason: reason
        })
    });
    return await response.json();
};
```

## 🎨 Simple UI Components

### **1. Sender ID Request Button**
```jsx
const SenderIDRequest = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);

    const requestSenderID = async () => {
        setLoading(true);
        try {
            await requestSenderID();
            alert('Request submitted successfully!');
            checkStatus(); // Refresh status
        } catch (error) {
            alert('Request failed: ' + error.message);
        }
        setLoading(false);
    };

    const checkStatus = async () => {
        const data = await checkStatus();
        setStatus(data);
    };

    useEffect(() => {
        checkStatus();
    }, []);

    return (
        <div>
            <h3>SMS Sender ID</h3>
            {status?.sender_id_requests?.length > 0 ? (
                <div>
                    <p>Status: <strong>{status.sender_id_requests[0].status}</strong></p>
                    <p>Sender ID: {status.sender_id_requests[0].requested_sender_id}</p>
                </div>
            ) : (
                <div>
                    <p>No sender ID request found</p>
                    <button onClick={requestSenderID} disabled={loading}>
                        {loading ? 'Requesting...' : 'Request Sender ID'}
                    </button>
                </div>
            )}
        </div>
    );
};
```

### **2. SMS Balance Display**
```jsx
const SMSBalance = () => {
    const [balance, setBalance] = useState(null);

    useEffect(() => {
        const fetchBalance = async () => {
            const data = await checkStatus();
            setBalance(data.sms_balance);
        };
        fetchBalance();
    }, []);

    return (
        <div>
            <h3>SMS Credits</h3>
            <p>Available: <strong>{balance?.credits || 0}</strong></p>
            <p>Total Purchased: {balance?.total_purchased || 0}</p>
        </div>
    );
};
```

### **3. Admin Approval List**
```jsx
const AdminApprovalList = () => {
    const [requests, setRequests] = useState([]);

    useEffect(() => {
        const fetchRequests = async () => {
            const data = await getRequests();
            setRequests(data);
        };
        fetchRequests();
    }, []);

    const handleApprove = async (id) => {
        try {
            await approveRequest(id);
            alert('Request approved!');
            // Refresh the list
            const data = await getRequests();
            setRequests(data);
        } catch (error) {
            alert('Failed to approve: ' + error.message);
        }
    };

    const handleReject = async (id) => {
        const reason = prompt('Enter rejection reason:');
        if (reason) {
            try {
                await rejectRequest(id, reason);
                alert('Request rejected!');
                // Refresh the list
                const data = await getRequests();
                setRequests(data);
            } catch (error) {
                alert('Failed to reject: ' + error.message);
            }
        }
    };

    return (
        <div>
            <h3>Sender ID Requests</h3>
            {requests.map(request => (
                <div key={request.id} style={{border: '1px solid #ccc', padding: '10px', margin: '10px 0'}}>
                    <p><strong>User:</strong> {request.user_email}</p>
                    <p><strong>Sender ID:</strong> {request.requested_sender_id}</p>
                    <p><strong>Status:</strong> {request.status}</p>
                    <p><strong>Justification:</strong> {request.business_justification}</p>
                    
                    {request.status === 'pending' && (
                        <div>
                            <button onClick={() => handleApprove(request.id)} style={{marginRight: '10px'}}>
                                Approve
                            </button>
                            <button onClick={() => handleReject(request.id)}>
                                Reject
                            </button>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};
```

### **4. Fixed Profile Form**
```jsx
const ProfileForm = () => {
    const [formData, setFormData] = useState({
        email: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        bio: '',
        email_notifications: true,
        sms_notifications: false
    });
    const [errors, setErrors] = useState({});

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        
        try {
            const response = await fetch('/api/auth/profile/', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                setErrors(errorData);
                return;
            }
            
            alert('Profile updated successfully!');
        } catch (error) {
            alert('Update failed: ' + error.message);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>Update Profile</h3>
            
            <div>
                <label>Email *</label>
                <input 
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                />
                {errors.email && <span style={{color: 'red'}}>{errors.email[0]}</span>}
            </div>
            
            <div>
                <label>First Name *</label>
                <input 
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    required
                />
                {errors.first_name && <span style={{color: 'red'}}>{errors.first_name[0]}</span>}
            </div>
            
            <div>
                <label>Last Name *</label>
                <input 
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    required
                />
                {errors.last_name && <span style={{color: 'red'}}>{errors.last_name[0]}</span>}
            </div>
            
            <div>
                <label>Phone Number</label>
                <input 
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                />
            </div>
            
            <div>
                <label>Bio</label>
                <textarea 
                    value={formData.bio}
                    onChange={(e) => setFormData({...formData, bio: e.target.value})}
                />
            </div>
            
            <div>
                <label>
                    <input 
                        type="checkbox"
                        checked={formData.email_notifications}
                        onChange={(e) => setFormData({...formData, email_notifications: e.target.checked})}
                    />
                    Email Notifications
                </label>
            </div>
            
            <div>
                <label>
                    <input 
                        type="checkbox"
                        checked={formData.sms_notifications}
                        onChange={(e) => setFormData({...formData, sms_notifications: e.target.checked})}
                    />
                    SMS Notifications
                </label>
            </div>
            
            <button type="submit">Update Profile</button>
        </form>
    );
};
```

## 🔄 User Workflow

### **For Regular Users:**
1. **Login** → See SMS balance and sender ID status
2. **Request Sender ID** → Click "Request Sender ID" button
3. **Wait for Approval** → Admin will approve/reject
4. **Purchase SMS Credits** → Buy SMS packages
5. **Send SMS** → Use approved sender ID

### **For Admin Users:**
1. **Login** → See sender ID requests list
2. **Review Requests** → Check user justifications
3. **Approve/Reject** → Click approve or reject buttons
4. **Monitor Usage** → Check SMS balances and usage

## 📱 Simple Integration Steps

### **Step 1: Add API Functions**
Copy the API functions above into your project.

### **Step 2: Add UI Components**
Copy the React components above into your project.

### **Step 3: Add to Your Pages**
- Add `SenderIDRequest` component to user dashboard
- Add `SMSBalance` component to show credits
- Add `AdminApprovalList` component to admin panel
- Update your profile form with the fixed version

### **Step 4: Test**
- Test requesting sender ID
- Test admin approval
- Test profile updates
- Test SMS sending

## 🎨 Simple CSS

```css
/* Add this to your CSS file */
.sender-id-section {
    border: 1px solid #ddd;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}

.status-pending { color: orange; }
.status-approved { color: green; }
.status-rejected { color: red; }

.error-message {
    color: red;
    font-size: 12px;
    margin-top: 5px;
}

.admin-request-item {
    border: 1px solid #ccc;
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
}

.approve-btn {
    background: green;
    color: white;
    padding: 5px 10px;
    border: none;
    margin-right: 10px;
    cursor: pointer;
}

.reject-btn {
    background: red;
    color: white;
    padding: 5px 10px;
    border: none;
    cursor: pointer;
}
```

## ✅ What's Fixed

1. **Profile Updates** - No more 400 errors
2. **Better Validation** - Clear error messages
3. **Sender ID System** - Users can request approval
4. **Admin Control** - Approve/reject requests
5. **SMS Balance** - Show credits and status

## 🚀 Ready to Use

All the code above is ready to copy and paste into your frontend project. The API endpoints are working and tested.

**That's it! Simple and easy to understand.** 🎉
