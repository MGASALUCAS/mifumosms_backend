# SMS Provider Management in Admin Panel

## Overview

The admin panel now provides an easy interface to manage SMS providers. You can:
- View all SMS providers with their balance status
- Test connections to providers
- Set a provider as default
- Activate/deactivate providers
- Check balance automatically

## Accessing the Admin Panel

1. Navigate to: `http://localhost:8000/admin/`
2. Go to **Messaging** section
3. Click on **SMS Providers**

## Features

### 1. View Provider Status

The SMS Provider list shows:
- **Name**: Provider name
- **Type**: Beem Africa, Twilio, Africa's Talking, etc.
- **Tenant**: Which tenant owns this provider
- **Active Status**: Whether the provider is active
- **Default**: Whether this is the default provider
- **Balance**: Real-time balance check
- **Cost**: Cost per SMS
- **Currency**: Currency used

### 2. Balance Status

The admin automatically checks SMS balance for each provider:
- ✅ **Green badge**: Balance available (shows amount)
- ❌ **Red badge**: Error checking balance (shows error message)
- ⚠️ **Yellow badge**: Balance check failed
- ℹ️ **Blue badge**: Not a Beem provider (balance check not supported)

### 3. Setting Default Provider

**To set a provider as default:**

#### Method 1: Using the Actions dropdown
1. Select the provider(s) you want to set as default
2. Choose **"Set as default provider"** from the Actions dropdown
3. Click **Go**

#### Method 2: When editing
1. Click on a provider to edit it
2. Check the **"Is default"** checkbox
3. Save

**Note:** Setting a provider as default automatically:
- Activates the provider
- Removes default status from other providers in the same tenant

### 4. Testing Connections

**To test provider connections:**

#### Method 1: Batch testing (multiple providers)
1. Select one or more providers
2. Choose **"Test connections for selected providers"** from Actions
3. Click **Go**
4. View results

#### Method 2: Individual testing
1. Click on a provider to edit
2. Scroll to **"Provider Status"** section
3. Click **"Test Connection"** button

### 5. Activating/Deactivating Providers

**To activate providers:**
1. Select provider(s)
2. Choose **"Activate selected providers"** from Actions
3. Click **Go**

**To deactivate providers:**
1. Select provider(s)
2. Choose **"Deactivate selected providers"** from Actions
3. Click **Go**

### 6. Creating New Provider

1. Click **"Add SMS provider"**
2. Fill in the form:
   - **Name**: A descriptive name (e.g., "Beem Main")
   - **Provider Type**: Beem, Twilio, etc.
   - **Tenant**: Select the tenant
   - **Is active**: Check to activate
   - **Is default**: Check if this should be the default
   - **API Key**: From provider dashboard
   - **Secret Key**: From provider dashboard
   - **API URL**: Provider endpoint
   - **Cost per SMS**: Cost in your currency
   - **Currency**: USD, TZS, etc.
3. Click **Save**

## Common Scenarios

### Scenario 1: Switching to a Different Provider

1. Create new provider with its credentials
2. Test the connection to verify it works
3. Set it as default provider
4. The system will automatically use it for all SMS operations

### Scenario 2: Handling Low Balance

If you see insufficient balance error:

1. Go to Admin Panel → SMS Providers
2. Check the **Balance** column to see current balance
3. If balance is low:
   - Click on the provider to edit
   - Scroll to **"Provider Status"** section
   - Review the **Balance Information**
4. Add balance to your provider account
5. Test connection again to verify

### Scenario 3: Provider is Down

If a provider stops working:

1. Go to Admin Panel → SMS Providers
2. Find the active provider
3. **Deactivate** it (uncheck "Is active")
4. **Activate** another provider
5. **Set it as default** if needed
6. All SMS operations will now use the new provider

### Scenario 4: Multiple Providers for Backup

