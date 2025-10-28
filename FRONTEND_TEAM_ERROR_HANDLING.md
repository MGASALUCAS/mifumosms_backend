# Frontend Team Management Error Handling Guide

## Backend Error Message
```
Error: {'email': 'This user already has a pending invitation. You can resend the invitation instead.'}
```

Status: `400 Bad Request`

## Frontend Implementation

### 1. React Component Example

```tsx
import { useState } from 'react';

interface InviteMemberProps {
  teamId: string;
  onSuccess?: () => void;
}

export function InviteTeamMember({ teamId, onSuccess }: InviteMemberProps) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<'agent' | 'admin'>('agent');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(
        `/api/tenants/${teamId}/team/invite/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, role })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        // Handle different error types
        if (response.status === 400 && data.email) {
          const errorMessage = data.email;
          
          // Check for pending invitation error
          if (errorMessage.includes('pending invitation')) {
            const shouldResend = window.confirm(
              `${errorMessage}\n\nWould you like to resend the invitation now?`
            );
            
            if (shouldResend) {
              // Call resend invitation
              await handleResendInvitation(email, teamId);
            } else {
              setError(errorMessage);
            }
          }
          // Check for active member error
          else if (errorMessage.includes('already an active member')) {
            setError(`✅ ${errorMessage}`);
          }
          // Check for suspended member error
          else if (errorMessage.includes('suspended')) {
            const shouldActivate = window.confirm(
              `${errorMessage}\n\nWould you like to activate them now?`
            );
            
            if (shouldActivate) {
              // Call activate member
              await handleActivateMember(email, teamId);
            } else {
              setError(errorMessage);
            }
          }
          // Other errors
          else {
            setError(errorMessage);
          }
        } else {
          setError(data.detail || 'Failed to invite member');
        }
        return;
      }

      // Success
      setEmail('');
      onSuccess?.();
      alert('Member invited successfully!');
      
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get membership ID
  const getMembershipId = async (email: string, teamId: string) => {
    try {
      const response = await fetch(
        `/api/tenants/${teamId}/team/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      const members = await response.json();
      const member = members.find((m: any) => m.user_email === email);
      return member?.id;
    } catch (err) {
      return null;
    }
  };

  const handleResendInvitation = async (email: string, teamId: string) => {
    try {
      const membershipId = await getMembershipId(email, teamId);
      if (!membershipId) {
        setError('Could not find member to resend invitation');
        return;
      }

      const response = await fetch(
        `/api/tenants/${teamId}/team/${membershipId}/resend-invitation/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        alert('Invitation resent successfully!');
        onSuccess?.();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to resend invitation');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    }
  };

  const handleActivateMember = async (email: string, teamId: string) => {
    try {
      const membershipId = await getMembershipId(email, teamId);
      if (!membershipId) {
        setError('Could not find member to activate');
        return;
      }

      const response = await fetch(
        `/api/tenants/${teamId}/team/${membershipId}/activate/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        alert('Member activated successfully!');
        onSuccess?.();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to activate member');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    }
  };

  return (
    <form onSubmit={handleInvite}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div>
        <label>Role:</label>
        <select value={role} onChange={(e) => setRole(e.target.value as 'agent' | 'admin')}>
          <option value="agent">Agent</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <button type="submit" disabled={loading}>
        {loading ? 'Inviting...' : 'Invite Member'}
      </button>
    </form>
  );
}
```

### 2. Using React Query

```tsx
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

function useTeamMembers(tenantId: string) {
  return useQuery({
    queryKey: ['team', tenantId],
    queryFn: async () => {
      const response = await fetch(
        `/api/tenants/${tenantId}/team/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      if (!response.ok) throw new Error('Failed to fetch team members');
      return response.json();
    }
  });
}

function useInviteMember(tenantId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ email, role }: { email: string; role: string }) => {
      const response = await fetch(
        `/api/tenants/${tenantId}/team/invite/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, role })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        // Handle errors
        if (response.status === 400 && data.email) {
          throw new Error(data.email);
        }
        throw new Error(data.detail || 'Failed to invite member');
      }

      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team', tenantId] });
    }
  });
}

function useResendInvitation(tenantId: string, membershipId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await fetch(
        `/api/tenants/${tenantId}/team/${membershipId}/resend-invitation/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to resend invitation');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team', tenantId] });
    }
  });
}

