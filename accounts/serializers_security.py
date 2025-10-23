"""
Security-related serializers for authentication and security features.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models_security import UserSession, TwoFactorAuth, SecurityEvent


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        """Validate password confirmation."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return data

    def save(self):
        """Save the new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Log security event
        SecurityEvent.objects.create(
            user=user,
            event_type='password_change',
            description='Password changed successfully',
            ip_address=self.context['request'].META.get('REMOTE_ADDR'),
            user_agent=self.context['request'].META.get('HTTP_USER_AGENT', ''),
            metadata={'changed_at': user.updated_at.isoformat()}
        )
        
        return user


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions."""
    is_current = serializers.SerializerMethodField()
    device_info = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            'id', 'session_key', 'ip_address', 'device_name', 'location',
            'is_active', 'created_at', 'last_activity', 'expires_at',
            'is_current', 'device_info', 'time_ago'
        ]
        read_only_fields = ['id', 'session_key', 'created_at', 'last_activity']

    def get_is_current(self, obj):
        """Check if this is the current session."""
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            return obj.session_key == request.session.session_key
        return False

    def get_device_info(self, obj):
        """Extract device information from user agent."""
        user_agent = obj.user_agent or ''
        device_info = {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device_type': 'Unknown'
        }
        
        # Simple user agent parsing (in production, use a proper library)
        if 'Chrome' in user_agent:
            device_info['browser'] = 'Chrome'
        elif 'Firefox' in user_agent:
            device_info['browser'] = 'Firefox'
        elif 'Safari' in user_agent:
            device_info['browser'] = 'Safari'
        elif 'Edge' in user_agent:
            device_info['browser'] = 'Edge'
        
        if 'Windows' in user_agent:
            device_info['os'] = 'Windows'
        elif 'Mac' in user_agent:
            device_info['os'] = 'macOS'
        elif 'Linux' in user_agent:
            device_info['os'] = 'Linux'
        elif 'Android' in user_agent:
            device_info['os'] = 'Android'
        elif 'iOS' in user_agent:
            device_info['os'] = 'iOS'
        
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_info['device_type'] = 'Mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            device_info['device_type'] = 'Tablet'
        else:
            device_info['device_type'] = 'Desktop'
        
        return device_info

    def get_time_ago(self, obj):
        """Get human-readable time ago."""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.last_activity
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"


class TwoFactorAuthSerializer(serializers.ModelSerializer):
    """Serializer for two-factor authentication."""
    qr_code_data = serializers.SerializerMethodField()
    backup_codes = serializers.SerializerMethodField()

    class Meta:
        model = TwoFactorAuth
        fields = [
            'id', 'is_enabled', 'created_at', 'updated_at',
            'qr_code_data', 'backup_codes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_qr_code_data(self, obj):
        """Get QR code data for setup."""
        if obj.is_enabled:
            return None  # Don't show QR code if already enabled
        return obj.get_qr_code_data()

    def get_backup_codes(self, obj):
        """Get backup codes (only when first enabling)."""
        if obj.is_enabled:
            return None  # Don't show backup codes if already enabled
        return obj.backup_codes


class Enable2FASerializer(serializers.Serializer):
    """Serializer for enabling 2FA."""
    totp_code = serializers.CharField(max_length=6, min_length=6)
    backup_codes = serializers.ListField(
        child=serializers.CharField(max_length=8),
        read_only=True
    )

    def validate_totp_code(self, value):
        """Validate TOTP code format."""
        if not value.isdigit():
            raise serializers.ValidationError("TOTP code must contain only digits.")
        return value

    def save(self):
        """Enable 2FA for the user."""
        user = self.context['request'].user
        totp_code = self.validated_data['totp_code']
        
        # Get or create 2FA record
        two_factor, created = TwoFactorAuth.objects.get_or_create(user=user)
        
        if not two_factor.secret_key:
            two_factor.generate_secret_key()
        
        # Verify TOTP code
        if not two_factor.verify_totp(totp_code):
            raise serializers.ValidationError("Invalid TOTP code. Please try again.")
        
        # Generate backup codes
        backup_codes = two_factor.generate_backup_codes()
        
        # Enable 2FA
        two_factor.enable()
        
        # Log security event
        SecurityEvent.objects.create(
            user=user,
            event_type='2fa_enabled',
            description='Two-factor authentication enabled',
            ip_address=self.context['request'].META.get('REMOTE_ADDR'),
            user_agent=self.context['request'].META.get('HTTP_USER_AGENT', ''),
            metadata={'enabled_at': two_factor.updated_at.isoformat()}
        )
        
        return two_factor, backup_codes


class Disable2FASerializer(serializers.Serializer):
    """Serializer for disabling 2FA."""
    password = serializers.CharField(write_only=True)
    totp_code = serializers.CharField(max_length=6, min_length=6, required=False)

    def validate_password(self, value):
        """Validate user password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect.")
        return value

    def validate_totp_code(self, value):
        """Validate TOTP code if 2FA is enabled."""
        user = self.context['request'].user
        try:
            two_factor = user.two_factor_auth
            if two_factor.is_enabled and not two_factor.verify_totp(value):
                raise serializers.ValidationError("Invalid TOTP code.")
        except TwoFactorAuth.DoesNotExist:
            pass
        return value

    def save(self):
        """Disable 2FA for the user."""
        user = self.context['request'].user
        
        try:
            two_factor = user.two_factor_auth
            two_factor.disable()
            
            # Log security event
            SecurityEvent.objects.create(
                user=user,
                event_type='2fa_disabled',
                description='Two-factor authentication disabled',
                ip_address=self.context['request'].META.get('REMOTE_ADDR'),
                user_agent=self.context['request'].META.get('HTTP_USER_AGENT', ''),
                metadata={'disabled_at': timezone.now().isoformat()}
            )
            
        except TwoFactorAuth.DoesNotExist:
            pass


class Verify2FASerializer(serializers.Serializer):
    """Serializer for verifying 2FA codes."""
    totp_code = serializers.CharField(max_length=6, min_length=6, required=False)
    backup_code = serializers.CharField(max_length=8, required=False)

    def validate(self, data):
        """Validate that either TOTP or backup code is provided."""
        if not data.get('totp_code') and not data.get('backup_code'):
            raise serializers.ValidationError("Either TOTP code or backup code is required.")
        return data

    def validate_totp_code(self, value):
        """Validate TOTP code format."""
        if value and not value.isdigit():
            raise serializers.ValidationError("TOTP code must contain only digits.")
        return value

    def verify(self, user):
        """Verify 2FA code."""
        try:
            two_factor = user.two_factor_auth
            if not two_factor.is_enabled:
                return True  # 2FA not enabled, skip verification
            
            totp_code = self.validated_data.get('totp_code')
            backup_code = self.validated_data.get('backup_code')
            
            if totp_code and two_factor.verify_totp(totp_code):
                return True
            elif backup_code and two_factor.verify_backup_code(backup_code):
                return True
            else:
                return False
                
        except TwoFactorAuth.DoesNotExist:
            return True  # No 2FA setup, skip verification


class SecurityEventSerializer(serializers.ModelSerializer):
    """Serializer for security events."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = SecurityEvent
        fields = [
            'id', 'event_type', 'event_type_display', 'description',
            'ip_address', 'user_agent', 'metadata', 'created_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at']

    def get_time_ago(self, obj):
        """Get human-readable time ago."""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
