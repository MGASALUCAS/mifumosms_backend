"""
Notification API views for the Mifumo WMS system.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

from .models import Notification, NotificationSettings, NotificationTemplate
from .services import NotificationService, SMSCreditNotificationService
from .system_monitor import SystemMonitor
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer,
    NotificationSettingsSerializer, NotificationTemplateSerializer
)

logger = logging.getLogger(__name__)


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListCreateView(generics.ListCreateAPIView):
    """
    List and create notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        """Get notifications for the authenticated user."""
        # Handle Swagger schema generation with AnonymousUser
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        queryset = Notification.objects.filter(user=self.request.user)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by type
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(notification_type=type_filter)

        # Filter by priority
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        # Filter out expired notifications
        queryset = queryset.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Create notification for the authenticated user."""
        serializer.save(user=self.request.user, tenant=self.request.user.get_tenant())


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get notifications for the authenticated user."""
        # Handle Swagger schema generation with AnonymousUser
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """
    Get notification statistics for the authenticated user.

    Returns:
        - Total notifications
        - Unread count
        - Count by type
        - Count by priority
    """
    try:
        user = request.user
        queryset = Notification.objects.filter(user=user)

        # Filter out expired notifications
        queryset = queryset.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

        stats = {
            'total': queryset.count(),
            'unread': queryset.filter(status='unread').count(),
            'by_type': {},
            'by_priority': {},
            'recent_count': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }

        # Count by type
        from .models import NotificationType
        for notification_type, _ in NotificationType.choices:
            count = queryset.filter(notification_type=notification_type).count()
            if count > 0:
                stats['by_type'][notification_type] = count

        # Count by priority
        from .models import NotificationPriority
        for priority, _ in NotificationPriority.choices:
            count = queryset.filter(priority=priority).count()
            if count > 0:
                stats['by_priority'][priority] = count

        return Response({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"Failed to get notification stats: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get notification statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a specific notification as read.

    Args:
        notification_id: UUID of the notification to mark as read
    """
    try:
        notification_service = NotificationService()
        success = notification_service.mark_as_read(notification_id, request.user)

        if success:
            return Response({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return Response({
                'success': False,
                'error': 'Notification not found or already read'
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Failed to mark notification as read: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to mark notification as read'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """
    Mark all notifications as read for the authenticated user.
    """
    try:
        notification_service = NotificationService()
        count = notification_service.mark_all_as_read(request.user)

        return Response({
            'success': True,
            'message': f'Marked {count} notifications as read'
        })

    except Exception as e:
        logger.error(f"Failed to mark all notifications as read: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to mark all notifications as read'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """
    Get the count of unread notifications for the authenticated user.
    """
    try:
        notification_service = NotificationService()
        count = notification_service.get_unread_count(request.user)

        return Response({
            'success': True,
            'unread_count': count
        })

    except Exception as e:
        logger.error(f"Failed to get unread count: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get unread count'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_notifications(request):
    """
    Get recent notifications for the header dropdown.

    Returns real notifications including system-generated ones for admins.
    """
    try:
        user = request.user
        system_monitor = SystemMonitor()

        # Get real notifications using system monitor
        notifications = system_monitor.get_real_notifications(user, limit=10)

        # Separate unread and read
        unread_notifications = [n for n in notifications if n.status == 'unread']
        read_notifications = [n for n in notifications if n.status == 'read']

        # Take up to 5 unread and 5 read
        display_notifications = unread_notifications[:5] + read_notifications[:5]
        display_notifications = display_notifications[:10]

        serializer = NotificationSerializer(display_notifications, many=True)

        return Response({
            'success': True,
            'notifications': serializer.data,
            'unread_count': len(unread_notifications)
        })

    except Exception as e:
        logger.error(f"Failed to get recent notifications: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get recent notifications'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    """
    Get and update notification settings for the authenticated user.
    """
    serializer_class = NotificationSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Get or create notification settings for the user."""
        settings_obj, created = NotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings_obj


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_sms_credit_notification(request):
    """
    Test SMS credit notification (for testing purposes).

    This endpoint simulates a low credit scenario and sends a notification.
    """
    try:
        user = request.user
        current_credits = request.data.get('current_credits', 10)
        total_credits = request.data.get('total_credits', 100)

        # Create SMS credit notification service
        sms_credit_service = SMSCreditNotificationService()

        # Check and notify about low credit
        sms_credit_service.check_and_notify_low_credit(
            user=user,
            current_credits=current_credits,
            total_credits=total_credits
        )

        return Response({
            'success': True,
            'message': 'SMS credit notification test completed',
            'current_credits': current_credits,
            'total_credits': total_credits,
            'percentage': (current_credits / total_credits) * 100
        })

    except Exception as e:
        logger.error(f"Failed to test SMS credit notification: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to test SMS credit notification'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_system_notification(request):
    """
    Create a system notification (for admin users).

    This endpoint allows creating notifications for other users.
    """
    try:
        # Check if user is admin
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'error': 'Permission denied. Admin access required.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get notification data
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('type', 'system')
        priority = request.data.get('priority', 'medium')
        user_emails = request.data.get('user_emails', [])

        if not title or not message:
            return Response({
                'success': False,
                'error': 'Title and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get users to notify
        if user_emails:
            users = User.objects.filter(email__in=user_emails)
        else:
            # Notify all users in the tenant
            users = User.objects.filter(tenant=request.user.get_tenant())

        if not users.exists():
            return Response({
                'success': False,
                'error': 'No users found to notify'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create notifications
        notification_service = NotificationService()
        notifications = notification_service.create_bulk_notifications(
            users=list(users),
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            is_system=True
        )

        return Response({
            'success': True,
            'message': f'Created {len(notifications)} notifications',
            'notifications_created': len(notifications)
        })

    except Exception as e:
        logger.error(f"Failed to create system notification: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to create system notification'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_templates(request):
    """
    Get available notification templates.
    """
    try:
        templates = NotificationTemplate.objects.filter(is_active=True)
        serializer = NotificationTemplateSerializer(templates, many=True)

        return Response({
            'success': True,
            'templates': serializer.data
        })

    except Exception as e:
        logger.error(f"Failed to get notification templates: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get notification templates'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_health_check(request):
    """
    Check system health and create notifications for problems (admin only).
    """
    try:
        # Check if user is admin
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'error': 'Permission denied. Admin access required.'
            }, status=status.HTTP_403_FORBIDDEN)

        system_monitor = SystemMonitor()
        health_status = system_monitor.check_system_health()

        return Response({
            'success': True,
            'health_status': health_status
        })

    except Exception as e:
        logger.error(f"Failed to check system health: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to check system health'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_problem(request):
    """
    Report a system problem and create notification (admin only).
    """
    try:
        # Check if user is admin
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'error': 'Permission denied. Admin access required.'
            }, status=status.HTTP_403_FORBIDDEN)

        problem_type = request.data.get('problem_type')
        description = request.data.get('description')
        priority = request.data.get('priority', 'medium')
        data = request.data.get('data', {})

        if not problem_type or not description:
            return Response({
                'success': False,
                'error': 'Problem type and description are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        system_monitor = SystemMonitor()
        notification = system_monitor.create_problem_notification(
            problem_type=problem_type,
            description=description,
            priority=priority,
            data=data
        )

        if notification:
            return Response({
                'success': True,
                'message': 'Problem reported and notification created',
                'notification_id': str(notification.id)
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to create problem notification'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Failed to report problem: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to report problem'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_real_notifications(request):
    """
    Get real notifications including system-generated ones.
    """
    try:
        user = request.user
        limit = int(request.query_params.get('limit', 20))

        system_monitor = SystemMonitor()
        notifications = system_monitor.get_real_notifications(user, limit=limit)

        serializer = NotificationSerializer(notifications, many=True)

        return Response({
            'success': True,
            'notifications': serializer.data,
            'count': len(notifications)
        })

    except Exception as e:
        logger.error(f"Failed to get real notifications: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to get real notifications'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_notifications(request):
    """
    Clean up old notifications (admin only).
    """
    try:
        # Check if user is admin
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'error': 'Permission denied. Admin access required.'
            }, status=status.HTTP_403_FORBIDDEN)

        days = int(request.data.get('days', 30))

        system_monitor = SystemMonitor()
        deleted_count = system_monitor.cleanup_old_notifications(days=days)

        return Response({
            'success': True,
            'message': f'Cleaned up {deleted_count} old notifications',
            'deleted_count': deleted_count
        })

    except Exception as e:
        logger.error(f"Failed to cleanup notifications: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to cleanup notifications'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