// Usage in component
export function InviteTeamMember({ tenantId }: { tenantId: string }) {
  const { data: members } = useTeamMembers(tenantId);
  const inviteMutation = useInviteMember(tenantId);

  const handleInvite = async (email: string, role: string) => {
    try {
      await inviteMutation.mutateAsync({ email, role });
      alert('Member invited successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      if (errorMessage.includes('pending invitation')) {
        // Find the member and offer to resend
        const member = members?.find((m: any) => m.user_email === email);
        if (member) {
          const resendInvitation = useResendInvitation(tenantId, member.id);
          const shouldResend = window.confirm(
            `${errorMessage}\n\nWould you like to resend the invitation now?`
          );
          
          if (shouldResend) {
            await resendInvitation.mutateAsync();
          }
        }
      } else {
        alert(errorMessage);
      }
    }
  };

  return (
    // Your form component
  );
}
```

### 3. Simple JavaScript Version

```javascript
async function inviteTeamMember(tenantId, email, role) {
  try {
    const response = await fetch(
      `/api/tenants/${tenantId}/team/invite/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, role })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      // Handle error based on type
      if (response.status === 400 && data.email) {
        const errorMessage = data.email;

        if (errorMessage.includes('pending invitation')) {
          // Show user-friendly message with action
          const action = confirm(
            `This user already has a pending invitation.\n\n` +
            `Would you like to resend the invitation?`
          );

          if (action) {
            // Find and resend invitation
            const members = await fetchTeamMembers(tenantId);
            const member = members.find(m => m.user_email === email);
            if (member) {
              await resendInvitation(tenantId, member.id);
            }
          }
        } else {
          alert(errorMessage);
        }
      } else {
        alert(data.detail || 'Failed to invite member');
      }
      return;
    }

    // Success
    alert('Member invited successfully!');
    return data;

  } catch (error) {
    alert('An error occurred. Please try again.');
    console.error(error);
  }
}

async function fetchTeamMembers(tenantId) {
  const response = await fetch(
    `/api/tenants/${tenantId}/team/`,
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    }
  );
  return response.json();
}

async function resendInvitation(tenantId, membershipId) {
  const response = await fetch(
    `/api/tenants/${tenantId}/team/${membershipId}/resend-invitation/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    }
  );

  if (response.ok) {
    alert('Invitation resent successfully!');
  } else {
    const data = await response.json();
    alert(data.error || 'Failed to resend invitation');
  }
}
```

## Error Messages from Backend

### Pending Invitation
```json
{
  "email": "This user already has a pending invitation. You can resend the invitation instead."
}
```
**User Action**: Click "Resend Invitation" button

### Active Member
```json
{
  "email": "This user is already an active member with the role: Agent."
}
```
**User Action**: No action needed (informational)

### Suspended Member
```json
{
  "email": "This user's membership is suspended. You can activate them instead."
}
```
**User Action**: Click "Activate Member" button

## UI Recommendations

1. **Show clear error messages** instead of generic "Bad Request"
2. **Provide action buttons** for resend/activate options
3. **Auto-refresh team list** after successful operations
4. **Display member status** (active, pending, suspended) clearly
5. **Add confirmation dialogs** for destructive actions

## Summary

The backend now returns **actionable error messages**:
- ✅ Tells user what the problem is
- ✅ Suggests what they can do
- ✅ Provides specific guidance

The frontend should:
1. Parse these messages
2. Offer contextual actions (resend, activate)
3. Make it easy for users to fix issues

