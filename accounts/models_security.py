"""
Security models for user authentication and security features.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import secrets
import pyotp
import qrcode
import io
import base64

User = get_user_model()


class UserSession(models.Model):
    """
    Tracks user login sessions for security management.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.email} - {self.device_name or 'Unknown Device'}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def terminate(self):
        """Terminate this session."""
        self.is_active = False
        self.save()


class TwoFactorAuth(models.Model):
    """
    Manages two-factor authentication for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_auth')
    secret_key = models.CharField(max_length=32, unique=True)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'two_factor_auth'

    def __str__(self):
        return f"2FA for {self.user.email} - {'Enabled' if self.is_enabled else 'Disabled'}"

    def generate_secret_key(self):
        """Generate a new secret key for TOTP."""
        self.secret_key = pyotp.random_base32()
        self.save()
        return self.secret_key

    def generate_backup_codes(self, count=10):
        """Generate backup codes for 2FA."""
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = codes
        self.save()
        return codes

    def verify_totp(self, token):
        """Verify a TOTP token."""
        if not self.is_enabled or not self.secret_key:
            return False
        
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token, valid_window=1)

    def verify_backup_code(self, code):
        """Verify a backup code."""
        if not self.is_enabled or not self.backup_codes:
            return False
        
        if code in self.backup_codes:
            # Remove used backup code
            self.backup_codes.remove(code)
            self.save()
            return True
        return False

    def get_qr_code_data(self):
        """Generate QR code data for authenticator app setup."""
        if not self.secret_key:
            return None
        
        totp_uri = pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=self.user.email,
            issuer_name="Mifumo SMS"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'qr_code': f"data:image/png;base64,{img_str}",
            'secret_key': self.secret_key,
            'manual_entry_key': self.secret_key
        }

    def enable(self):
        """Enable 2FA for the user."""
        self.is_enabled = True
        self.save()

    def disable(self):
        """Disable 2FA for the user."""
        self.is_enabled = False
        self.backup_codes = []
        self.save()


class SecurityEvent(models.Model):
    """
    Logs security-related events for audit purposes.
    """
    EVENT_TYPES = [
        ('password_change', 'Password Changed'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('session_terminated', 'Session Terminated'),
        ('failed_login', 'Failed Login'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_event_type_display()} - {self.created_at}"
