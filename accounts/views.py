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
