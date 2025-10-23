"""
System monitoring and automatic notification creation.
This module monitors system health and creates notifications for problems.
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection, models
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from typing import List, Dict, Any
from .models import Notification, NotificationType, NotificationPriority
from .services import NotificationService
from accounts.models import User
from messaging.models import Message, Contact
from billing.models import SMSBalance

logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    Monitors system health and creates notifications for problems.
    """
    
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
        self.notification_service = NotificationService(tenant_id)
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Check overall system health and create notifications for issues.
        
        Returns:
            Dictionary with health status and issues found
        """
        issues = []
        warnings = []
        
        # Check database connectivity
        db_status = self._check_database_health()
        if not db_status['healthy']:
            issues.append(db_status)
        
        # Check SMS service health
        sms_status = self._check_sms_service_health()
        if not sms_status['healthy']:
            issues.append(sms_status)
        
        # Check message delivery rates
        delivery_status = self._check_message_delivery_health()
        if not delivery_status['healthy']:
            warnings.append(delivery_status)
        
        # Check SMS credit levels
        credit_status = self._check_sms_credit_health()
        if not credit_status['healthy']:
            warnings.append(credit_status)
        
        # Check failed messages
        failed_messages_status = self._check_failed_messages_health()
        if not failed_messages_status['healthy']:
            issues.append(failed_messages_status)
        
        # Check user activity
        activity_status = self._check_user_activity_health()
        if not activity_status['healthy']:
            warnings.append(activity_status)
        
        # Create notifications for issues
        self._create_health_notifications(issues, warnings)
        
        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'timestamp': timezone.now()
        }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            with connection.cursor() as cursor:
                # Test basic query
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                # Check database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                # Check for long-running queries (simplified check)
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                return {
                    'component': 'Database',
                    'healthy': True,
                    'status': 'OK',
                    'details': {
                        'size_mb': round(db_size / (1024 * 1024), 2),
                        'table_count': table_count
                    }
                }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'component': 'Database',
                'healthy': False,
                'status': 'ERROR',
                'error': str(e),
                'priority': 'high'
            }
    
    def _check_sms_service_health(self) -> Dict[str, Any]:
        """Check SMS service health."""
        try:
            # Check recent SMS sending success rate
            recent_messages = Message.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            total_messages = recent_messages.count()
            if total_messages == 0:
                return {
                    'component': 'SMS Service',
                    'healthy': True,
                    'status': 'OK',
                    'details': {'message': 'No recent messages to check'}
                }
            
            successful_messages = recent_messages.filter(status='delivered').count()
            success_rate = (successful_messages / total_messages) * 100
            
            if success_rate < 80:
                return {
                    'component': 'SMS Service',
                    'healthy': False,
                    'status': 'WARNING',
                    'error': f'SMS success rate is {success_rate:.1f}% (below 80% threshold)',
                    'priority': 'medium',
                    'details': {
                        'success_rate': success_rate,
                        'total_messages': total_messages,
                        'successful_messages': successful_messages
                    }
                }
            
            return {
                'component': 'SMS Service',
                'healthy': True,
                'status': 'OK',
                'details': {
                    'success_rate': success_rate,
                    'total_messages': total_messages
                }
            }
        except Exception as e:
            logger.error(f"SMS service health check failed: {str(e)}")
            return {
                'component': 'SMS Service',
                'healthy': False,
                'status': 'ERROR',
                'error': str(e),
                'priority': 'high'
            }
    
    def _check_message_delivery_health(self) -> Dict[str, Any]:
        """Check message delivery health."""
        try:
            # Check for stuck messages (older than 1 hour, not delivered)
            stuck_messages = Message.objects.filter(
                created_at__lt=timezone.now() - timedelta(hours=1),
                status__in=['pending', 'sending']
            ).count()
            
            if stuck_messages > 10:
                return {
                    'component': 'Message Delivery',
                    'healthy': False,
                    'status': 'WARNING',
                    'error': f'{stuck_messages} messages stuck in pending/sending state',
                    'priority': 'medium',
                    'details': {'stuck_messages': stuck_messages}
                }
            
            return {
                'component': 'Message Delivery',
                'healthy': True,
                'status': 'OK',
                'details': {'stuck_messages': stuck_messages}
            }
        except Exception as e:
            logger.error(f"Message delivery health check failed: {str(e)}")
            return {
                'component': 'Message Delivery',
                'healthy': False,
                'status': 'ERROR',
                'error': str(e),
                'priority': 'high'
            }
    
    def _check_sms_credit_health(self) -> Dict[str, Any]:
        """Check SMS credit health across all tenants."""
        try:
            low_credit_tenants = []
            
            for balance in SMSBalance.objects.all():
                if balance.credits < 100:  # Low credit threshold
                    low_credit_tenants.append({
                        'tenant': balance.tenant.name,
                        'credits': balance.credits
                    })
            
            if low_credit_tenants:
                return {
                    'component': 'SMS Credits',
                    'healthy': False,
                    'status': 'WARNING',
                    'error': f'{len(low_credit_tenants)} tenants have low SMS credits',
                    'priority': 'medium',
                    'details': {'low_credit_tenants': low_credit_tenants}
                }
            
            return {
                'component': 'SMS Credits',
                'healthy': True,
                'status': 'OK',
                'details': {'low_credit_tenants': 0}
            }
        except Exception as e:
            logger.error(f"SMS credit health check failed: {str(e)}")
            return {
                'component': 'SMS Credits',
                'healthy': False,
                'status': 'ERROR',
                'error': str(e),
                'priority': 'high'
            }
    
    def _check_failed_messages_health(self) -> Dict[str, Any]:
        """Check for high number of failed messages."""
        try:
            # Check failed messages in last 24 hours
            recent_failed = Message.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24),
                status='failed'
            ).count()
            
            if recent_failed > 50:  # High failure threshold
                return {
                    'component': 'Failed Messages',
                    'healthy': False,
                    'status': 'ERROR',
                    'error': f'{recent_failed} messages failed in the last 24 hours',
                    'priority': 'high',
                    'details': {'failed_messages': recent_failed}
                }
            
            return {
                'component': 'Failed Messages',
                'healthy': True,
                'status': 'OK',
                'details': {'failed_messages': recent_failed}
            }
        except Exception as e:
            logger.error(f"Failed messages health check failed: {str(e)}")
            return {
                'component': 'Failed Messages',
                'healthy': False,
                'status': 'ERROR',
                'error': str(e),
                'priority': 'high'
            }
    
    def _check_user_activity_health(self) -> Dict[str, Any]:
        """Check user activity patterns."""
        try:
            # Check for users who haven't logged in recently
            inactive_users = User.objects.filter(
                last_login__lt=timezone.now() - timedelta(days=30)
            ).count()
            
            total_users = User.objects.count()
            inactive_percentage = (inactive_users / total_users) * 100 if total_users > 0 else 0
            
            if inactive_percentage > 70:  # High inactivity threshold
                return {
                    'component': 'User Activity',
                    'healthy': False,
                    'status': 'WARNING',
                    'error': f'{inactive_percentage:.1f}% of users inactive for 30+ days',
                    'priority': 'low',
                    'details': {
                        'inactive_users': inactive_users,
                        'total_users': total_users,
                        'inactive_percentage': inactive_percentage
                    }
                }
            
            return {
                'component': 'User Activity',
                'healthy': True,
                'status': 'OK',
                'details': {
                    'inactive_users': inactive_users,
                    'inactive_percentage': inactive_percentage
                }
            }
        except Exception as e:
            logger.error(f"User activity health check failed: {str(e)}")
            return {
                'component': 'User Activity',
                'healthy': False,
                'status': 'ERROR',
                'error': str(e),
                'priority': 'high'
            }
    
    def _create_health_notifications(self, issues: List[Dict], warnings: List[Dict]):
        """Create notifications for system health issues."""
        # Get all admin users
        admin_users = User.objects.filter(is_superuser=True)
        
        # Create notifications for issues
        for issue in issues:
            priority = issue.get('priority', 'high')
            notification_type = NotificationType.ERROR if issue['status'] == 'ERROR' else NotificationType.WARNING
            
            for admin in admin_users:
                self.notification_service.create_notification(
                    user=admin,
                    title=f"System Issue: {issue['component']}",
                    message=f"{issue['component']} is experiencing issues: {issue['error']}",
                    notification_type=notification_type,
                    priority=priority,
                    data=issue.get('details', {}),
                    action_text="View Details",
                    is_system=True,
                    is_auto_generated=True
                )
        
        # Create notifications for warnings
        for warning in warnings:
            priority = warning.get('priority', 'medium')
            
            for admin in admin_users:
                self.notification_service.create_notification(
                    user=admin,
                    title=f"System Warning: {warning['component']}",
                    message=f"{warning['component']} needs attention: {warning['error']}",
                    notification_type=NotificationType.WARNING,
                    priority=priority,
                    data=warning.get('details', {}),
                    action_text="View Details",
                    is_system=True,
                    is_auto_generated=True
                )
    
    def create_problem_notification(self, problem_type: str, description: str, 
                                  user: User = None, data: Dict = None, 
                                  priority: str = 'medium') -> Notification:
        """
        Create a notification for a specific problem.
        
        Args:
            problem_type: Type of problem (e.g., 'SMS_FAILURE', 'PAYMENT_ERROR')
            description: Description of the problem
            user: User to notify (if None, notifies all admins)
            data: Additional data about the problem
            priority: Priority level
        
        Returns:
            Created notification
        """
        if user is None:
            # Notify all admin users
            admin_users = User.objects.filter(is_superuser=True)
            notifications = []
            
            for admin in admin_users:
                notification = self.notification_service.create_notification(
                    user=admin,
                    title=f"System Problem: {problem_type}",
                    message=description,
                    notification_type=NotificationType.ERROR,
                    priority=priority,
                    data=data or {},
                    action_text="View Details",
                    is_system=True,
                    is_auto_generated=True
                )
                notifications.append(notification)
            
            return notifications[0] if notifications else None
        else:
            return self.notification_service.create_notification(
                user=user,
                title=f"Problem: {problem_type}",
                message=description,
                notification_type=NotificationType.ERROR,
                priority=priority,
                data=data or {},
                action_text="View Details",
                is_system=True,
                is_auto_generated=True
            )
    
    def get_real_notifications(self, user: User, limit: int = 20) -> List[Notification]:
        """
        Get real notifications for a user, including system-generated ones.
        
        Args:
            user: User to get notifications for
            limit: Maximum number of notifications to return
        
        Returns:
            List of notifications
        """
        # Get user's notifications
        user_notifications = Notification.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]
        
        # If user is admin, also include system notifications
        if user.is_superuser:
            system_notifications = Notification.objects.filter(
                is_system=True
            ).order_by('-created_at')[:limit//2]
            
            # Combine and sort by creation date
            all_notifications = list(user_notifications) + list(system_notifications)
            all_notifications.sort(key=lambda x: x.created_at, reverse=True)
            return all_notifications[:limit]
        
        return list(user_notifications)
    
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """
        Clean up old notifications.
        
        Args:
            days: Number of days to keep notifications
        
        Returns:
            Number of notifications deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete old read notifications
        old_notifications = Notification.objects.filter(
            created_at__lt=cutoff_date,
            status='read'
        )
        
        count = old_notifications.count()
        old_notifications.delete()
        
        logger.info(f"Cleaned up {count} old notifications")
        return count
