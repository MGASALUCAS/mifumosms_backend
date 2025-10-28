# Frontend "No members yet" Fix

## The Problem
After refreshing the browser, frontend shows "No members yet" even though backend returns 2 members.

## Backend Status
✅ Backend is working - logs show:
```
Found 2 members
Serialized data: [
  {user_email: 'admin@mifumo.com', status: 'active'},
  {user_email: 'magesa133@gmail.com', status: 'pending'}
]
```

## Frontend Issues

### Issue 1: Not Fetching Team Members
Frontend might not be loading team members on component mount.

**Fix:**
```jsx
useEffect(() => {
  fetchTeamMembers(tenantId);
}, [tenantId]);

async function fetchTeamMembers(tenantId) {
  const response = await fetch(`/api/tenants/${tenantId}/team/`);
  const data = await response.json();
  setMembers(data);
}
```

### Issue 2: Filtering Out Pending Members
Frontend might be filtering and showing only 'active' members.

**Fix:**
```jsx
// WRONG - filters out pending
const activeMembers = members.filter(m => m.status === 'active');

// RIGHT - show all members
const allMembers = members; // Show all
const activeMembers = members.filter(m => m.status === 'active');
const pendingMembers = members.filter(m => m.status === 'pending');
```

### Issue 3: Wrong Tenant ID
Using wrong tenant ID or not passing it correctly.

**Fix:**
```jsx
// Make sure you're using the correct tenant ID
const tenantId = currentTenant?.id; // or from context
fetchTeamMembers(tenantId);
```

## Complete Working Example

```jsx
import { useState, useEffect } from 'react';

function TeamManagement() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const tenantId = 'e745958e-282d-45b8-9f3c-630509d28928'; // From your tenant context

  useEffect(() => {
    loadTeamMembers();
  }, []);

  const loadTeamMembers = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/tenants/${tenantId}/team/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load team members');
      }

      const data = await response.json();
      setMembers(data);
      setError(null);
    } catch (err) {
      setError('Failed to load team members');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  // Display all members (including pending)
  return (
    <div>
      <h2>Team Members ({members.length})</h2>
      
      {members.length === 0 ? (
        <p>No members yet</p>
      ) : (
        <ul>
          {members.map(member => (
            <li key={member.id}>
              <div>
                <strong>{member.user_name || member.user_email}</strong>
                <span className={`badge ${member.status}`}>
                  {member.status}
                </span>
                <span className="role">{member.role}</span>
              </div>
              {member.status === 'pending' && (
                <button onClick={() => resendInvitation(member.id)}>
                  Resend Invitation
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## Debug Steps

### 1. Check API Response
```javascript
// Add this to see what you're getting
console.log('Team members:', members);
console.log('Count:', members.length);

// Check each member
members.forEach(m => {
  console.log('Member:', m.user_email, 'Status:', m.status);
});
```

### 2. Check Tenant ID
```javascript
console.log('Current tenant ID:', tenantId);
console.log('API URL:', `/api/tenants/${tenantId}/team/`);
```

### 3. Check Filtering
```javascript
// Make sure you're not filtering incorrectly
const allMembers = members; // Should show all
const onlyActive = members.filter(m => m.status === 'active'); // Only active
```

## Common Causes

1. **Not calling API** on component mount
2. **Filtering members** incorrectly
3. **Using wrong tenant ID**
4. **Not handling pending members**
5. **State not updating** after refresh

## Quick Checklist

- [ ] API is being called on mount
- [ ] Using correct tenant ID
- [ ] Not filtering out pending members
- [ ] State is being set with API response
- [ ] Console shows correct member count

## The Real Fix

Replace your team loading logic with:

```jsx
const loadMembers = async () => {
  const response = await fetch(`/api/tenants/${tenantId}/team/`);
  const data = await response.json();
  
  console.log('Backend returned:', data.length, 'members');
  setMembers(data); // This should show all members including pending
};
```

And make sure you're not filtering:
```jsx
// Show ALL members (active + pending + suspended)
{members.map(m => <MemberCard key={m.id} member={m} />)}

// NOT this (which would hide pending):
{members.filter(m => m.status === 'active').map(...)}
```

