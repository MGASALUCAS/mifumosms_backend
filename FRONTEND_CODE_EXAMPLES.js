// Frontend Code Examples - Updated for Backend Changes
// Copy these examples to your frontend code

// ===========================================
// 1. API CALL (api.ts)
// ===========================================

// OLD - Remove this
const submitSenderRequest_OLD = async (data) => {
  const response = await fetch('/api/messaging/sender-requests/submit/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      requested_sender_id: data.senderId,
      sample_content: data.sampleContent,
      business_justification: data.businessJustification // ❌ REMOVE
    })
  });
  return response.json();
};

// NEW - Use this
const submitSenderRequest = async (data) => {
  const response = await fetch('/api/messaging/sender-requests/submit/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      requested_sender_id: data.senderId,
      sample_content: data.sampleContent
    })
  });
  return response.json();
};

// ===========================================
// 2. REACT COMPONENT (SenderNames.tsx)
// ===========================================

import React, { useState } from 'react';

const SenderNames = () => {
  // OLD State - Remove businessJustification
  // const [businessJustification, setBusinessJustification] = useState(''); // ❌ REMOVE

  // NEW State - Only these two
  const [senderId, setSenderId] = useState('');
  const [sampleContent, setSampleContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form validation
  const validateForm = () => {
    if (!senderId.trim()) {
      setError('Sender ID is required');
      return false;
    }
    if (senderId.length > 11) {
      setError('Sender ID cannot exceed 11 characters');
      return false;
    }
    if (!sampleContent.trim()) {
      setError('Sample content is required');
      return false;
    }
    if (sampleContent.length > 170) {
      setError('Sample content cannot exceed 170 characters');
      return false;
    }
    return true;
  };

  // Form submission handler
  const handleRequestSenderName = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await submitSenderRequest({
        senderId: senderId.trim(),
        sampleContent: sampleContent.trim()
      });
      
      if (result.success) {
        // Success - clear form and show success message
        setSenderId('');
        setSampleContent('');
        alert('Sender ID request submitted successfully!');
        // Refresh the list or update UI
      } else {
        setError(result.message || 'Failed to submit request');
      }
    } catch (error) {
      setError('Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Request Sender ID</h2>
      
      {error && <div style={{color: 'red'}}>{error}</div>}
      
      <form onSubmit={handleRequestSenderName}>
        <div>
          <label>Sender ID (max 11 characters):</label>
          <input
            type="text"
            value={senderId}
            onChange={(e) => setSenderId(e.target.value)}
            maxLength={11}
            required
            disabled={loading}
          />
        </div>
        
        <div>
          <label>Sample Message (max 170 characters):</label>
          <textarea
            value={sampleContent}
            onChange={(e) => setSampleContent(e.target.value)}
            maxLength={170}
            required
            disabled={loading}
            rows={4}
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Request'}
        </button>
      </form>
    </div>
  );
};

export default SenderNames;

// ===========================================
// 3. STATS API CALL
// ===========================================

const getSenderRequestStats = async () => {
  try {
    const response = await fetch('/api/messaging/sender-requests/stats/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    
    if (data.success) {
      return data.data.stats;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
};

// ===========================================
// 4. LIST REQUESTS API CALL
// ===========================================

const getSenderRequests = async (page = 1, pageSize = 10) => {
  try {
    const response = await fetch(`/api/messaging/sender-requests/?page=${page}&page_size=${pageSize}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    
    if (data.success) {
      return data.data;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error('Error fetching requests:', error);
    return [];
  }
};

// ===========================================
// 5. USAGE EXAMPLE
// ===========================================

// In your component
const MyComponent = () => {
  const [stats, setStats] = useState(null);
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    // Load stats
    getSenderRequestStats().then(setStats);
    
    // Load requests
    getSenderRequests().then(setRequests);
  }, []);

  return (
    <div>
      {stats && (
        <div>
          <h3>Statistics</h3>
          <p>Total Requests: {stats.total_requests}</p>
          <p>Pending: {stats.pending_requests}</p>
          <p>Approved: {stats.approved_requests}</p>
        </div>
      )}
      
      <div>
        <h3>Recent Requests</h3>
        {requests.map(request => (
          <div key={request.id}>
            <strong>{request.requested_sender_id}</strong> - {request.status}
          </div>
        ))}
      </div>
    </div>
  );
};

// ===========================================
// 6. TEST DATA FOR TESTING
// ===========================================

const testData = {
  requested_sender_id: "TEST-SMS",
  sample_content: "This is a test message for validation."
};

// This should work with the updated backend
console.log('Test data:', testData);


