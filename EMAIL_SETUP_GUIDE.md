# Email Configuration Setup Guide

## Step-by-Step Email Setup

### 1. Locate Your Environment File

The project uses `python-decouple` to read environment variables. Create a `.env` file in your project root directory.

### 2. Add Email Configuration

Open or create `.env` file in the root directory and add:

```env
# SMTP Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM_NAME=Mifumo WMS
EMAIL_FROM_ADDRESS=noreply@mifumo.com
```

### 3. Gmail Setup (Most Common)

If using Gmail, you need to use an **App Password**:

#### Steps to Get Gmail App Password:

1. Go to your Google Account
2. Select **Security**
3. Under "Signing in to Google," select **2-Step Verification** (enable if not enabled)
4. At the bottom, select **App passwords**
5. Choose app: **Mail**
6. Choose device: **Other (Custom name)** → Enter "Mifumo WMS"
7. Click **Generate**
8. Copy the 16-character password

#### Your .env file will look like:

```env
EMAIL_HOST_USER=yourname@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

**Note**: Use the 16-character password without spaces, or with spaces (both work).

### 4. Alternative Email Providers

#### SendGrid
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

#### AWS SES
```env
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-access-key
EMAIL_HOST_PASSWORD=your-secret-key
```

#### Outlook/Office 365
```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

### 5. Test Email Configuration

#### Using Django Shell
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email.',
    'noreply@mifumo.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

#### Quick Test Script
Create `test_email.py`:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        'Test Email',
        'If you receive this, your email is configured correctly!',
        'noreply@mifumo.com',
        ['your-email@example.com'],
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run: `python test_email.py`

### 6. Security Best Practices

#### DO:
- ✅ Use App Passwords for Gmail (not your main password)
- ✅ Store credentials in `.env` file
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables in production
- ✅ Enable 2FA on your email account

#### DON'T:
- ❌ Commit `.env` to version control
- ❌ Share your app passwords
- ❌ Use your main email password
- ❌ Hardcode credentials in code

### 7. Current Configuration in Code

The email settings are already configured in `mifumo/settings.py`:

```python
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_FROM_NAME = config("EMAIL_FROM_NAME", default="Mifumo WMS")
EMAIL_FROM_ADDRESS = config("EMAIL_FROM_ADDRESS", default="noreply@mifumo.com")
DEFAULT_FROM_EMAIL = f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
```

These read from your `.env` file automatically.

### 8. Without Email Configuration

**Good news!** Team invitations still work even if email is not configured:

- ✅ Member is created successfully
- ✅ Invitation token is generated
- ✅ Membership is saved in database
- ⚠️ No email is sent

You can manually share the invitation link or check the logs for the token.

### 9. Quick Setup Commands

```bash
# 1. Create .env file
touch .env

# 2. Add credentials (using nano or any editor)
nano .env

# 3. Add the configuration:
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# 4. Restart server
python manage.py runserver
```

### 10. Troubleshooting

#### Error: "SMTPAuthenticationError"
- Check email and password are correct
- For Gmail: Use App Password, not regular password
- Ensure 2-Step Verification is enabled

#### Error: "Connection refused"
- Check EMAIL_HOST is correct
- Check EMAIL_PORT is correct (587 for Gmail)
- Check firewall isn't blocking port

#### Error: "TLS/SSL error"
- Set `EMAIL_USE_TLS=True` for port 587
- Set `EMAIL_USE_SSL=True` for port 465

#### No Error But No Email
- Check spam folder
- Verify recipient email is correct
- Check logs for send_mail errors
- Try different email provider

### 11. Production Deployment

For production, use environment variables or a config file:

```bash
export EMAIL_HOST_USER="production@mifumo.com"
export EMAIL_HOST_PASSWORD="production-password"
```

Or use a secrets manager (AWS Secrets Manager, Azure Key Vault, etc.).

---

## Summary

**To enable email functionality:**
1. Create `.env` file
2. Add your email credentials
3. Restart the server
4. Email will work automatically!

**Team invitations work regardless of email configuration** - members are created and invitation links are generated even if email fails to send.

