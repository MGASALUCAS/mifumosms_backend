"""
Custom admin site configuration for Mifumo WMS.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


class MifumoAdminSite(AdminSite):
    """
    Custom admin site with enhanced dashboard and analytics.
    """
    site_header = "Mifumo WMS Administration"
    site_title = "Mifumo WMS Admin"
    index_title = "Welcome to Mifumo WMS Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
            path('sms-dashboard/', self.admin_view(self.sms_dashboard_view), name='sms_dashboard'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with dashboard widgets.
        """
        extra_context = extra_context or {}
        
        # Get analytics data
        from accounts.models import User
        from tenants.models import Tenant
        from messaging.models import Contact, Message, Campaign
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        
        # Tenant statistics
        total_tenants = Tenant.objects.count()
        active_tenants = Tenant.objects.filter(is_active=True).count()
        
        # Messaging statistics
        total_contacts = Contact.objects.count()
        total_messages = Message.objects.count()
        active_campaigns = Campaign.objects.filter(status='running').count()
        
        # Recent activity
        recent_messages = Message.objects.select_related('conversation__contact').order_by('-created_at')[:5]
        recent_users = User.objects.order_by('-created_at')[:5]
        
        # Message status breakdown
        message_stats = Message.objects.values('status').annotate(count=Count('id')).order_by('-count')
        
        extra_context.update({
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'total_contacts': total_contacts,
            'total_messages': total_messages,
            'active_campaigns': active_campaigns,
            'recent_messages': recent_messages,
            'recent_users': recent_users,
            'message_stats': message_stats,
        })
        
        return super().index(request, extra_context)
    
    def analytics_view(self, request):
        """
        Analytics dashboard view.
        """
        from accounts.models import User
        from messaging.models import Contact, Message, Campaign
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Date range for analytics
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # User growth
        user_growth = User.objects.filter(created_at__range=[start_date, end_date]).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Message volume
        message_volume = Message.objects.filter(created_at__range=[start_date, end_date]).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Campaign performance
        campaign_stats = Campaign.objects.values('status').annotate(count=Count('id'))
        
        context = {
            'user_growth': list(user_growth),
            'message_volume': list(message_volume),
            'campaign_stats': list(campaign_stats),
            'title': 'Analytics Dashboard',
        }
        
        return render(request, 'admin/analytics.html', context)
    
    def sms_dashboard_view(self, request):
        """
        SMS dashboard view.
        """
        from messaging.models_sms import SMSProvider, SMSMessage, SenderID
        
        # SMS statistics
        total_sms = SMSMessage.objects.count()
        sent_sms = SMSMessage.objects.filter(status='sent').count()
        delivered_sms = SMSMessage.objects.filter(status='delivered').count()
        failed_sms = SMSMessage.objects.filter(status='failed').count()
        
        # Provider statistics
        provider_stats = SMSProvider.objects.annotate(
            message_count=Count('smsmessage')
        ).order_by('-message_count')
        
        # Sender ID statistics
        sender_stats = SenderID.objects.annotate(
            message_count=Count('smsmessage')
        ).order_by('-message_count')
        
        context = {
            'total_sms': total_sms,
            'sent_sms': sent_sms,
            'delivered_sms': delivered_sms,
            'failed_sms': failed_sms,
            'provider_stats': provider_stats,
            'sender_stats': sender_stats,
            'title': 'SMS Dashboard',
        }
        
        return render(request, 'admin/sms_dashboard.html', context)


# Create custom admin site instance
admin_site = MifumoAdminSite(name='mifumo_admin')

# Register all models with the custom admin site
from django.contrib.auth.models import User, Group
from accounts.models import User as CustomUser, UserProfile
from tenants.models import Tenant, Membership
from messaging.models import Contact, Segment, Template, Conversation, Message, Attachment, Campaign, Flow

# Register Django's built-in models
admin_site.register(User)
admin_site.register(Group)

# Register custom models
admin_site.register(CustomUser)
admin_site.register(UserProfile)
admin_site.register(Tenant)
admin_site.register(Membership)
admin_site.register(Contact)
admin_site.register(Segment)
admin_site.register(Template)
admin_site.register(Conversation)
admin_site.register(Message)
admin_site.register(Attachment)
admin_site.register(Campaign)
admin_site.register(Flow)
