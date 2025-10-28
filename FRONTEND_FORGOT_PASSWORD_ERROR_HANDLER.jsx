/**
 * Frontend Error Handler for Forgot Password SMS
 * 
 * Copy this code into your frontend forgot password component.
 * Replace the admin contact information with your actual details.
 */

import React, { useState } from 'react';

const ForgotPasswordForm = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/auth/sms/forgot-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone_number: phoneNumber
        })
      });

      const data = await response.json();

      // Check if the request was successful
      if (!response.ok || !data.success) {
        // Handle insufficient balance error
        if (data.error_code === 102 || data.error?.includes('balance')) {
          // Show user-friendly message
          alert(
            'SMS Service Temporarily Unavailable\n\n' +
            'We are currently unable to send SMS messages. ' +
            'Please contact the administrator for assistance.\n\n' +
            '📧 Email: admin@mifumosms.com\n' +
            '📞 Phone: +255 XXX XXX XXX\n' +
            '🕐 Support Hours: Monday-Friday, 9:00 AM - 5:00 PM'
          );
          
          // You can also use toast notification here
          // toast.error('SMS service unavailable. Please contact admin.');
          return;
        }

        // Handle other errors (phone not found, network error, etc.)
        let errorMessage = data.error || 'Failed to send password reset code.';
        
        // Make error messages more user-friendly
        if (errorMessage.includes('No account found')) {
          errorMessage = 'No account found with this phone number. Please check and try again.';
        }
        
        alert(errorMessage);
        return;
      }

      // Success - show success message
      alert('✅ Password reset code has been sent to your phone number. Please check your messages.');
      
      // Optional: Redirect to verification page
      // window.location.href = '/verify-code';
      
    } catch (error) {
      console.error('Error:', error);
      alert('Network error. Please check your internet connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-form">
      <h2>Forgot Password</h2>
      <p>Enter your phone number to receive a password reset code.</p>
      
      <form onSubmit={handleForgotPassword}>
        <input
          type="tel"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
          placeholder="+255 XXX XXX XXX"
          required
          disabled={loading}
        />
        
        <button 
          type="submit" 
          disabled={loading || !phoneNumber}
        >
          {loading ? 'Sending...' : 'Send Reset Code'}
        </button>
      </form>

      <div className="help-text">
        <p>Having trouble? Contact support:</p>
        <p>
          📧 <a href="mailto:admin@mifumosms.com">admin@mifumosms.com</a><br/>
          📞 <a href="tel:+255XXXXXXXXX">+255 XXX XXX XXX</a>
        </p>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;

/**
 * USAGE INSTRUCTIONS:
 * 
 * 1. Replace admin contact information:
 *    - Change: admin@mifumosms.com → your-admin-email@domain.com
 *    - Change: +255 XXX XXX XXX → your-phone-number
 * 
 * 2. If you're using a UI library (Ant Design, Material-UI, etc.):
 *    Replace 'alert()' with your library's notification component:
 * 
 *    Example with Ant Design:
 *    import { notification } from 'antd';
 *    notification.error({ message: 'Title', description: 'Description' });
 * 
 * 3. If you're using Toast notifications:
 *    Replace 'alert()' with toast.error() or toast.success()
 * 
 * 4. Add this CSS for styling:
 *    .forgot-password-form { max-width: 400px; margin: 0 auto; padding: 20px; }
 */

