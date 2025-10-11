"""
Dashboard views for Mifumo WMS.
Provides comprehensive analytics and dashboard data.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Contact, Message, Campaign, Conversation
from .models_sms import SMSMessage, SMSDeliveryReport
from tenants.models import Tenant

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Get comprehensive dashboard overview data.

    GET /api/messaging/dashboard/overview/

    Response:
    {
        "success": true,
        "data": {
            "metrics": {
                "total_messages": 12450,
                "active_contacts": 3240,
                "campaign_success_rate": 94.2,
                "revenue_this_month": 4280
            },
            "recent_campaigns": [...],
            "message_stats": {
                "today": 150,
                "this_week": 1200,
                "this_month": 4500
            },
            "contact_stats": {
                "total": 5000,
                "active": 3240,
                "new_this_month": 150
            }
        }
    }
    """
    try:
        user = request.user

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Message statistics
        total_messages = Message.objects.filter(conversation__contact__created_by=user).count()
        messages_today = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=today_start
        ).count()
        messages_this_week = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=week_start
        ).count()
        messages_this_month = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=month_start
        ).count()

        # Contact statistics
        total_contacts = Contact.objects.filter(created_by=user).count()
        active_contacts = Contact.objects.filter(created_by=user, is_active=True).count()
        new_contacts_this_month = Contact.objects.filter(
            created_by=user,
            created_at__gte=month_start
        ).count()

        # Campaign statistics
        total_campaigns = Campaign.objects.filter(created_by=user).count()
        completed_campaigns = Campaign.objects.filter(
            created_by=user,
            status='completed'
        ).count()

        # Calculate campaign success rate
        campaign_success_rate = 0
        if total_campaigns > 0:
            successful_campaigns = Campaign.objects.filter(
                created_by=user,
                status='completed'
            ).aggregate(
                total_sent=Sum('sent_count', default=0),
                total_delivered=Sum('delivered_count', default=0)
            )

            if successful_campaigns['total_sent'] > 0:
                campaign_success_rate = round(
                    (successful_campaigns['total_delivered'] / successful_campaigns['total_sent']) * 100, 1
                )

        # Sender ID calculation
        sender_ids_this_month = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=month_start
        ).values('provider').distinct().count()

        # Recent campaigns (last 5)
        recent_campaigns = Campaign.objects.filter(created_by=user).order_by('-created_at')[:5]
        campaigns_data = []

        for campaign in recent_campaigns:
            campaigns_data.append({
                'id': str(campaign.id),
                'name': campaign.name,
                'type': 'SMS' if campaign.template and 'sms' in campaign.template.category.lower() else 'WhatsApp',
                'status': campaign.status,
                'sent': campaign.sent_count or 0,
                'delivered': campaign.delivered_count or 0,
                'opened': campaign.read_count or 0,
                'progress': min(100, int((campaign.sent_count or 0) / max(1, campaign.total_recipients or 1) * 100)),
                'created_at': campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                'created_at_human': _get_human_time(campaign.created_at)
            })

        # Message trends
        message_trends = {
            'today': messages_today,
            'this_week': messages_this_week,
            'this_month': messages_this_month,
            'growth_rate': _calculate_growth_rate(messages_this_month, messages_this_week)
        }

        # Contact trends
        contact_trends = {
            'total': total_contacts,
            'active': active_contacts,
            'new_this_month': new_contacts_this_month,
            'growth_rate': _calculate_growth_rate(active_contacts, total_contacts)
        }

        return Response({
            'success': True,
            'data': {
                'metrics': {
                    'total_messages': total_messages,
                    'active_contacts': active_contacts,
                    'campaign_success_rate': campaign_success_rate,
                    'sender_ids_this_month': sender_ids_this_month
                },
                'recent_campaigns': campaigns_data,
                'message_stats': message_trends,
                'contact_stats': contact_trends,
                'last_updated': now.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Dashboard overview error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve dashboard data',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    """
    Get detailed metrics for dashboard cards.

    GET /api/messaging/dashboard/metrics/

    Response:
    {
        "success": true,
        "data": {
            "total_messages": {
                "value": 12450,
                "change": "+12.5%",
                "change_type": "positive",
                "description": "Last 30 days"
            },
            "active_contacts": {
                "value": 3240,
                "change": "+8.2%",
                "change_type": "positive",
                "description": "Engaged this month"
            },
            "campaign_success": {
                "value": "94.2%",
                "change": "+2.1%",
                "change_type": "positive",
                "description": "Delivery rate"
            },
            "revenue": {
                "value": "Tsh 4,280",
                "change": "+18.7%",
                "change_type": "positive",
                "description": "This month"
            }
        }
    }
    """
    try:
        user = request.user

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        # Total messages (last 30 days)
        messages_30_days = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=now - timedelta(days=30)
        ).count()

        messages_60_days = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=now - timedelta(days=60),
            created_at__lt=now - timedelta(days=30)
        ).count()

        messages_change = _calculate_percentage_change(messages_30_days, messages_60_days)

        # Active contacts (engaged this month)
        active_contacts = Contact.objects.filter(
            created_by=user,
            is_active=True,
            last_contacted_at__gte=month_start
        ).count()

        last_month_active = Contact.objects.filter(
            created_by=user,
            is_active=True,
            last_contacted_at__gte=last_month_start,
            last_contacted_at__lt=month_start
        ).count()

        contacts_change = _calculate_percentage_change(active_contacts, last_month_active)

        # Campaign success rate
        campaigns_this_month = Campaign.objects.filter(
            created_by=user,
            created_at__gte=month_start
        )

        total_sent = campaigns_this_month.aggregate(total_sent=Sum('sent_count'))['total_sent'] or 0
        total_delivered = campaigns_this_month.aggregate(total_delivered=Sum('delivered_count'))['total_delivered'] or 0

        success_rate = round((total_delivered / max(1, total_sent)) * 100, 1) if total_sent > 0 else 0

        # Previous month for comparison
        campaigns_last_month = Campaign.objects.filter(
            created_by=user,
            created_at__gte=last_month_start,
            created_at__lt=month_start
        )

        last_month_sent = campaigns_last_month.aggregate(last_month_sent=Sum('sent_count'))['last_month_sent'] or 0
        last_month_delivered = campaigns_last_month.aggregate(last_month_delivered=Sum('delivered_count'))['last_month_delivered'] or 0
        last_month_success_rate = round((last_month_delivered / max(1, last_month_sent)) * 100, 1) if last_month_sent > 0 else 0

        success_change = _calculate_percentage_change(success_rate, last_month_success_rate)

        # Sender ID statistics
        sender_ids_this_month = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=month_start
        ).values('provider').distinct().count()

        sender_ids_last_month = Message.objects.filter(
            conversation__contact__created_by=user,
            created_at__gte=last_month_start,
            created_at__lt=month_start
        ).values('provider').distinct().count()

        sender_id_change = _calculate_percentage_change(sender_ids_this_month, sender_ids_last_month)

        return Response({
            'success': True,
            'data': {
                'total_messages': {
                    'value': messages_30_days,
                    'change': f"{messages_change['sign']}{messages_change['percentage']:.1f}%",
                    'change_type': messages_change['type'],
                    'description': 'Last 30 days'
                },
                'active_contacts': {
                    'value': active_contacts,
                    'change': f"{contacts_change['sign']}{contacts_change['percentage']:.1f}%",
                    'change_type': contacts_change['type'],
                    'description': 'Engaged this month'
                },
                'campaign_success': {
                    'value': f"{success_rate}%",
                    'change': f"{success_change['sign']}{success_change['percentage']:.1f}%",
                    'change_type': success_change['type'],
                    'description': 'Delivery rate'
                },
                'sender_id': {
                    'value': sender_ids_this_month,
                    'change': f"{sender_id_change['sign']}{sender_id_change['percentage']:.1f}%",
                    'change_type': sender_id_change['type'],
                    'description': 'Active this month'
                }
            }
        })

    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve dashboard metrics',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_human_time(dt):
    """Convert datetime to human readable format."""
    now = timezone.now()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def _calculate_growth_rate(current, previous):
    """Calculate growth rate percentage."""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 1)


def _calculate_percentage_change(current, previous):
    """Calculate percentage change with type."""
    if previous == 0:
        change = 100 if current > 0 else 0
        return {
            'percentage': change,
            'sign': '+' if current > 0 else '',
            'type': 'positive' if current > 0 else 'neutral'
        }

    change = ((current - previous) / previous) * 100
    return {
        'percentage': abs(change),
        'sign': '+' if change > 0 else '-',
        'type': 'positive' if change > 0 else 'negative' if change < 0 else 'neutral'
    }
