"""
Views for user authentication and management.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.db.models import Q
from datetime import timedelta

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, EmailVerificationSerializer,
    UserProfileSettingsSerializer, UserPreferencesSerializer,
    UserNotificationsSerializer, UserSecuritySerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Create user and send verification email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate verification token
        user.verification_token = get_random_string(32)
        user.verification_sent_at = timezone.now()
        user.save()

        # Send verification email (disabled for development)
        # self.send_verification_email(user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User created successfully. Please check your email for verification.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user):
        """Send email verification to user."""
        verification_url = f"{settings.BASE_URL}/verify-email/{user.verification_token}"

        subject = 'Verify your email address - Mifumo WMS'
        message = f"""
        Hi {user.get_full_name()},

        Welcome to Mifumo WMS! Please verify your email address by clicking the link below:

        {verification_url}

        This link will expire in 24 hours.

        If you didn't create an account, please ignore this email.

        Best regards,
        The Mifumo Team
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class UserLoginView(generics.GenericAPIView):
    """User login endpoint."""

    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.update_last_login()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """Extended user profile management."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class PasswordChangeView(generics.GenericAPIView):
    """Password change endpoint."""

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        """Change user password."""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset."""
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    user = User.objects.get(email=email)

    # Generate reset token
    user.verification_token = get_random_string(32)
    user.verification_sent_at = timezone.now()
    user.save()

    # Send reset email
    reset_url = f"{settings.BASE_URL}/reset-password/{user.verification_token}"

    subject = 'Password Reset Request - Mifumo WMS'
    message = f"""
    Hi {user.get_full_name()},

    You requested a password reset for your Mifumo WMS account. Click the link below to reset your password:

    {reset_url}

    This link will expire in 1 hour for security reasons.

    If you didn't request this password reset, please ignore this email and your password will remain unchanged.

    For security reasons, please do not share this link with anyone.

    Best regards,
    The Mifumo Team

    ---
    This is an automated message. Please do not reply to this email.
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': 'Password reset email sent successfully. Please check your inbox and follow the instructions.',
            'email': email  # Return email for confirmation
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to send password reset email. Please try again later.',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Forgot password endpoint - same as password reset but with better UX."""
    return password_reset_request(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset."""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']

    try:
        user = User.objects.get(verification_token=token)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid or expired reset token. Please request a new password reset.',
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if token is not expired (1 hour)
    if user.verification_sent_at and timezone.now() - user.verification_sent_at > timedelta(hours=1):
        return Response({
            'success': False,
            'message': 'Reset token has expired. Please request a new password reset.',
            'error': 'Token expired'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Update password
    user.set_password(new_password)
    user.verification_token = ''
    user.save()

    return Response({
        'success': True,
        'message': 'Password reset successfully. You can now log in with your new password.',
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify user email address."""
    serializer = EmailVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data['token']
    user = User.objects.get(verification_token=token)

    # Check if token is not expired (24 hours)
    if user.verification_sent_at and timezone.now() - user.verification_sent_at > timedelta(hours=24):
        return Response({'error': 'Verification token has expired'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify user
    user.is_verified = True
    user.verification_token = ''
    user.save()

    return Response({'message': 'Email verified successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_api_key(request):
    """Generate API key for user."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    api_key = profile.generate_api_key()

    return Response({
        'message': 'API key generated successfully',
        'api_key': api_key
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_api_key(request):
    """Revoke user's API key."""
    try:
        profile = request.user.profile
        profile.api_key = ''
        profile.api_key_created_at = None
        profile.save()

        return Response({'message': 'API key revoked successfully'})
    except UserProfile.DoesNotExist:
        return Response({'error': 'No profile found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_lookup(request):
    """
    User lookup endpoint for Django admin raw_id_fields.
    This endpoint provides user search functionality for admin interface.
    """
    search_query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 20)), 100)

    # Build search query
    users = User.objects.all()
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    total_count = users.count()
    users_page = users[start:end]

    # Format response for Django admin lookup
    results = []
    for user in users_page:
        results.append({
            'id': str(user.id),
            'text': f"{user.get_full_name()} ({user.email})",
            'email': user.email,
            'full_name': user.get_full_name(),
            'is_active': user.is_active,
            'is_verified': user.is_verified
        })

    return Response({
        'results': results,
        'pagination': {
            'more': end < total_count,
            'page': page,
            'page_size': page_size,
            'total_count': total_count
        }
    })


# =============================================
# USER PROFILE SETTINGS VIEWS
# =============================================

class UserProfileSettingsView(generics.RetrieveUpdateAPIView):
    """User profile settings management (first name, last name, phone number)."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSettingsSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """Get current user profile settings."""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def put(self, request, *args, **kwargs):
        """Update user profile settings."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Profile settings updated successfully',
            'data': serializer.data
        })

    def patch(self, request, *args, **kwargs):
        """Partially update user profile settings."""
        return self.put(request, *args, **kwargs)


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """User preferences management (language, timezone, display settings)."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserPreferencesSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """Get current user preferences."""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def put(self, request, *args, **kwargs):
        """Update user preferences."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Preferences updated successfully',
            'data': serializer.data
        })

    def patch(self, request, *args, **kwargs):
        """Partially update user preferences."""
        return self.put(request, *args, **kwargs)


