"""
Views for billing functionality.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Q

from .models import Plan, Subscription, Invoice, UsageRecord, PaymentMethod, Coupon
from .serializers import (
    PlanSerializer, SubscriptionSerializer, InvoiceSerializer,
    UsageRecordSerializer, PaymentMethodSerializer, CouponSerializer,
    CreateSubscriptionSerializer, UpdateSubscriptionSerializer, BillingOverviewSerializer
)
from core.permissions import IsTenantMember, IsTenantAdmin
from .services.stripe_service import StripeService


class PlanListView(generics.ListAPIView):
    """List available subscription plans."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = PlanSerializer
    queryset = Plan.objects.filter(is_active=True)


class SubscriptionDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update tenant subscription."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = SubscriptionSerializer
    
    def get_object(self):
        """Get tenant's subscription."""
        try:
            return self.request.tenant.subscription
        except Subscription.DoesNotExist:
            return None


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def create_subscription(request):
    """Create a new subscription."""
    serializer = CreateSubscriptionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        stripe_service = StripeService()
        
        # Get plan
        plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
        
        # Create Stripe customer if not exists
        customer_id = stripe_service.get_or_create_customer(
            tenant=request.tenant,
            email=request.user.email
        )
        
        # Create Stripe subscription
        stripe_subscription = stripe_service.create_subscription(
            customer_id=customer_id,
            plan=plan,
            billing_cycle=serializer.validated_data['billing_cycle'],
            coupon_code=serializer.validated_data.get('coupon_code')
        )
        
        # Create subscription record
        subscription = Subscription.objects.create(
            tenant=request.tenant,
            plan=plan,
            stripe_subscription_id=stripe_subscription['id'],
            stripe_customer_id=customer_id,
            status=stripe_subscription['status'],
            billing_cycle=serializer.validated_data['billing_cycle'],
            current_period_start=timezone.datetime.fromtimestamp(
                stripe_subscription['current_period_start']
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                stripe_subscription['current_period_end']
            ),
            trial_end=timezone.datetime.fromtimestamp(
                stripe_subscription['trial_end']
            ) if stripe_subscription.get('trial_end') else None
        )
        
        return Response({
            'message': 'Subscription created successfully',
            'subscription': SubscriptionSerializer(subscription).data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def cancel_subscription(request):
    """Cancel tenant subscription."""
    try:
        subscription = request.tenant.subscription
        if not subscription:
            return Response(
                {'error': 'No active subscription found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stripe_service = StripeService()
        stripe_service.cancel_subscription(subscription.stripe_subscription_id)
        
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        
        return Response({'message': 'Subscription cancelled successfully'})
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


class InvoiceListView(generics.ListAPIView):
    """List tenant invoices."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        """Filter invoices by tenant."""
        return Invoice.objects.filter(tenant=self.request.tenant)


class InvoiceDetailView(generics.RetrieveAPIView):
    """Retrieve invoice details."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        """Filter invoices by tenant."""
        return Invoice.objects.filter(tenant=self.request.tenant)


class PaymentMethodListView(generics.ListCreateAPIView):
    """List and create payment methods."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        """Filter payment methods by tenant."""
        return PaymentMethod.objects.filter(tenant=self.request.tenant, is_active=True)
    
    def perform_create(self, serializer):
        """Create payment method for tenant."""
        serializer.save(tenant=self.request.tenant)


class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete payment method."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = PaymentMethodSerializer
    
    def get_queryset(self):
        """Filter payment methods by tenant."""
        return PaymentMethod.objects.filter(tenant=self.request.tenant)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def set_default_payment_method(request, payment_method_id):
    """Set default payment method."""
    try:
        payment_method = get_object_or_404(
            PaymentMethod,
            id=payment_method_id,
            tenant=request.tenant
        )
        
        # Remove default from other payment methods
        PaymentMethod.objects.filter(
            tenant=request.tenant,
            is_default=True
        ).update(is_default=False)
        
        # Set as default
        payment_method.is_default = True
        payment_method.save()
        
        return Response({'message': 'Default payment method updated'})
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


class UsageRecordListView(generics.ListAPIView):
    """List tenant usage records."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = UsageRecordSerializer
    
    def get_queryset(self):
        """Filter usage records by tenant."""
        return UsageRecord.objects.filter(tenant=self.request.tenant)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def billing_overview(request):
    """Get billing overview for tenant."""
    try:
        tenant = request.tenant
        
        # Get current subscription
        subscription = getattr(tenant, 'subscription', None)
        current_plan = subscription.plan if subscription else None
        
        # Get current usage
        from messaging.services.costmeter import CostMeterService
        cost_service = CostMeterService()
        current_usage = cost_service.get_current_month_usage(tenant)
        
        # Get upcoming invoice
        upcoming_invoice = None
        if subscription:
            upcoming_invoice = Invoice.objects.filter(
                tenant=tenant,
                status__in=['draft', 'open']
            ).first()
        
        # Get payment methods
        payment_methods = PaymentMethod.objects.filter(
            tenant=tenant,
            is_active=True
        )
        
        # Get recent invoices
        recent_invoices = Invoice.objects.filter(
            tenant=tenant
        ).order_by('-invoice_date')[:5]
        
        # Get usage history (last 6 months)
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        usage_history = UsageRecord.objects.filter(
            tenant=tenant,
            period_start__gte=six_months_ago
        ).order_by('-period_start')
        
        overview_data = {
            'current_plan': current_plan,
            'subscription': subscription,
            'current_usage': current_usage,
            'upcoming_invoice': upcoming_invoice,
            'payment_methods': payment_methods,
            'recent_invoices': recent_invoices,
            'usage_history': usage_history
        }
        
        serializer = BillingOverviewSerializer(overview_data)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantMember])
def usage_limits(request):
    """Get usage limits for tenant."""
    try:
        from messaging.services.costmeter import CostMeterService
        cost_service = CostMeterService()
        
        limits = cost_service.get_usage_limits(request.tenant)
        return Response(limits)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CouponListView(generics.ListAPIView):
    """List available coupons."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CouponSerializer
    
    def get_queryset(self):
        """Filter active and valid coupons."""
        return Coupon.objects.filter(is_active=True)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantMember])
def validate_coupon(request):
    """Validate a coupon code."""
    coupon_code = request.data.get('code', '')
    
    try:
        coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        
        if not coupon.is_valid:
            return Response(
                {'error': 'Coupon is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data
        })
    
    except Coupon.DoesNotExist:
        return Response(
            {'error': 'Invalid coupon code'},
            status=status.HTTP_400_BAD_REQUEST
        )