1. Create multiple providers
2. Set one as default
3. Keep others active as backup
4. When default provider fails, quickly switch to backup:
   - Edit the backup provider
   - Check "Is default"
   - Uncheck on the old default
   - Save

## Admin Actions Summary

| Action | Purpose | Usage |
|--------|---------|-------|
| **Set as default** | Make provider the default for tenant | Select provider(s) → Action: "Set as default provider" |
| **Test connections** | Test if providers are working | Select provider(s) → Action: "Test connections..." |
| **Activate** | Enable providers | Select provider(s) → Action: "Activate selected providers" |
| **Deactivate** | Disable providers | Select provider(s) → Action: "Deactivate selected providers" |

## Balance Check Details

### When Balance is Checked

Balance is automatically checked:
- When viewing the SMS Provider list
- When editing a provider
- When testing connections

### Balance Check Information

The balance check shows:
- **Success**: Shows balance amount
- **Error**: Shows error message (e.g., "Insufficient balance", "Invalid credentials")
- **Not Available**: Provider type doesn't support balance checking

### Troubleshooting Balance Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Insufficient balance" | Account needs top-up | Add funds to provider account |
| "Invalid credentials" | Wrong API keys | Update API key and secret key |
| "Network error" | Connection issue | Check network, try again later |
| "Unauthorized" | Invalid API key | Verify API key in provider dashboard |

## Best Practices

### 1. Always Test Before Setting as Default

```
1. Create provider → Test connection → Verify balance → Set as default
```

### 2. Monitor Balance Regularly

- Check balance status in admin panel
- Set up notifications for low balance
- Keep backup providers ready

### 3. Use Descriptive Names

- **Good**: "Beem Africa - Main", "Beem Africa - Backup"
- **Bad**: "Provider 1", "Test"

### 4. Document Provider Settings

Keep a record of:
- Provider credentials (store securely)
- Costs and rates
- Any special settings

### 5. Test After Changes

After updating provider settings:
1. Test the connection
2. Send a test SMS
3. Verify delivery

## API Integration

The system automatically uses the default provider. When you send an SMS:

```python
from messaging.services.sms_service import SMSService

# Automatically uses default provider for tenant
sms_service = SMSService(tenant_id=str(tenant.id))
result = sms_service.send_sms(
    to="+255689726060",
    message="Hello",
    sender_id="MIFUMO"
)
```

To use a specific provider:

```python
# Use specific provider
result = sms_service.send_sms(
    to="+255689726060",
    message="Hello",
    sender_id="MIFUMO",
    provider_id="your-provider-id"  # Specify provider
)
```

## Security Notes

- **API keys** are stored in the database (encrypted in production)
- **Never** commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Only admins can access the admin panel

## Quick Reference

### URLs

- Admin Panel: `/admin/`
- SMS Providers: `/admin/messaging/smsprovider/`
- Add Provider: `/admin/messaging/smsprovider/add/`

### Required Fields

When creating a provider:
- ✅ Name (required)
- ✅ Provider Type (required)
- ✅ Tenant (required)
- ✅ API Key (required)
- ✅ Secret Key (required)
- ✅ API URL (required)
- ✅ Cost per SMS (required)
- ✅ Currency (required)

### Optional Fields

- Webhook URL (for delivery reports)
- Settings (JSON for provider-specific config)
- Is active (defaults to True)
- Is default (defaults to False)

## Getting Help

If you encounter issues:

1. **Check logs**: Look for error messages in Django logs
2. **Test connection**: Use the admin action to test
3. **Verify credentials**: Double-check API keys
4. **Check balance**: Ensure sufficient balance
5. **Contact support**: If issue persists

## Summary

The SMS Provider management in the admin panel provides:
- ✅ Easy provider switching
- ✅ Real-time balance checking
- ✅ Connection testing
- ✅ Batch operations
- ✅ Clear status indicators
- ✅ Quick default switching

This makes it easy to manage multiple SMS providers, switch between them, and handle issues like insufficient balance or provider downtime.

