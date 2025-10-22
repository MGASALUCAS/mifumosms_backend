"""
Activity tracking views for dashboard.
Provides recent activity feed and performance overview data.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Contact, Message, Campaign, Conversation, Template
from .models_sms import SMSMessage, SMSDeliveryReport
from tenants.models import Tenant
from accounts.models import User

logger = logging.getLogger(__name__)


def _get_human_time(dt):
    """Convert datetime to human readable format."""
    if not dt:
        return "Unknown"
    
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} min ago"
    else:
        return "Just now"


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """
    Get recent activity feed for the dashboard.
    
    GET /api/messaging/activity/recent/
    
    Response:
    {
        "success": true,
        "data": {
            "activities": [
                {
                    "id": "uuid",
                    "type": "conversation_reply",
                    "title": "John Kamau replied to conversation Kenya Coffee Exports",
                    "description": "New message in conversation",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "time_ago": "2 min ago",
                    "is_live": true,
                    "metadata": {
                        "conversation_id": "uuid",
                        "contact_name": "John Kamau",
                        "conversation_subject": "Kenya Coffee Exports"
                    }
                },
                {
                    "id": "uuid",
                    "type": "campaign_completed",
                    "title": "System completed campaign Mother's Day Promotion",
                    "description": "98% delivered",
                    "timestamp": "2024-01-15T10:15:00Z",
                    "time_ago": "15 min ago",
                    "is_live": false,
                    "metadata": {
                        "campaign_id": "uuid",
                        "campaign_name": "Mother's Day Promotion",
                        "delivery_rate": 98
                    }
                }
            ],
            "has_more": true,
            "total_count": 25
        }
    }
    """
    try:
        user = request.user
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get query parameters
        limit = int(request.GET.get('limit', 10))
        activity_type = request.GET.get('type')  # Filter by activity type
        
        activities = []
        
        # 1. Recent conversation replies (messages)
        if not activity_type or activity_type == 'conversation_reply':
            recent_messages = Message.objects.filter(
                tenant=tenant,
                direction='in'  # Incoming messages (replies)
            ).select_related('conversation__contact').order_by('-created_at')[:limit]
            
            for message in recent_messages:
                activities.append({
                    'id': f"msg_{message.id}",
                    'type': 'conversation_reply',
                    'title': f"{message.conversation.contact.name} replied to conversation {message.conversation.subject or 'Untitled'}",
                    'description': f"New message: {message.text[:50]}{'...' if len(message.text) > 50 else ''}",
                    'timestamp': message.created_at.isoformat(),
                    'time_ago': _get_human_time(message.created_at),
                    'is_live': (timezone.now() - message.created_at).seconds < 300,  # Live if within 5 minutes
                    'metadata': {
                        'conversation_id': str(message.conversation.id),
                        'contact_name': message.conversation.contact.name,
                        'conversation_subject': message.conversation.subject or 'Untitled',
                        'message_id': str(message.id)
                    }
                })
        
        # 2. Campaign completions
        if not activity_type or activity_type == 'campaign_completed':
            recent_campaigns = Campaign.objects.filter(
                created_by=user,
                tenant=tenant,
                status='completed'
            ).order_by('-updated_at')[:limit]
            
            for campaign in recent_campaigns:
                delivery_rate = 0
                if campaign.total_recipients and campaign.total_recipients > 0:
                    delivery_rate = round((campaign.delivered_count or 0) / campaign.total_recipients * 100)
                
                activities.append({
                    'id': f"camp_{campaign.id}",
                    'type': 'campaign_completed',
                    'title': f"System completed campaign {campaign.name}",
                    'description': f"{delivery_rate}% delivered",
                    'timestamp': campaign.updated_at.isoformat(),
                    'time_ago': _get_human_time(campaign.updated_at),
                    'is_live': False,
                    'metadata': {
                        'campaign_id': str(campaign.id),
                        'campaign_name': campaign.name,
                        'delivery_rate': delivery_rate,
                        'sent_count': campaign.sent_count or 0,
                        'delivered_count': campaign.delivered_count or 0
                    }
                })
        
        # 3. Contact additions
        if not activity_type or activity_type == 'contact_added':
            recent_contacts = Contact.objects.filter(
                created_by=user,
                tenant=tenant
            ).order_by('-created_at')[:limit]
            
            # Group contacts by creation time (same hour)
            contact_groups = {}
            for contact in recent_contacts:
                hour_key = contact.created_at.replace(minute=0, second=0, microsecond=0)
                if hour_key not in contact_groups:
                    contact_groups[hour_key] = []
                contact_groups[hour_key].append(contact)
            
            for hour, contacts in list(contact_groups.items())[:limit]:
                if len(contacts) == 1:
                    contact = contacts[0]
                    activities.append({
                        'id': f"contact_{contact.id}",
                        'type': 'contact_added',
                        'title': f"{contact.name} added to contacts",
                        'description': f"New contact: {contact.phone_e164}",
                        'timestamp': contact.created_at.isoformat(),
                        'time_ago': _get_human_time(contact.created_at),
                        'is_live': False,
                        'metadata': {
                            'contact_id': str(contact.id),
                            'contact_name': contact.name,
                            'phone': contact.phone_e164
                        }
                    })
                else:
                    # Multiple contacts added in same hour
                    activities.append({
                        'id': f"contacts_{hour.isoformat()}",
                        'type': 'contacts_added',
                        'title': f"Added {len(contacts)} new contacts",
                        'description': f"Bulk import completed",
                        'timestamp': hour.isoformat(),
                        'time_ago': _get_human_time(hour),
                        'is_live': False,
                        'metadata': {
                            'count': len(contacts),
                            'contacts': [str(c.id) for c in contacts[:5]]  # First 5 contact IDs
                        }
                    })
        
        # 4. Template approvals
        if not activity_type or activity_type == 'template_approved':
            recent_templates = Template.objects.filter(
                created_by=user,
                tenant=tenant,
                approved=True
            ).order_by('-updated_at')[:limit]
            
            for template in recent_templates:
                activities.append({
                    'id': f"template_{template.id}",
                    'type': 'template_approved',
                    'title': f"{user.first_name or user.email} approved template {template.name}",
                    'description': f"{template.category_display} - {template.language_display}",
                    'timestamp': template.updated_at.isoformat(),
                    'time_ago': _get_human_time(template.updated_at),
                    'is_live': False,
                    'metadata': {
                        'template_id': str(template.id),
                        'template_name': template.name,
                        'category': template.category,
                        'language': template.language,
                        'channel': template.channel
                    }
                })
        
        # 5. Campaign starts
        if not activity_type or activity_type == 'campaign_started':
            started_campaigns = Campaign.objects.filter(
                created_by=user,
                tenant=tenant,
                status='running'
            ).order_by('-created_at')[:limit]
            
            for campaign in started_campaigns:
                activities.append({
                    'id': f"camp_start_{campaign.id}",
                    'type': 'campaign_started',
                    'title': f"Campaign {campaign.name} started",
                    'description': f"Targeting {campaign.total_recipients or 0} recipients",
                    'timestamp': campaign.created_at.isoformat(),
                    'time_ago': _get_human_time(campaign.created_at),
                    'is_live': (timezone.now() - campaign.created_at).seconds < 300,
                    'metadata': {
                        'campaign_id': str(campaign.id),
                        'campaign_name': campaign.name,
                        'recipient_count': campaign.total_recipients or 0
                    }
                })
        
        # Sort all activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        activities = activities[:limit]
        
        # Check if there are more activities
        total_count = len(activities)
        has_more = total_count >= limit
        
        return Response({
            'success': True,
            'data': {
                'activities': activities,
                'has_more': has_more,
                'total_count': total_count,
                'live_count': len([a for a in activities if a.get('is_live', False)])
            }
        })
        
    except Exception as e:
        logger.error(f"Error in recent_activity: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve recent activity',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_overview(request):
    """
    Get performance overview data for the dashboard.
    
    GET /api/messaging/performance/overview/
    
    Response:
    {
        "success": true,
        "data": {
            "metrics": {
                "total_messages": 1250,
                "delivery_rate": 96.8,
                "response_rate": 45.2,
                "active_conversations": 25,
                "campaign_success_rate": 94.2
            },
            "charts": {
                "message_volume": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "data": [100, 150, 200, 180, 220]
                },
                "delivery_rates": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "data": [95, 96, 97, 96, 98]
                }
            },
            "coming_soon": true
        }
    }
    """
    try:
        user = request.user
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate metrics
        total_messages = Message.objects.filter(tenant=tenant).count()
        delivered_messages = Message.objects.filter(
            tenant=tenant,
            status__in=['delivered', 'read']
        ).count()
        
        delivery_rate = 0
        if total_messages > 0:
            delivery_rate = round((delivered_messages / total_messages) * 100, 1)
        
        # Response rate (messages with replies)
        conversations_with_replies = Conversation.objects.filter(
            tenant=tenant,
            message_count__gt=1
        ).count()
        total_conversations = Conversation.objects.filter(tenant=tenant).count()
        
        response_rate = 0
        if total_conversations > 0:
            response_rate = round((conversations_with_replies / total_conversations) * 100, 1)
        
        # Active conversations (open status)
        active_conversations = Conversation.objects.filter(
            tenant=tenant,
            status='open'
        ).count()
        
        # Campaign success rate
        completed_campaigns = Campaign.objects.filter(
            created_by=user,
            tenant=tenant,
            status='completed'
        )
        
        campaign_success_rate = 0
        if completed_campaigns.exists():
            total_sent = sum(c.sent_count or 0 for c in completed_campaigns)
            total_delivered = sum(c.delivered_count or 0 for c in completed_campaigns)
            if total_sent > 0:
                campaign_success_rate = round((total_delivered / total_sent) * 100, 1)
        
        # Generate sample chart data (in real implementation, this would come from actual data)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        message_volume = [100, 150, 200, 180, 220]
        delivery_rates = [95, 96, 97, 96, 98]
        
        return Response({
            'success': True,
            'data': {
                'metrics': {
                    'total_messages': total_messages,
                    'delivery_rate': delivery_rate,
                    'response_rate': response_rate,
                    'active_conversations': active_conversations,
                    'campaign_success_rate': campaign_success_rate
                },
                'charts': {
                    'message_volume': {
                        'labels': months,
                        'data': message_volume
                    },
                    'delivery_rates': {
                        'labels': months,
                        'data': delivery_rates
                    }
                },
                'coming_soon': True  # As shown in the UI
            }
        })
        
    except Exception as e:
        logger.error(f"Error in performance_overview: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve performance overview',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_statistics(request):
    """
    Get activity statistics for the dashboard.
    
    GET /api/messaging/activity/statistics/
    
    Response:
    {
        "success": true,
        "data": {
            "today": {
                "messages_sent": 25,
                "messages_received": 15,
                "conversations_started": 5,
                "campaigns_launched": 2
            },
            "this_week": {
                "messages_sent": 180,
                "messages_received": 120,
                "conversations_started": 35,
                "campaigns_launched": 8
            },
            "this_month": {
                "messages_sent": 750,
                "messages_received": 500,
                "conversations_started": 150,
                "campaigns_launched": 25
            }
        }
    }
    """
    try:
        user = request.user
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Today's statistics
        today_stats = {
            'messages_sent': Message.objects.filter(
                tenant=tenant,
                direction='out',
                created_at__gte=today_start
            ).count(),
            'messages_received': Message.objects.filter(
                tenant=tenant,
                direction='in',
                created_at__gte=today_start
            ).count(),
            'conversations_started': Conversation.objects.filter(
                tenant=tenant,
                created_at__gte=today_start
            ).count(),
            'campaigns_launched': Campaign.objects.filter(
                created_by=user,
                tenant=tenant,
                created_at__gte=today_start
            ).count()
        }
        
        # This week's statistics
        week_stats = {
            'messages_sent': Message.objects.filter(
                tenant=tenant,
                direction='out',
                created_at__gte=week_start
            ).count(),
            'messages_received': Message.objects.filter(
                tenant=tenant,
                direction='in',
                created_at__gte=week_start
            ).count(),
            'conversations_started': Conversation.objects.filter(
                tenant=tenant,
                created_at__gte=week_start
            ).count(),
            'campaigns_launched': Campaign.objects.filter(
                created_by=user,
                tenant=tenant,
                created_at__gte=week_start
            ).count()
        }
        
        # This month's statistics
        month_stats = {
            'messages_sent': Message.objects.filter(
                tenant=tenant,
                direction='out',
                created_at__gte=month_start
            ).count(),
            'messages_received': Message.objects.filter(
                tenant=tenant,
                direction='in',
                created_at__gte=month_start
            ).count(),
            'conversations_started': Conversation.objects.filter(
                tenant=tenant,
                created_at__gte=month_start
            ).count(),
            'campaigns_launched': Campaign.objects.filter(
                created_by=user,
                tenant=tenant,
                created_at__gte=month_start
            ).count()
        }
        
        return Response({
            'success': True,
            'data': {
                'today': today_stats,
                'this_week': week_stats,
                'this_month': month_stats
            }
        })
        
    except Exception as e:
        logger.error(f"Error in activity_statistics: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve activity statistics',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
