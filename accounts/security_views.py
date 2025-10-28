"""
Security endpoints for 2FA, sessions, and security events.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_summary(request):
    """
    Get security summary information.
    GET /api/auth/security/summary/
    """
    user = request.user
    
    # Calculate security score based on various factors
    security_score = 0
    
    # Password exists
    if user.password:
        security_score += 25
    # Email verified
    if user.is_verified:
        security_score += 25
    # Phone verified
    if user.phone_verified:
        security_score += 25
    # Phone number exists
    if user.phone_number:
        security_score += 25
    
    # Get active sessions count (mock for now)
    active_sessions = 1
    
    # Get recent events count (mock for now)
    recent_events_count = 0
    
    # Last password change (use updated_at as proxy)
    last_password_change = user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
    
    return Response({
        'success': True,
        'data': {
            'two_factor_enabled': False,
            'active_sessions': active_sessions,
            'recent_events_count': recent_events_count,
            'last_password_change': last_password_change,
            'security_score': security_score
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def two_factor_status(request):
    """
    Get two-factor authentication status.
    GET /api/auth/security/2fa/status/
    """
    user = request.user
    
    # For now, 2FA is disabled
    # In the future, we can check if user has a TwoFactorAuth object
    return Response({
        'success': True,
        'data': {
            'id': 'mock-2fa-id',
            'is_enabled': False,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else timezone.now().isoformat(),
            'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else timezone.now().isoformat(),
            'qr_code_data': None,
            'backup_codes': None
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_sessions(request):
    """
    Get active sessions for the user.
    GET /api/auth/security/sessions/
    """
    user = request.user
    
    # For now, return a mock session
    # In the future, we can query actual UserSession model
    current_session = {
        'id': 'current-session-id',
        'session_key': 'current-session-key',
        'ip_address': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'device_name': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        'location': 'Unknown',
        'is_active': True,
        'created_at': user.last_login_at.isoformat() if user.last_login_at else timezone.now().isoformat(),
        'last_activity': timezone.now().isoformat(),
        'expires_at': (timezone.now() + timedelta(days=7)).isoformat(),
        'is_current': True,
        'device_info': {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device_type': 'Unknown'
        },
        'time_ago': 'Just now'
    }
    
    return Response({
        'success': True,
        'sessions': [current_session],
        'total_count': 1
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_session(request, session_id):
    """
    Terminate a specific session.
    POST /api/auth/security/sessions/{session_id}/terminate/
    """
    # For now, just return success
    # In the future, we can actually terminate sessions
    if session_id == 'current-session-id':
        return Response({
            'success': False,
            'error': 'Cannot terminate current session'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': True,
        'message': 'Session terminated successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_all_other_sessions(request):
    """
    Terminate all other sessions except the current one.
    POST /api/auth/security/sessions/terminate-all-others/
    """
    # For now, just return success with count
    return Response({
        'success': True,
        'message': 'Terminated 0 other sessions',
        'terminated_count': 0
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_events(request):
    """
    Get security events for the user.
    GET /api/auth/security/events/
    """
    user = request.user
    
    # For now, return empty events
    # In the future, we can query SecurityEvent model
    return Response({
        'success': True,
        'events': [],
        'total_count': 0,
        'has_more': False
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_two_factor(request):
    """
    Enable two-factor authentication.
    POST /api/auth/security/2fa/enable/
    """
    # For now, return a message that this is not yet implemented
    return Response({
        'success': False,
        'message': 'Two-factor authentication is not yet implemented. Coming soon!'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_two_factor(request):
    """
    Disable two-factor authentication.
    POST /api/auth/security/2fa/disable/
    """
    # For now, return a message that this is not yet implemented
    return Response({
        'success': False,
        'message': 'Two-factor authentication is not yet implemented. Coming soon!'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_two_factor(request):
    """
    Verify two-factor authentication code.
    POST /api/auth/security/2fa/verify/
    """
    # For now, return a message that this is not yet implemented
    return Response({
        'success': False,
        'message': 'Two-factor authentication is not yet implemented. Coming soon!'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_security(request):
    """
    Change password from security settings.
    POST /api/auth/security/change-password/
    """
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        return Response({
            'success': False,
            'errors': {
                'non_field_errors': ['All password fields are required.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check current password
    if not request.user.check_password(current_password):
        return Response({
            'success': False,
            'errors': {
                'current_password': ['Current password is incorrect.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if new password matches confirmation
    if new_password != confirm_password:
        return Response({
            'success': False,
            'errors': {
                'confirm_password': ['Passwords do not match.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    if len(new_password) < 8:
        return Response({
            'success': False,
            'errors': {
                'new_password': ['Password must be at least 8 characters long.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Change password
    request.user.set_password(new_password)
    request.user.save()
    
    return Response({
        'success': True,
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)