class UserNotificationsView(generics.RetrieveUpdateAPIView):
    """User notification preferences management."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserNotificationsSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """Get current user notification preferences."""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def put(self, request, *args, **kwargs):
        """Update user notification preferences."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'data': serializer.data
        })

    def patch(self, request, *args, **kwargs):
        """Partially update user notification preferences."""
        return self.put(request, *args, **kwargs)


class UserSecurityView(generics.RetrieveUpdateAPIView):
    """User security settings management (password, 2FA)."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSecuritySerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """Get current user security settings."""
        user = self.get_object()
        # Return basic security info for now
        return Response({
            'success': True,
            'data': {
                'has_password': bool(user.password),
                'is_verified': user.is_verified,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                'two_factor_enabled': False,  # Future implementation
                'api_key_configured': hasattr(user, 'profile') and bool(user.profile.api_key)
            }
        })

    def put(self, request, *args, **kwargs):
        """Update user security settings."""
        # For now, just return a message about future implementation
        return Response({
            'success': True,
            'message': 'Security settings endpoint ready for future 2FA implementation',
            'data': {
                'two_factor_enabled': False,
                'api_key_configured': hasattr(self.request.user, 'profile') and bool(self.request.user.profile.api_key)
            }
        })

    def patch(self, request, *args, **kwargs):
        """Partially update user security settings."""
        return self.put(request, *args, **kwargs)


# =============================================
# SMS VERIFICATION ENDPOINTS
# =============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    """Send SMS verification code to phone number."""
    phone_number = request.data.get('phone_number')
    message_type = request.data.get('message_type', 'verification')
    
    # If phone number provided, find user by phone
    user = None
    if phone_number:
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({
                'success': False,
                'error': 'No account found with this phone number.'
            }, status=status.HTTP_404_NOT_FOUND)
    elif request.user.is_authenticated:
        user = request.user
    else:
        return Response({
            'success': False,
            'error': 'Phone number or authentication required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Send verification code
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    result = sms_service.send_verification_code(user, message_type)
    
    if result['success']:
        response_data = {
            'success': True,
            'message': 'Verification code sent successfully',
            'phone_number': result.get('phone_number')
        }
        # Include bypassed flag if present
        if result.get('bypassed'):
            response_data['bypassed'] = True
        return Response(response_data)
    else:
        return Response({
            'success': False,
            'error': result.get('error', 'Failed to send verification code')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone_code(request):
    """Verify SMS verification code."""
    phone_number = request.data.get('phone_number')
    verification_code = request.data.get('verification_code')
    
    # Find user
    user = None
    if phone_number:
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({
                'success': False,
                'error': 'No account found with this phone number.'
            }, status=status.HTTP_404_NOT_FOUND)
    elif request.user.is_authenticated:
        user = request.user
    else:
        return Response({
            'success': False,
            'error': 'Phone number or authentication required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify code
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    result = sms_service.verify_code(user, verification_code)
    
    if result['success']:
        response_data = {
            'success': True,
            'message': 'Phone number verified successfully',
            'phone_verified': user.phone_verified
        }
        # Include bypassed flag if present
        if result.get('bypassed'):
            response_data['bypassed'] = True
        return Response(response_data)
    else:
        return Response({
            'success': False,
            'error': result.get('error', 'Verification failed'),
            'attempts_remaining': result.get('attempts_remaining', 0)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_sms(request):
    """Send password reset code via SMS."""
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize phone number for database lookup
    normalized_phone = normalize_phone_number(phone_number)
    user = User.objects.filter(phone_number=normalized_phone).first()
    if not user:
        return Response({
            'success': False,
            'error': 'No account found with this phone number.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Send password reset code
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    result = sms_service.send_verification_code(user, "password_reset")
    
    if result['success']:
        response_data = {
            'success': True,
            'message': 'Password reset code sent to your phone number',
            'phone_number': result.get('phone_number')
        }
        # Include bypassed flag if present
        if result.get('bypassed'):
            response_data['bypassed'] = True
        return Response(response_data)
    else:
        return Response({
            'success': False,
            'error': result.get('error', 'Failed to send reset code')
        }, status=status.HTTP_400_BAD_REQUEST)


def normalize_phone_number(phone_number):
    """Normalize phone number to local format for database lookup."""
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # Remove leading +
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Convert international format to local format
    if cleaned.startswith('255') and len(cleaned) == 12:
        # 255689726060 -> 0689726060
        cleaned = '0' + cleaned[3:]
    elif len(cleaned) == 9 and cleaned.startswith('6'):
        # 689726060 -> 0689726060
        cleaned = '0' + cleaned
    
    return cleaned


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_sms(request):
    """Reset password using SMS verification code."""
    phone_number = request.data.get('phone_number')
    verification_code = request.data.get('verification_code')
    new_password = request.data.get('new_password')
    
    if not phone_number or not verification_code or not new_password:
        return Response({
            'success': False,
            'error': 'Phone number, verification code, and new password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize phone number for database lookup
    normalized_phone = normalize_phone_number(phone_number)
    user = User.objects.filter(phone_number=normalized_phone).first()
    if not user:
        return Response({
            'success': False,
            'error': 'No account found with this phone number.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify code (don't clear code yet, will be cleared after password reset)
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    verify_result = sms_service.verify_code(user, verification_code, clear_code=False)
    
    if not verify_result['success']:
        return Response({
            'success': False,
            'error': verify_result.get('error', 'Invalid verification code'),
            'attempts_remaining': verify_result.get('attempts_remaining', 0)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Reset password
    user.set_password(new_password)
    
    # Clear verification code after successful password reset
    user.refresh_from_db()  # Refresh to get latest data
    user.phone_verification_code = ''
    user.phone_verification_sent_at = None
    user.save(update_fields=['phone_verification_code', 'phone_verification_sent_at'])
    
    return Response({
        'success': True,
        'message': 'Password reset successfully. You can now login with your new password.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_account_sms(request):
    """Confirm account using SMS verification code."""
    verification_code = request.data.get('verification_code')
    user = request.user
    
    if not verification_code:
        return Response({
            'success': False,
            'error': 'Verification code is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify code
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    result = sms_service.verify_code(user, verification_code)
    
    if result['success']:
        # Mark account as verified
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        response_data = {
            'success': True,
            'message': 'Account confirmed successfully',
            'is_verified': user.is_verified,
            'phone_verified': user.phone_verified
        }
        # Include bypassed flag if present
        if result.get('bypassed'):
            response_data['bypassed'] = True
        return Response(response_data)
    else:
        return Response({
            'success': False,
            'error': result.get('error', 'Verification failed'),
            'attempts_remaining': result.get('attempts_remaining', 0)
        }, status=status.HTTP_400_BAD_REQUEST)


# =============================================
# SMS VERIFICATION LINK ENDPOINTS
# =============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_link_sms(request):
    """Send account verification link via SMS."""
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize phone number for database lookup
    normalized_phone = normalize_phone_number(phone_number)
    user = User.objects.filter(phone_number=normalized_phone).first()
    if not user:
        return Response({
            'success': False,
            'error': 'No account found with this phone number.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Bypass for superadmin users
    if user.is_superuser or user.is_staff:
        return Response({
            'success': True,
            'message': 'Account verification not required for admin users',
            'bypassed': True,
            'phone_number': normalized_phone
        })
    
    # Generate verification token
    verification_token = get_random_string(32)
    user.verification_token = verification_token
    user.verification_sent_at = timezone.now()
    user.save(update_fields=['verification_token', 'verification_sent_at'])
    
    # Create verification link
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    verification_link = f"{base_url}/verify-account?token={verification_token}&phone={normalized_phone}"
    
    # Send SMS with verification link
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    
    # Create SMS message with link
    message = f"Your Mifumo WMS account verification link: {verification_link}. This link expires in 1 hour. Do not share this link with anyone."
    
    result = sms_service.send_verification_sms(
        user.phone_number,
        message,
        "account_verification"
    )
    
    if result['success']:
        return Response({
            'success': True,
            'message': 'Verification link sent to your phone number',
            'phone_number': normalized_phone,
            'verification_link': verification_link  # For testing purposes
        })
    else:
        return Response({
            'success': False,
            'error': result.get('error', 'Failed to send verification link')
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_account_link(request):
    """Verify account using verification link from SMS."""
    token = request.data.get('token')
    phone_number = request.data.get('phone_number')
    
    if not token or not phone_number:
        return Response({
            'success': False,
            'error': 'Token and phone number are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize phone number
    normalized_phone = normalize_phone_number(phone_number)
    
    try:
        user = User.objects.get(
            verification_token=token,
            phone_number=normalized_phone
        )
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid verification link or phone number.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if token is not expired (1 hour)
    if user.verification_sent_at and timezone.now() - user.verification_sent_at > timedelta(hours=1):
        return Response({
            'success': False,
            'error': 'Verification link has expired. Please request a new one.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify account
    user.is_verified = True
    user.phone_verified = True
    user.verification_token = ''
    user.save(update_fields=['is_verified', 'phone_verified', 'verification_token'])
    
    return Response({
        'success': True,
        'message': 'Account verified successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_verified': user.is_verified,
            'phone_verified': user.phone_verified
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_link(request):
    """Resend verification link via SMS."""
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalize phone number for database lookup
    normalized_phone = normalize_phone_number(phone_number)
    user = User.objects.filter(phone_number=normalized_phone).first()
    if not user:
        return Response({
            'success': False,
            'error': 'No account found with this phone number.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Bypass for superadmin users
    if user.is_superuser or user.is_staff:
        return Response({
            'success': True,
            'message': 'Account verification not required for admin users',
            'bypassed': True,
            'phone_number': normalized_phone
        })
    
    # Check if user is already verified
    if user.is_verified and user.phone_verified:
        return Response({
            'success': True,
            'message': 'Account is already verified',
            'phone_number': normalized_phone
        })
    
    # Generate new verification token
    verification_token = get_random_string(32)
    user.verification_token = verification_token
    user.verification_sent_at = timezone.now()
    user.save(update_fields=['verification_token', 'verification_sent_at'])
    
    # Create verification link
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    verification_link = f"{base_url}/verify-account?token={verification_token}&phone={normalized_phone}"
    
    # Send SMS with verification link
    from .services.sms_verification import SMSVerificationService
    sms_service = SMSVerificationService(str(user.get_tenant().id))
    
    # Create SMS message with link
    message = f"Your new Mifumo WMS account verification link: {verification_link}. This link expires in 1 hour. Do not share this link with anyone."
    
    result = sms_service.send_verification_sms(
        user.phone_number,
        message,
        "account_verification"
    )
    
    if result['success']:
        return Response({
            'success': True,
            'message': 'New verification link sent to your phone number',
            'phone_number': normalized_phone,
            'verification_link': verification_link  # For testing purposes
        })
    else:
        return Response({
            'success': False,
            'error': result.get('error', 'Failed to send verification link')
        }, status=status.HTTP_400_BAD_REQUEST)