"""
Views for user authentication and management.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, EmailVerificationSerializer
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
    
    subject = 'Password reset request - Mifumo WMS'
    message = f"""
    Hi {user.get_full_name()},
    
    You requested a password reset. Click the link below to reset your password:
    
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    
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
    
    return Response({'message': 'Password reset email sent'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset."""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    user = User.objects.get(verification_token=token)
    
    # Check if token is not expired (1 hour)
    if user.verification_sent_at and timezone.now() - user.verification_sent_at > timedelta(hours=1):
        return Response({'error': 'Reset token has expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update password
    user.set_password(new_password)
    user.verification_token = ''
    user.save()
    
    return Response({'message': 'Password reset successfully'})


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
