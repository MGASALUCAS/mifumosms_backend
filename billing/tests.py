"""
Comprehensive tests for the Billing API.
Tests all documented endpoints with real data scenarios.
"""
import json
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock

from .models import (
    SMSPackage, SMSBalance, Purchase, PaymentTransaction, 
    BillingPlan, Subscription, UsageRecord, CustomSMSPurchase
)
from tenants.models import Tenant

User = get_user_model()


class BillingAPITestCase(APITestCase):
    """Base test case for billing API tests."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Create test tenant
        self.tenant = Tenant.objects.create(
            name='Test Company',
            subdomain='test-company'
        )
        
        # Associate user with tenant through membership
        from tenants.models import Membership
        Membership.objects.create(
            tenant=self.tenant,
            user=self.user,
            role='owner',
            status='active'
        )
        
        # Create JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test SMS packages
        self.create_test_packages()
        
        # Create test billing plan
        self.create_test_billing_plan()
        
        # Create test subscription
        self.create_test_subscription()
        
        # Create test SMS balance
        self.create_test_sms_balance()
    
    def create_test_packages(self):
        """Create test SMS packages."""
        self.lite_package = SMSPackage.objects.create(
            name='Lite Package',
            package_type='lite',
            credits=1000,
            price=Decimal('25000.00'),
            unit_price=Decimal('25.00'),
            is_popular=False,
            is_active=True,
            features=['1000 SMS Credits', 'Standard Support', 'Basic Analytics'],
            default_sender_id='Taarifa-SMS',
            allowed_sender_ids=['Taarifa-SMS', 'Quantum'],
            sender_id_restriction='allowed_list'
        )
        
        self.standard_package = SMSPackage.objects.create(
            name='Standard Package',
            package_type='standard',
            credits=5000,
            price=Decimal('100000.00'),
            unit_price=Decimal('20.00'),
            is_popular=True,
            is_active=True,
            features=['5000 SMS Credits', 'Priority Support', 'Advanced Analytics', 'Bulk SMS Tools'],
            default_sender_id='Taarifa-SMS',
            allowed_sender_ids=['Taarifa-SMS', 'Quantum', 'Mifumo'],
            sender_id_restriction='allowed_list'
        )
        
        self.pro_package = SMSPackage.objects.create(
            name='Pro Package',
            package_type='pro',
            credits=10000,
            price=Decimal('150000.00'),
            unit_price=Decimal('15.00'),
            is_popular=False,
            is_active=True,
            features=['10000 SMS Credits', 'Premium Support', 'Advanced Analytics', 'Bulk SMS Tools', 'API Access'],
            default_sender_id='Mifumo',
            allowed_sender_ids=['Mifumo', 'Quantum', 'Taarifa-SMS'],
            sender_id_restriction='allowed_list'
        )
    
    def create_test_billing_plan(self):
        """Create test billing plan."""
        self.billing_plan = BillingPlan.objects.create(
            name='Professional',
            plan_type='professional',
            description='Professional plan with advanced features',
            price=Decimal('50000.00'),
            currency='TZS',
            billing_cycle='monthly',
            max_contacts=10000,
            max_campaigns=100,
            max_sms_per_month=5000,
            features=['Advanced Analytics', 'Priority Support', 'Bulk SMS Tools', 'Custom Sender IDs'],
            is_active=True
        )
    
    def create_test_subscription(self):
        """Create test subscription."""
        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.billing_plan,
            status='active',
            current_period_start=timezone.now().replace(day=1),
            current_period_end=timezone.now().replace(day=1) + timezone.timedelta(days=30),
            cancel_at_period_end=False
        )
    
    def create_test_sms_balance(self):
        """Create test SMS balance."""
        self.sms_balance = SMSBalance.objects.create(
            tenant=self.tenant,
            credits=1500,
            total_purchased=10000,
            total_used=8500
        )


class SMSPackageAPITests(BillingAPITestCase):
    """Test SMS Package API endpoints."""
    
    def test_list_sms_packages(self):
        """Test listing SMS packages."""
        url = reverse('sms-package-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)
        
        # Check package data structure
        package = response.data['results'][0]
        required_fields = [
            'id', 'name', 'package_type', 'credits', 'price', 'unit_price',
            'is_popular', 'is_active', 'features', 'savings_percentage',
            'default_sender_id', 'allowed_sender_ids', 'sender_id_restriction',
            'created_at', 'updated_at'
        ]
        for field in required_fields:
            self.assertIn(field, package)
        
        # Check popular package is marked correctly
        popular_packages = [p for p in response.data['results'] if p['is_popular']]
        self.assertEqual(len(popular_packages), 1)
        self.assertEqual(popular_packages[0]['name'], 'Standard Package')
    
    def test_sms_package_serialization(self):
        """Test SMS package serialization matches documentation."""
        url = reverse('sms-package-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find the standard package
        standard_package = next(
            p for p in response.data['results'] 
            if p['name'] == 'Standard Package'
        )
        
        # Verify data matches documentation format
        self.assertEqual(standard_package['name'], 'Standard Package')
        self.assertEqual(standard_package['package_type'], 'standard')
        self.assertEqual(standard_package['credits'], 5000)
        self.assertEqual(standard_package['price'], '100000.00')
        self.assertEqual(standard_package['unit_price'], '20.00')
        self.assertTrue(standard_package['is_popular'])
        self.assertTrue(standard_package['is_active'])
        self.assertIn('5000 SMS Credits', standard_package['features'])
        self.assertEqual(float(standard_package['savings_percentage']), 33.3)
        self.assertEqual(standard_package['default_sender_id'], 'Taarifa-SMS')
        self.assertIn('Taarifa-SMS', standard_package['allowed_sender_ids'])
        self.assertEqual(standard_package['sender_id_restriction'], 'allowed_list')


class SMSBalanceAPITests(BillingAPITestCase):
    """Test SMS Balance API endpoints."""
    
    def test_get_sms_balance(self):
        """Test getting SMS balance."""
        url = reverse('sms-balance')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure matches documentation
        required_fields = ['id', 'credits', 'total_purchased', 'total_used', 'last_updated', 'created_at', 'tenant']
        for field in required_fields:
            self.assertIn(field, response.data)
        
        # Check actual values
        self.assertEqual(response.data['credits'], 1500)
        self.assertEqual(response.data['total_purchased'], 10000)
        self.assertEqual(response.data['total_used'], 8500)
    
    def test_sms_balance_tenant_isolation(self):
        """Test that SMS balance is tenant-specific."""
        # Create another tenant and user
        other_tenant = Tenant.objects.create(name='Other Company', subdomain='other-company')
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        # Associate other user with other tenant
        from tenants.models import Membership
        Membership.objects.create(
            tenant=other_tenant,
            user=other_user,
            role='owner',
            status='active'
        )
        
        # Create balance for other tenant
        SMSBalance.objects.create(
            tenant=other_tenant,
            credits=500,
            total_purchased=2000,
            total_used=1500
        )
        
        # Test that we still get our tenant's balance
        url = reverse('sms-balance')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['credits'], 1500)  # Our tenant's balance


class UsageStatisticsAPITests(BillingAPITestCase):
    """Test Usage Statistics API endpoints."""
    
    def setUp(self):
        super().setUp()
        # Create usage records
        self.create_usage_records()
    
    def create_usage_records(self):
        """Create test usage records."""
        # Create usage records for different periods
        now = timezone.now()
        
        # This month
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=500,
            cost=Decimal('12500.00'),
            created_at=now
        )
        
        # Last month
        last_month = now.replace(day=1) - timezone.timedelta(days=1)
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=750,
            cost=Decimal('18750.00'),
            created_at=last_month
        )
        
        # This week
        this_week = now - timezone.timedelta(days=3)
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=125,
            cost=Decimal('3125.00'),
            created_at=this_week
        )
        
        # Today
        today = now - timezone.timedelta(hours=2)
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=25,
            cost=Decimal('625.00'),
            created_at=today
        )
    
    def test_usage_statistics(self):
        """Test usage statistics endpoint."""
        url = reverse('sms-usage-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        data = response.data['data']
        required_fields = ['current_balance', 'total_usage', 'monthly_usage', 'weekly_usage', 'daily_usage']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Check current balance
        self.assertEqual(data['current_balance'], 1500)
        
        # Check usage data structure
        for usage_type in ['total_usage', 'monthly_usage', 'weekly_usage']:
            usage_data = data[usage_type]
            self.assertIn('credits', usage_data)
            self.assertIn('cost', usage_data)
        
        # Check daily_usage structure (it's a list)
        self.assertIsInstance(data['daily_usage'], list)
        for daily_data in data['daily_usage']:
            self.assertIn('credits', daily_data)
            self.assertIn('cost', daily_data)
            self.assertIn('date', daily_data)
    
    def test_usage_statistics_with_filters(self):
        """Test usage statistics with date filters."""
        url = reverse('sms-usage-statistics')
        
        # Test with start_date filter
        response = self.client.get(url, {'start_date': '2024-01-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test with end_date filter
        response = self.client.get(url, {'end_date': '2024-12-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test with period filter
        response = self.client.get(url, {'period': 'daily'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PurchaseAPITests(BillingAPITestCase):
    """Test Purchase API endpoints."""
    
    def setUp(self):
        super().setUp()
        # Create test purchases
        self.create_test_purchases()
    
    def create_test_purchases(self):
        """Create test purchases."""
        # Create completed purchase
        self.completed_purchase = Purchase.objects.create(
            tenant=self.tenant,
            user=self.user,
            package=self.standard_package,
            invoice_number='INV-COMPLETED-123',
            amount=Decimal('100000.00'),
            credits=5000,
            unit_price=Decimal('20.00'),
            payment_method='zenopay_mobile_money',
            payment_reference='MPESA123456789',
            status='completed',
            completed_at=timezone.now()
        )
        
        # Create pending purchase
        self.pending_purchase = Purchase.objects.create(
            tenant=self.tenant,
            user=self.user,
            package=self.lite_package,
            invoice_number='INV-PENDING-123',
            amount=Decimal('25000.00'),
            credits=1000,
            unit_price=Decimal('25.00'),
            payment_method='zenopay_mobile_money',
            status='pending'
        )
    
    def test_list_purchases(self):
        """Test listing purchases."""
        url = reverse('sms-purchase-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check purchase data structure
        purchase = response.data['results'][0]
        required_fields = [
            'id', 'invoice_number', 'package', 'package_name', 'amount', 'credits',
            'unit_price', 'payment_method', 'payment_method_display', 'payment_reference',
            'status', 'status_display', 'created_at', 'completed_at', 'tenant'
        ]
        for field in required_fields:
            self.assertIn(field, purchase)
    
    def test_purchase_detail(self):
        """Test getting purchase detail."""
        url = reverse('sms-purchase-detail', kwargs={'pk': self.completed_purchase.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check detailed purchase data
        purchase = response.data
        self.assertEqual(purchase['package_name'], 'Standard Package')
        self.assertEqual(purchase['amount'], '100000.00')
        self.assertEqual(purchase['credits'], 5000)
        self.assertEqual(purchase['status'], 'completed')
        self.assertEqual(purchase['payment_method_display'], 'ZenoPay Mobile Money')
    
    def test_purchase_history_with_filters(self):
        """Test purchase history with filters."""
        url = reverse('sms-purchase-history')
        
        # Test with status filter
        response = self.client.get(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['purchases']), 1)
        
        # Test with date filters
        response = self.client.get(url, {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentAPITests(BillingAPITestCase):
    """Test Payment API endpoints."""
    
    @patch('billing.zenopay_service.zenopay_service.create_payment')
    def test_initiate_payment(self, mock_create_payment):
        """Test payment initiation."""
        # Mock ZenoPay response
        mock_create_payment.return_value = {
            'success': True,
            'order_id': 'ZENO-123456',
            'message': 'Payment request sent successfully'
        }
        
        url = reverse('payment-initiate')
        data = {
            'package_id': str(self.standard_package.id),
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'vodacom'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('transaction_id', response.data['data'])
        self.assertIn('order_id', response.data['data'])
        self.assertEqual(response.data['data']['amount'], 100000.00)
        self.assertEqual(response.data['data']['credits'], 5000)
        self.assertEqual(response.data['data']['mobile_money_provider'], 'vodacom')
        self.assertEqual(response.data['data']['provider_name'], 'Vodacom M-Pesa')
    
    def test_initiate_payment_validation(self):
        """Test payment initiation validation."""
        url = reverse('payment-initiate')
        
        # Test missing required fields
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['message'])
        
        # Test invalid phone number
        data = {
            'package_id': str(self.standard_package.id),
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '1234567890',  # Invalid format
            'mobile_money_provider': 'vodacom'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid phone number', response.data['message'])
        
        # Test invalid package ID
        data = {
            'package_id': 'invalid-uuid',
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'vodacom'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid package ID format', response.data['message'])
    
    def test_get_mobile_money_providers(self):
        """Test getting mobile money providers."""
        url = reverse('payment-providers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('providers', response.data)
        
        providers = response.data['providers']
        self.assertEqual(len(providers), 4)
        
        # Check provider structure
        provider = providers[0]
        required_fields = ['code', 'name', 'description', 'icon', 'is_active', 'min_amount', 'max_amount']
        for field in required_fields:
            self.assertIn(field, provider)
        
        # Check specific providers
        provider_codes = [p['code'] for p in providers]
        expected_codes = ['vodacom', 'tigo', 'airtel', 'halotel']
        for code in expected_codes:
            self.assertIn(code, provider_codes)
    
    def test_payment_verification(self):
        """Test payment verification."""
        # Create a test payment transaction
        transaction = PaymentTransaction.objects.create(
            tenant=self.tenant,
            user=self.user,
            order_id='MIFUMO-20241201-ABC12345',
            amount=Decimal('100000.00'),
            currency='TZS',
            status='completed',
            payment_reference='MPESA123456789',
            mobile_money_provider='vodacom',
            completed_at=timezone.now()
        )
        
        url = reverse('payment-verify', kwargs={'order_id': transaction.order_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['amount'], 100000.00)
    
    def test_get_active_payments(self):
        """Test getting active payments."""
        # Create active payment
        PaymentTransaction.objects.create(
            tenant=self.tenant,
            order_id='MIFUMO-20241201-ACTIVE123',
            amount=Decimal('50000.00'),
            currency='TZS',
            status='pending'
        )
        
        url = reverse('payment-active')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('active_payments', response.data)
        self.assertIn('expired_payments', response.data)
        self.assertIn('count', response.data)
    
    def test_payment_progress(self):
        """Test payment progress tracking."""
        # Create payment transaction
        transaction = PaymentTransaction.objects.create(
            tenant=self.tenant,
            user=self.user,
            order_id='MIFUMO-20241201-PROGRESS123',
            amount=Decimal('75000.00'),
            currency='TZS',
            status='processing'
        )
        
        url = reverse('payment-progress', kwargs={'transaction_id': transaction.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        data = response.data['data']
        self.assertIn('transaction_id', data)
        self.assertIn('status', data)
        self.assertIn('progress_percentage', data)
        self.assertIn('current_step', data)
        self.assertIn('steps', data)
    
    def test_cancel_payment(self):
        """Test payment cancellation."""
        # Create pending payment
        transaction = PaymentTransaction.objects.create(
            tenant=self.tenant,
            user=self.user,
            order_id='MIFUMO-20241201-CANCEL123',
            amount=Decimal('30000.00'),
            currency='TZS',
            status='pending'
        )
        
        url = reverse('payment-cancel', kwargs={'transaction_id': transaction.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('cancelled_order', response.data)
        
        # Verify transaction was cancelled
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'cancelled')


class CustomSMSAPITests(BillingAPITestCase):
    """Test Custom SMS Purchase API endpoints."""
    
    def test_calculate_custom_sms_pricing(self):
        """Test custom SMS pricing calculation."""
        url = reverse('custom-sms-calculate')
        data = {'credits': 5000}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        data = response.data['data']
        required_fields = [
            'credits', 'unit_price', 'total_price', 'active_tier',
            'tier_min_credits', 'tier_max_credits', 'savings_percentage', 'pricing_tiers'
        ]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Check pricing calculation
        self.assertEqual(data['credits'], 5000)
        self.assertEqual(data['unit_price'], 25.00)  # Standard tier
        self.assertEqual(data['total_price'], 125000.00)
        self.assertEqual(data['active_tier'], 'Standard')
        self.assertEqual(data['savings_percentage'], 16.7)  # (30-25)/30 * 100
    
    def test_custom_sms_pricing_tiers(self):
        """Test different pricing tiers."""
        url = reverse('custom-sms-calculate')
        
        # Test different credit amounts
        test_cases = [
            (500, 'Lite', 30.00),      # Lite tier
            (5000, 'Standard', 25.00), # Standard tier
            (15000, 'Standard', 25.00), # Still Standard tier
            (75000, 'Pro', 18.00)      # Pro tier
        ]
        
        for credits, expected_tier, expected_unit_price in test_cases:
            data = {'credits': credits}
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.data['data']
            self.assertEqual(result['active_tier'], expected_tier)
            self.assertEqual(result['unit_price'], expected_unit_price)
    
    @patch('billing.zenopay_service.zenopay_service.create_payment')
    def test_initiate_custom_sms_purchase(self, mock_create_payment):
        """Test custom SMS purchase initiation."""
        # Mock ZenoPay response
        mock_create_payment.return_value = {
            'success': True,
            'order_id': 'ZENO-CUSTOM-123456',
            'message': 'Payment request sent successfully'
        }
        
        url = reverse('custom-sms-initiate')
        data = {
            'credits': 5000,
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'vodacom'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('purchase_id', response.data['data'])
        self.assertEqual(response.data['data']['credits'], 5000)
        self.assertEqual(response.data['data']['unit_price'], 25.00)
        self.assertEqual(response.data['data']['total_price'], 125000.00)
        self.assertEqual(response.data['data']['active_tier'], 'Standard')
    
    def test_custom_sms_purchase_status(self):
        """Test custom SMS purchase status check."""
        # Create custom SMS purchase
        purchase = CustomSMSPurchase.objects.create(
            tenant=self.tenant,
            credits=5000,
            unit_price=Decimal('25.00'),
            total_price=Decimal('125000.00'),
            active_tier='Standard',
            tier_min_credits=5000,
            tier_max_credits=50000,
            status='completed',
            completed_at=timezone.now()
        )
        
        url = reverse('custom-sms-status', kwargs={'purchase_id': purchase.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        data = response.data['data']
        self.assertEqual(data['purchase_id'], str(purchase.id))
        self.assertEqual(data['credits'], 5000)
        self.assertEqual(data['status'], 'completed')


class SubscriptionAPITests(BillingAPITestCase):
    """Test Subscription API endpoints."""
    
    def test_list_billing_plans(self):
        """Test listing billing plans."""
        url = reverse('plan-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        
        # Check plan data structure
        plan = response.data['results'][0]
        required_fields = [
            'id', 'name', 'plan_type', 'description', 'price', 'currency',
            'billing_cycle', 'max_contacts', 'max_campaigns', 'max_sms_per_month',
            'features', 'is_active', 'created_at'
        ]
        for field in required_fields:
            self.assertIn(field, plan)
    
    def test_get_subscription(self):
        """Test getting subscription details."""
        url = reverse('subscription-detail')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check subscription data structure
        required_fields = [
            'id', 'plan', 'plan_name', 'status', 'status_display',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'is_active', 'created_at', 'tenant'
        ]
        for field in required_fields:
            self.assertIn(field, response.data)
        
        # Check actual values
        self.assertEqual(response.data['plan_name'], 'Professional')
        self.assertEqual(response.data['status'], 'active')
        self.assertTrue(response.data['is_active'])
    
    def test_billing_overview(self):
        """Test billing overview endpoint."""
        url = reverse('billing-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        data = response.data['data']
        required_fields = ['subscription', 'sms_balance', 'recent_purchases', 'usage_summary', 'active_payments']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Check subscription data
        subscription = data['subscription']
        self.assertEqual(subscription['plan_name'], 'Professional')
        self.assertEqual(subscription['status'], 'active')
        self.assertTrue(subscription['is_active'])
        
        # Check SMS balance data
        sms_balance = data['sms_balance']
        self.assertEqual(sms_balance['credits'], 1500)
        self.assertEqual(sms_balance['total_purchased'], 10000)
        self.assertEqual(sms_balance['total_used'], 8500)


class AuthenticationTests(APITestCase):
    """Test authentication requirements."""
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        urls = [
            reverse('sms-package-list'),
            reverse('sms-balance'),
            reverse('sms-purchase-list'),
            reverse('payment-initiate'),
            reverse('plan-list'),
            reverse('subscription-detail'),
            reverse('billing-overview')
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_without_tenant_access_denied(self):
        """Test that users without tenant are denied access."""
        # Create user without tenant by temporarily disabling the signal
        from django.db.models.signals import post_save
        from accounts.signals import create_user_profile_and_tenant
        
        # Disable the signal temporarily
        post_save.disconnect(create_user_profile_and_tenant, sender=User)
        
        try:
            # Create user without tenant
            user = User.objects.create_user(
                email='notenant@example.com',
                password='testpass123'
            )
            
            # Create JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Set up authentication
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            
            # Test that requests are denied
            url = reverse('sms-balance')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('not associated with any tenant', response.data['message'])
        finally:
            # Re-enable the signal
            post_save.connect(create_user_profile_and_tenant, sender=User)


class ErrorHandlingTests(BillingAPITestCase):
    """Test error handling scenarios."""
    
    def test_invalid_package_id(self):
        """Test handling of invalid package ID."""
        url = reverse('payment-initiate')
        data = {
            'package_id': str(uuid.uuid4()),  # Non-existent package
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'vodacom'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Package not found', response.data['message'])
    
    def test_invalid_mobile_money_provider(self):
        """Test handling of invalid mobile money provider."""
        url = reverse('payment-initiate')
        data = {
            'package_id': str(self.standard_package.id),
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'invalid_provider'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid mobile money provider', response.data['message'])
    
    def test_invalid_phone_number_format(self):
        """Test handling of invalid phone number format."""
        url = reverse('payment-initiate')
        data = {
            'package_id': str(self.standard_package.id),
            'buyer_email': 'test@example.com',
            'buyer_name': 'John Doe',
            'buyer_phone': '1234567890',  # Invalid format
            'mobile_money_provider': 'vodacom'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid phone number', response.data['message'])
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        url = reverse('payment-initiate')
        data = {}  # Empty data
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['message'])


class DataValidationTests(BillingAPITestCase):
    """Test data validation and serialization."""
    
    def test_sms_package_savings_calculation(self):
        """Test SMS package savings percentage calculation."""
        # Test package with savings
        package = SMSPackage.objects.get(name='Standard Package')
        self.assertEqual(float(package.savings_percentage), 33.3)  # (30-20)/30 * 100
        
        # Test package without savings
        package = SMSPackage.objects.get(name='Lite Package')
        self.assertEqual(float(package.savings_percentage), 16.7)  # (30-25)/30 * 100
    
    def test_sender_id_validation(self):
        """Test sender ID validation for packages."""
        package = SMSPackage.objects.get(name='Standard Package')
        
        # Test allowed sender ID
        self.assertTrue(package.is_sender_id_allowed('Taarifa-SMS'))
        self.assertTrue(package.is_sender_id_allowed('Quantum'))
        self.assertTrue(package.is_sender_id_allowed('Mifumo'))
        
        # Test disallowed sender ID
        self.assertFalse(package.is_sender_id_allowed('InvalidSender'))
        self.assertFalse(package.is_sender_id_allowed(''))
        self.assertFalse(package.is_sender_id_allowed(None))
    
    def test_usage_record_aggregation(self):
        """Test usage record aggregation in statistics."""
        # Create multiple usage records on different days
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        day_before_yesterday = now - timedelta(days=2)
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=100,
            cost=Decimal('2500.00'),
            created_at=day_before_yesterday
        )
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=200,
            cost=Decimal('5000.00'),
            created_at=yesterday
        )
        
        url = reverse('sms-usage-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        
        # Check that usage is properly aggregated
        # Find the days with usage (they might not be in order)
        daily_credits = [day['credits'] for day in data['daily_usage']]
        daily_costs = [day['cost'] for day in data['daily_usage']]
        
        # Check that the total usage is correct (300 credits total)
        total_credits = sum(daily_credits)
        total_costs = sum(daily_costs)
        self.assertEqual(total_credits, 300)  # 100 + 200
        self.assertEqual(total_costs, 7500.00)  # 2500.00 + 5000.00


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['billing.tests'])
