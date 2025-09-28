"""
Cost calculation service for message billing.
"""
import logging
from typing import Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class CostMeterService:
    """
    Service for calculating message costs and tracking usage.
    """
    
    def __init__(self):
        # Cost per message in micro-units (cents * 10000)
        self.costs = {
            'whatsapp': {
                'text': 1000,  # $0.001 per text message
                'media': 2000,  # $0.002 per media message
            },
            'sms': {
                'text': 5000,  # $0.005 per SMS
                'media': 10000,  # $0.01 per MMS
            },
            'telegram': {
                'text': 0,  # Free
                'media': 0,  # Free
            }
        }
    
    def calculate_message_cost(self, message) -> int:
        """
        Calculate the cost of a message.
        
        Args:
            message: Message instance
        
        Returns:
            Cost in micro-units
        """
        try:
            provider = message.provider
            has_media = bool(message.media_url)
            
            if provider in self.costs:
                message_type = 'media' if has_media else 'text'
                return self.costs[provider].get(message_type, 0)
            else:
                logger.warning(f"Unknown provider for cost calculation: {provider}")
                return 0
        
        except Exception as e:
            logger.error(f"Error calculating message cost: {str(e)}")
            return 0
    
    def calculate_campaign_cost(self, campaign) -> int:
        """
        Calculate the total cost of a campaign.
        
        Args:
            campaign: Campaign instance
        
        Returns:
            Total cost in micro-units
        """
        try:
            # Get all messages for the campaign
            messages = campaign.messages.all()
            total_cost = 0
            
            for message in messages:
                total_cost += self.calculate_message_cost(message)
            
            return total_cost
        
        except Exception as e:
            logger.error(f"Error calculating campaign cost: {str(e)}")
            return 0
    
    def calculate_tenant_monthly_cost(self, tenant, year=None, month=None) -> Dict[str, Any]:
        """
        Calculate monthly costs for a tenant.
        
        Args:
            tenant: Tenant instance
            year: Year (defaults to current year)
            month: Month (defaults to current month)
        
        Returns:
            Dict with cost breakdown
        """
        try:
            from django.utils import timezone
            from django.db.models import Sum, Count
            from .models import Message
            
            if year is None:
                year = timezone.now().year
            if month is None:
                month = timezone.now().month
            
            # Get messages for the month
            messages = Message.objects.filter(
                tenant=tenant,
                created_at__year=year,
                created_at__month=month
            )
            
            # Calculate costs by provider
            costs_by_provider = {}
            total_cost = 0
            
            for provider in self.costs.keys():
                provider_messages = messages.filter(provider=provider)
                provider_cost = 0
                
                for message in provider_messages:
                    provider_cost += self.calculate_message_cost(message)
                
                costs_by_provider[provider] = {
                    'count': provider_messages.count(),
                    'cost_micro': provider_cost,
                    'cost_dollars': provider_cost / 1000000
                }
                
                total_cost += provider_cost
            
            return {
                'total_cost_micro': total_cost,
                'total_cost_dollars': total_cost / 1000000,
                'by_provider': costs_by_provider,
                'period': f"{year}-{month:02d}"
            }
        
        except Exception as e:
            logger.error(f"Error calculating monthly cost: {str(e)}")
            return {
                'total_cost_micro': 0,
                'total_cost_dollars': 0,
                'by_provider': {},
                'period': f"{year}-{month:02d}"
            }
    
    def get_usage_limits(self, tenant) -> Dict[str, int]:
        """
        Get usage limits for a tenant based on their subscription.
        
        Args:
            tenant: Tenant instance
        
        Returns:
            Dict with usage limits
        """
        try:
            # TODO: Integrate with billing system to get actual limits
            # For now, return default limits
            
            # Check if tenant has active subscription
            if hasattr(tenant, 'subscription') and tenant.subscription:
                plan = tenant.subscription.plan
                return {
                    'messages_per_month': plan.messages_limit,
                    'cost_limit_dollars': plan.cost_limit,
                    'current_usage': self.get_current_month_usage(tenant)
                }
            else:
                # Free tier limits
                return {
                    'messages_per_month': 1000,
                    'cost_limit_dollars': 10.0,
                    'current_usage': self.get_current_month_usage(tenant)
                }
        
        except Exception as e:
            logger.error(f"Error getting usage limits: {str(e)}")
            return {
                'messages_per_month': 1000,
                'cost_limit_dollars': 10.0,
                'current_usage': 0
            }
    
    def get_current_month_usage(self, tenant) -> Dict[str, Any]:
        """
        Get current month usage for a tenant.
        
        Args:
            tenant: Tenant instance
        
        Returns:
            Dict with current usage
        """
        try:
            from django.utils import timezone
            from .models import Message
            
            now = timezone.now()
            
            # Get messages for current month
            messages = Message.objects.filter(
                tenant=tenant,
                created_at__year=now.year,
                created_at__month=now.month
            )
            
            total_cost = 0
            for message in messages:
                total_cost += self.calculate_message_cost(message)
            
            return {
                'messages_count': messages.count(),
                'cost_micro': total_cost,
                'cost_dollars': total_cost / 1000000
            }
        
        except Exception as e:
            logger.error(f"Error getting current usage: {str(e)}")
            return {
                'messages_count': 0,
                'cost_micro': 0,
                'cost_dollars': 0
            }
    
    def check_usage_limits(self, tenant) -> Dict[str, Any]:
        """
        Check if tenant has exceeded usage limits.
        
        Args:
            tenant: Tenant instance
        
        Returns:
            Dict with limit check results
        """
        try:
            limits = self.get_usage_limits(tenant)
            current_usage = self.get_current_month_usage(tenant)
            
            messages_exceeded = current_usage['messages_count'] >= limits['messages_per_month']
            cost_exceeded = current_usage['cost_dollars'] >= limits['cost_limit_dollars']
            
            return {
                'within_limits': not (messages_exceeded or cost_exceeded),
                'messages_exceeded': messages_exceeded,
                'cost_exceeded': cost_exceeded,
                'limits': limits,
                'current_usage': current_usage
            }
        
        except Exception as e:
            logger.error(f"Error checking usage limits: {str(e)}")
            return {
                'within_limits': True,
                'messages_exceeded': False,
                'cost_exceeded': False,
                'limits': {},
                'current_usage': {}
            }
