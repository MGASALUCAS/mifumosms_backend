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
from billing.models import SMSBalance, SMSPackage

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
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Message statistics (tenant-based)
        total_messages = Message.objects.filter(tenant=tenant).count()
        messages_today = Message.objects.filter(
            tenant=tenant,
            created_at__gte=today_start
        ).count()
        messages_this_week = Message.objects.filter(
            tenant=tenant,
            created_at__gte=week_start
        ).count()
        messages_this_month = Message.objects.filter(
            tenant=tenant,
            created_at__gte=month_start
        ).count()

        # SMS Message statistics
        total_sms_messages = SMSMessage.objects.filter(tenant=tenant).count()
        sms_messages_today = SMSMessage.objects.filter(
            tenant=tenant,
            created_at__gte=today_start
        ).count()
        sms_messages_this_month = SMSMessage.objects.filter(
            tenant=tenant,
            created_at__gte=month_start
        ).count()

        # Contact statistics (tenant-based)
        total_contacts = Contact.objects.filter(tenant=tenant).count()
        active_contacts = Contact.objects.filter(tenant=tenant, is_active=True).count()
        new_contacts_this_month = Contact.objects.filter(
            tenant=tenant,
            created_at__gte=month_start
        ).count()

        # Campaign statistics (user-based, not tenant-based)
        total_campaigns = Campaign.objects.filter(created_by=user).count()
        completed_campaigns = Campaign.objects.filter(
            created_by=user,
            status='completed'
        ).count()

        # Calculate campaign success rate (user-based)
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

        # SMS Delivery Rate
        sms_delivery_rate = 0
        if total_sms_messages > 0:
            delivered_sms = SMSMessage.objects.filter(tenant=tenant, status='delivered').count()
            sms_delivery_rate = round((delivered_sms / total_sms_messages) * 100, 1)

        # Billing statistics
        sms_balance = SMSBalance.objects.filter(tenant=tenant).first()
        current_credits = sms_balance.credits if sms_balance else 0
        total_purchased = sms_balance.total_purchased if sms_balance else 0

        # Sender ID calculation - count active sender IDs for the tenant
        from messaging.models_sms import SMSSenderID
        sender_ids_this_month = SMSSenderID.objects.filter(
            tenant=tenant,
            status='active'
        ).count()

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
                    'total_sms_messages': total_sms_messages,
                    'active_contacts': active_contacts,
                    'campaign_success_rate': campaign_success_rate,
                    'sms_delivery_rate': sms_delivery_rate,
                    'current_credits': current_credits,
                    'total_purchased': total_purchased,
                    'sender_ids_this_month': sender_ids_this_month
                },
                'recent_campaigns': campaigns_data,
                'message_stats': message_trends,
                'sms_stats': {
                    'today': sms_messages_today,
                    'this_month': sms_messages_this_month,
                    'delivery_rate': sms_delivery_rate
                },
                'contact_stats': contact_trends,
                'billing_stats': {
                    'current_credits': current_credits,
                    'total_purchased': total_purchased,
                    'credits_used': total_purchased - current_credits if sms_balance else 0
                },
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
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        # Total messages (last 30 days) - tenant-based
        messages_30_days = Message.objects.filter(
            tenant=tenant,
            created_at__gte=now - timedelta(days=30)
        ).count()

        messages_60_days = Message.objects.filter(
            tenant=tenant,
            created_at__gte=now - timedelta(days=60),
            created_at__lt=now - timedelta(days=30)
        ).count()

        messages_change = _calculate_percentage_change(messages_30_days, messages_60_days)

        # SMS messages (last 30 days)
        sms_messages_30_days = SMSMessage.objects.filter(
            tenant=tenant,
            created_at__gte=now - timedelta(days=30)
        ).count()

        sms_messages_60_days = SMSMessage.objects.filter(
            tenant=tenant,
            created_at__gte=now - timedelta(days=60),
            created_at__lt=now - timedelta(days=30)
        ).count()

        sms_messages_change = _calculate_percentage_change(sms_messages_30_days, sms_messages_60_days)

        # Active contacts (engaged this month) - tenant-based
        active_contacts = Contact.objects.filter(
            tenant=tenant,
            is_active=True
        ).count()

        # For comparison, get active contacts from last month
        last_month_active = Contact.objects.filter(
            tenant=tenant,
            is_active=True,
            created_at__gte=last_month_start,
            created_at__lt=month_start
        ).count()

        contacts_change = _calculate_percentage_change(active_contacts, last_month_active)

        # Campaign success rate (user-based)
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

        # SMS Delivery Rate
        sms_delivered_this_month = SMSMessage.objects.filter(
            tenant=tenant,
            status='delivered',
            created_at__gte=month_start
        ).count()

        sms_delivered_last_month = SMSMessage.objects.filter(
            tenant=tenant,
            status='delivered',
            created_at__gte=last_month_start,
            created_at__lt=month_start
        ).count()

        sms_delivery_rate = round((sms_delivered_this_month / max(1, sms_messages_30_days)) * 100, 1) if sms_messages_30_days > 0 else 0
        last_month_sms_delivery_rate = round((sms_delivered_last_month / max(1, sms_messages_60_days)) * 100, 1) if sms_messages_60_days > 0 else 0
        sms_delivery_change = _calculate_percentage_change(sms_delivery_rate, last_month_sms_delivery_rate)

        # Billing metrics
        sms_balance = SMSBalance.objects.filter(tenant=tenant).first()
        current_credits = sms_balance.credits if sms_balance else 0
        total_purchased = sms_balance.total_purchased if sms_balance else 0

        # Calculate credits used this month (approximate)
        credits_used_this_month = max(0, total_purchased - current_credits)
        credits_used_last_month = 0  # This would need historical tracking for accurate comparison
        credits_change = _calculate_percentage_change(credits_used_this_month, credits_used_last_month)

        return Response({
            'success': True,
            'data': {
                'total_messages': {
                    'value': messages_30_days,
                    'change': f"{messages_change['sign']}{messages_change['percentage']:.1f}%",
                    'change_type': messages_change['type'],
                    'description': 'Last 30 days'
                },
                'sms_messages': {
                    'value': sms_messages_30_days,
                    'change': f"{sms_messages_change['sign']}{sms_messages_change['percentage']:.1f}%",
                    'change_type': sms_messages_change['type'],
                    'description': 'SMS last 30 days'
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
                'sms_delivery_rate': {
                    'value': f"{sms_delivery_rate}%",
                    'change': f"{sms_delivery_change['sign']}{sms_delivery_change['percentage']:.1f}%",
                    'change_type': sms_delivery_change['type'],
                    'description': 'SMS delivery rate'
                },
                'current_credits': {
                    'value': current_credits,
                    'change': f"{credits_change['sign']}{credits_change['percentage']:.1f}%",
                    'change_type': credits_change['type'],
                    'description': 'Available credits'
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_comprehensive(request):
    """
    Get comprehensive dashboard data with all metrics.
    
    GET /api/messaging/dashboard/comprehensive/
    
    This endpoint combines overview and metrics data for a complete dashboard view.
    """
    try:
        user = request.user
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        # Get all metrics in one go for better performance
        metrics_data = {
            # Messages
            'total_messages': Message.objects.filter(tenant=tenant).count(),
            'messages_today': Message.objects.filter(tenant=tenant, created_at__gte=today_start).count(),
            'messages_this_week': Message.objects.filter(tenant=tenant, created_at__gte=week_start).count(),
            'messages_this_month': Message.objects.filter(tenant=tenant, created_at__gte=month_start).count(),
            
            # SMS Messages
            'total_sms_messages': SMSMessage.objects.filter(tenant=tenant).count(),
            'sms_messages_today': SMSMessage.objects.filter(tenant=tenant, created_at__gte=today_start).count(),
            'sms_messages_this_month': SMSMessage.objects.filter(tenant=tenant, created_at__gte=month_start).count(),
            'sms_delivered': SMSMessage.objects.filter(tenant=tenant, status='delivered').count(),
            'sms_failed': SMSMessage.objects.filter(tenant=tenant, status='failed').count(),
            
            # Contacts
            'total_contacts': Contact.objects.filter(tenant=tenant).count(),
            'active_contacts': Contact.objects.filter(tenant=tenant, is_active=True).count(),
            'new_contacts_this_month': Contact.objects.filter(tenant=tenant, created_at__gte=month_start).count(),
            
            # Campaigns
            'total_campaigns': Campaign.objects.filter(created_by=user).count(),
            'completed_campaigns': Campaign.objects.filter(created_by=user, status='completed').count(),
            'running_campaigns': Campaign.objects.filter(created_by=user, status='running').count(),
            
            # Billing
            'current_credits': 0,
            'total_purchased': 0,
            
            # Sender IDs
            'active_sender_ids': 0,
        }

        # Get billing data
        sms_balance = SMSBalance.objects.filter(tenant=tenant).first()
        if sms_balance:
            metrics_data['current_credits'] = sms_balance.credits
            metrics_data['total_purchased'] = sms_balance.total_purchased

        # Get sender ID count
        from messaging.models_sms import SMSSenderID
        metrics_data['active_sender_ids'] = SMSSenderID.objects.filter(
            tenant=tenant,
            status='active'
        ).count()

        # Calculate rates
        sms_delivery_rate = 0
        if metrics_data['total_sms_messages'] > 0:
            sms_delivery_rate = round((metrics_data['sms_delivered'] / metrics_data['total_sms_messages']) * 100, 1)

        campaign_success_rate = 0
        if metrics_data['total_campaigns'] > 0:
            campaign_aggregate = Campaign.objects.filter(created_by=user, status='completed').aggregate(
                total_sent=Sum('sent_count', default=0),
                total_delivered=Sum('delivered_count', default=0)
            )
            if campaign_aggregate['total_sent'] > 0:
                campaign_success_rate = round(
                    (campaign_aggregate['total_delivered'] / campaign_aggregate['total_sent']) * 100, 1
                )

        # Recent activity
        recent_campaigns = Campaign.objects.filter(created_by=user).order_by('-created_at')[:5]
        recent_messages = Message.objects.filter(tenant=tenant).order_by('-created_at')[:10]

        campaigns_data = []
        for campaign in recent_campaigns:
            campaigns_data.append({
                'id': str(campaign.id),
                'name': campaign.name,
                'status': campaign.status,
                'sent': campaign.sent_count or 0,
                'delivered': campaign.delivered_count or 0,
                'created_at': campaign.created_at.strftime('%Y-%m-%d %H:%M'),
                'created_at_human': _get_human_time(campaign.created_at)
            })

        messages_data = []
        for message in recent_messages:
            messages_data.append({
                'id': str(message.id),
                'content': message.text[:50] + '...' if len(message.text) > 50 else message.text,
                'direction': message.direction,
                'status': message.status,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
                'created_at_human': _get_human_time(message.created_at)
            })

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_messages': metrics_data['total_messages'],
                    'total_sms_messages': metrics_data['total_sms_messages'],
                    'active_contacts': metrics_data['active_contacts'],
                    'current_credits': metrics_data['current_credits'],
                    'sms_delivery_rate': sms_delivery_rate,
                    'campaign_success_rate': campaign_success_rate,
                },
                'metrics': {
                    'messages': {
                        'today': metrics_data['messages_today'],
                        'this_week': metrics_data['messages_this_week'],
                        'this_month': metrics_data['messages_this_month'],
                        'total': metrics_data['total_messages']
                    },
                    'sms': {
                        'today': metrics_data['sms_messages_today'],
                        'this_month': metrics_data['sms_messages_this_month'],
                        'total': metrics_data['total_sms_messages'],
                        'delivered': metrics_data['sms_delivered'],
                        'failed': metrics_data['sms_failed'],
                        'delivery_rate': sms_delivery_rate
                    },
                    'contacts': {
                        'total': metrics_data['total_contacts'],
                        'active': metrics_data['active_contacts'],
                        'new_this_month': metrics_data['new_contacts_this_month']
                    },
                    'campaigns': {
                        'total': metrics_data['total_campaigns'],
                        'completed': metrics_data['completed_campaigns'],
                        'running': metrics_data['running_campaigns'],
                        'success_rate': campaign_success_rate
                    },
                    'billing': {
                        'current_credits': metrics_data['current_credits'],
                        'total_purchased': metrics_data['total_purchased'],
                        'credits_used': max(0, metrics_data['total_purchased'] - metrics_data['current_credits'])
                    }
                },
                'recent_activity': {
                    'campaigns': campaigns_data,
                    'messages': messages_data
                },
                'last_updated': now.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Comprehensive dashboard error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to retrieve comprehensive dashboard data',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
