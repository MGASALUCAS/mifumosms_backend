"""
Security-related views for authentication and security features.
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.contrib.sessions.models import Session

from .models_security import UserSession, TwoFactorAuth, SecurityEvent
from .serializers_security import (
    ChangePasswordSerializer, UserSessionSerializer, TwoFactorAuthSerializer,
    Enable2FASerializer, Disable2FASerializer, Verify2FASerializer,
    SecurityEventSerializer
)

logger = logging.getLogger(__name__)


class SecurityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.

    POST /api/auth/security/change-password/
    """
    try:
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to change password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def two_factor_status(request):
    """
    Get 2FA status and setup data.

    GET /api/auth/security/2fa/status/
    """
    try:
        two_factor, created = TwoFactorAuth.objects.get_or_create(user=request.user)

        if created:
            # Generate secret key for new 2FA setup
            two_factor.generate_secret_key()

        serializer = TwoFactorAuthSerializer(two_factor, context={'request': request})

        return Response({
            'success': True,
            'data': serializer.data
        })

    except Exception as e:
        logger.error(f"Error getting 2FA status: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get 2FA status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    Enable two-factor authentication.

    POST /api/auth/security/2fa/enable/
    """
    try:
        serializer = Enable2FASerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            two_factor, backup_codes = serializer.save()

            return Response({
                'success': True,
                'message': 'Two-factor authentication enabled successfully',
                'backup_codes': backup_codes,
                'warning': 'Please save these backup codes in a secure location. They will not be shown again.'
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error enabling 2FA: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to enable 2FA'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Disable two-factor authentication.

    POST /api/auth/security/2fa/disable/
    """
    try:
        serializer = Disable2FASerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response({
                'success': True,
                'message': 'Two-factor authentication disabled successfully'
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error disabling 2FA: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to disable 2FA'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """
    Verify 2FA code (for login or sensitive operations).

    POST /api/auth/security/2fa/verify/
    """
    try:
        serializer = Verify2FASerializer(data=request.data)

        if serializer.is_valid():
            is_valid = serializer.verify(request.user)

            if is_valid:
                return Response({
                    'success': True,
                    'message': '2FA verification successful'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid 2FA code'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error verifying 2FA: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to verify 2FA'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSessionListView(generics.ListAPIView):
    """
    List user's active sessions.

    GET /api/auth/security/sessions/
    """
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SecurityPagination

    def get_queryset(self):
        # Handle Swagger schema generation with AnonymousUser
        if not self.request.user.is_authenticated:
            return UserSession.objects.none()
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-last_activity')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, context={'request': request})

            return Response({
                'success': True,
                'sessions': serializer.data,
                'total_count': queryset.count()
            })

        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_session(request, session_id):
    """
    Terminate a specific session.

    POST /api/auth/security/sessions/{session_id}/terminate/
    """
    try:
        session = get_object_or_404(
            UserSession,
            id=session_id,
            user=request.user,
            is_active=True
        )

        # Don't allow terminating current session
        if session.session_key == request.session.session_key:
            return Response({
                'success': False,
                'error': 'Cannot terminate current session'
            }, status=status.HTTP_400_BAD_REQUEST)

        session.terminate()

        # Log security event
        SecurityEvent.objects.create(
            user=request.user,
            event_type='session_terminated',
            description=f'Session terminated: {session.device_name or "Unknown Device"}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'terminated_session_id': str(session.id),
                'terminated_at': timezone.now().isoformat()
            }
        )

        return Response({
            'success': True,
            'message': 'Session terminated successfully'
        })

    except Exception as e:
        logger.error(f"Error terminating session: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to terminate session'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_all_other_sessions(request):
    """
    Terminate all sessions except the current one.

    POST /api/auth/security/sessions/terminate-all-others/
    """
    try:
        current_session_key = request.session.session_key
        terminated_count = 0

        # Get all active sessions except current one
        other_sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(session_key=current_session_key)

        for session in other_sessions:
            session.terminate()
            terminated_count += 1

        # Log security event
        SecurityEvent.objects.create(
            user=request.user,
            event_type='session_terminated',
            description=f'All other sessions terminated ({terminated_count} sessions)',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'terminated_count': terminated_count,
                'terminated_at': timezone.now().isoformat()
            }
        )

        return Response({
            'success': True,
            'message': f'Terminated {terminated_count} other sessions',
            'terminated_count': terminated_count
        })

    except Exception as e:
        logger.error(f"Error terminating all other sessions: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to terminate sessions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SecurityEventListView(generics.ListAPIView):
    """
    List user's security events.

    GET /api/auth/security/events/
    """
    serializer_class = SecurityEventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SecurityPagination

    def get_queryset(self):
        # Handle Swagger schema generation with AnonymousUser
        if not self.request.user.is_authenticated:
            return SecurityEvent.objects.none()
        return SecurityEvent.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)

            return Response({
                'success': True,
                'events': serializer.data,
                'total_count': queryset.count()
            })

        except Exception as e:
            logger.error(f"Error listing security events: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get security events'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_summary(request):
    """
    Get security summary for the user.

    GET /api/auth/security/summary/
    """
    try:
        # Get 2FA status
        try:
            two_factor = request.user.two_factor_auth
            two_factor_enabled = two_factor.is_enabled
        except TwoFactorAuth.DoesNotExist:
            two_factor_enabled = False

        # Get session count
        active_sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).count()

        # Get recent security events count
        recent_events = SecurityEvent.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()

        # Get last password change
        last_password_change = SecurityEvent.objects.filter(
            user=request.user,
            event_type='password_change'
        ).order_by('-created_at').first()

        return Response({
            'success': True,
            'data': {
                'two_factor_enabled': two_factor_enabled,
                'active_sessions': active_sessions,
                'recent_events_count': recent_events,
                'last_password_change': last_password_change.created_at.isoformat() if last_password_change else None,
                'security_score': calculate_security_score(two_factor_enabled, active_sessions, recent_events)
            }
        })

    except Exception as e:
        logger.error(f"Error getting security summary: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get security summary'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_security_score(two_factor_enabled, active_sessions, recent_events):
    """Calculate a simple security score (0-100)."""
    score = 50  # Base score

    # 2FA adds 30 points
    if two_factor_enabled:
        score += 30

    # Fewer active sessions is better (max 20 points)
    if active_sessions <= 1:
        score += 20
    elif active_sessions <= 3:
        score += 15
    elif active_sessions <= 5:
        score += 10
    else:
        score += 5

    # Recent events indicate activity (max 20 points)
    if recent_events <= 5:
        score += 20
    elif recent_events <= 10:
        score += 15
    elif recent_events <= 20:
        score += 10
    else:
        score += 5

    return min(100, max(0, score))
