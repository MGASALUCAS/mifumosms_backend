"""
Stripe service for billing integration.
"""
import stripe
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class StripeService:
    """
    Service for interacting with Stripe API.
    """
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def get_or_create_customer(self, tenant, email: str) -> str:
        """
        Get or create Stripe customer for tenant.
        
        Args:
            tenant: Tenant instance
            email: Customer email
        
        Returns:
            Stripe customer ID
        """
        try:
            # Check if customer already exists
            if hasattr(tenant, 'stripe_customer_id') and tenant.stripe_customer_id:
                return tenant.stripe_customer_id
            
            # Create new customer
            customer = stripe.Customer.create(
                email=email,
                name=tenant.name,
                metadata={
                    'tenant_id': str(tenant.id),
                    'subdomain': tenant.subdomain
                }
            )
            
            # Save customer ID to tenant
            tenant.stripe_customer_id = customer.id
            tenant.save(update_fields=['stripe_customer_id'])
            
            logger.info(f"Created Stripe customer for tenant: {tenant.name}")
            return customer.id
        
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {str(e)}")
            raise
    
    def create_subscription(self, customer_id: str, plan, billing_cycle: str, coupon_code: str = None) -> Dict[str, Any]:
        """
        Create Stripe subscription.
        
        Args:
            customer_id: Stripe customer ID
            plan: Plan instance
            billing_cycle: 'monthly' or 'yearly'
            coupon_code: Optional coupon code
        
        Returns:
            Stripe subscription object
        """
        try:
            # Get price ID based on billing cycle
            if billing_cycle == 'yearly' and plan.stripe_price_id_yearly:
                price_id = plan.stripe_price_id_yearly
            else:
                price_id = plan.stripe_price_id_monthly
            
            if not price_id:
                raise ValueError(f"No Stripe price ID found for plan {plan.name}")
            
            # Prepare subscription data
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'payment_settings': {'save_default_payment_method': 'on_subscription'},
                'expand': ['latest_invoice.payment_intent']
            }
            
            # Add coupon if provided
            if coupon_code:
                subscription_data['coupon'] = coupon_code
            
            # Create subscription
            subscription = stripe.Subscription.create(**subscription_data)
            
            logger.info(f"Created Stripe subscription: {subscription.id}")
            return subscription
        
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {str(e)}")
            raise
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Cancel Stripe subscription.
        
        Args:
            subscription_id: Stripe subscription ID
        
        Returns:
            Cancelled subscription object
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled Stripe subscription: {subscription_id}")
            return subscription
        
        except Exception as e:
            logger.error(f"Error cancelling Stripe subscription: {str(e)}")
            raise
    
    def update_subscription(self, subscription_id: str, plan, billing_cycle: str) -> Dict[str, Any]:
        """
        Update Stripe subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            plan: New plan instance
            billing_cycle: 'monthly' or 'yearly'
        
        Returns:
            Updated subscription object
        """
        try:
            # Get price ID based on billing cycle
            if billing_cycle == 'yearly' and plan.stripe_price_id_yearly:
                price_id = plan.stripe_price_id_yearly
            else:
                price_id = plan.stripe_price_id_monthly
            
            if not price_id:
                raise ValueError(f"No Stripe price ID found for plan {plan.name}")
            
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0]['id'],
                    'price': price_id
                }],
                proration_behavior='create_prorations'
            )
            
            logger.info(f"Updated Stripe subscription: {subscription_id}")
            return updated_subscription
        
        except Exception as e:
            logger.error(f"Error updating Stripe subscription: {str(e)}")
            raise
    
    def create_payment_method(self, customer_id: str, payment_method_id: str) -> Dict[str, Any]:
        """
        Attach payment method to customer.
        
        Args:
            customer_id: Stripe customer ID
            payment_method_id: Stripe payment method ID
        
        Returns:
            Payment method object
        """
        try:
            # Attach payment method to customer
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            logger.info(f"Attached payment method to customer: {customer_id}")
            return payment_method
        
        except Exception as e:
            logger.error(f"Error attaching payment method: {str(e)}")
            raise
    
    def detach_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Detach payment method from customer.
        
        Args:
            payment_method_id: Stripe payment method ID
        
        Returns:
            Detached payment method object
        """
        try:
            payment_method = stripe.PaymentMethod.detach(payment_method_id)
            
            logger.info(f"Detached payment method: {payment_method_id}")
            return payment_method
        
        except Exception as e:
            logger.error(f"Error detaching payment method: {str(e)}")
            raise
    
    def create_invoice(self, customer_id: str, subscription_id: str) -> Dict[str, Any]:
        """
        Create invoice for customer.
        
        Args:
            customer_id: Stripe customer ID
            subscription_id: Stripe subscription ID
        
        Returns:
            Invoice object
        """
        try:
            invoice = stripe.Invoice.create(
                customer=customer_id,
                subscription=subscription_id,
                auto_advance=True
            )
            
            logger.info(f"Created invoice: {invoice.id}")
            return invoice
        
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise
    
    def get_customer_invoices(self, customer_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get customer invoices.
        
        Args:
            customer_id: Stripe customer ID
            limit: Number of invoices to retrieve
        
        Returns:
            List of invoices
        """
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return invoices
        
        except Exception as e:
            logger.error(f"Error getting customer invoices: {str(e)}")
            raise
    
    def create_coupon(self, code: str, discount_type: str, discount_value: float, 
                     duration: str = 'once', max_redemptions: int = None) -> Dict[str, Any]:
        """
        Create Stripe coupon.
        
        Args:
            code: Coupon code
            discount_type: 'percent' or 'fixed'
            discount_value: Discount value
            duration: 'once', 'repeating', or 'forever'
            max_redemptions: Maximum number of redemptions
        
        Returns:
            Coupon object
        """
        try:
            coupon_data = {
                'id': code,
                'duration': duration
            }
            
            if discount_type == 'percent':
                coupon_data['percent_off'] = discount_value
            else:
                coupon_data['amount_off'] = int(discount_value * 100)  # Convert to cents
                coupon_data['currency'] = 'usd'
            
            if max_redemptions:
                coupon_data['max_redemptions'] = max_redemptions
            
            coupon = stripe.Coupon.create(**coupon_data)
            
            logger.info(f"Created Stripe coupon: {code}")
            return coupon
        
        except Exception as e:
            logger.error(f"Error creating Stripe coupon: {str(e)}")
            raise
    
    def get_customer_payment_methods(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer payment methods.
        
        Args:
            customer_id: Stripe customer ID
        
        Returns:
            List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            return payment_methods
        
        except Exception as e:
            logger.error(f"Error getting customer payment methods: {str(e)}")
            raise
