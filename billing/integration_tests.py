"""
Integration tests for complete billing workflows.
Tests end-to-end scenarios that match real-world usage.
"""
import json
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
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


class CompletePaymentFlowTests(APITestCase):
    """Test complete payment workflows from initiation to completion."""
    
    def setUp(self):
        """Set up test data for complete workflows."""
        # Create test user and tenant
        self.user = User.objects.create_user(
            email='integration@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Tester'
        )
        
        self.tenant = Tenant.objects.create(
            name='Integration Test Company',
            subdomain='integration-test'
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
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test SMS package
        self.sms_package = SMSPackage.objects.create(
            name='Integration Test Package',
            package_type='standard',
            credits=2000,
            price=Decimal('40000.00'),
            unit_price=Decimal('20.00'),
            is_popular=True,
            is_active=True,
            features=['2000 SMS Credits', 'Priority Support', 'Advanced Analytics'],
            default_sender_id='TestSender',
            allowed_sender_ids=['TestSender', 'IntegrationSender'],
            sender_id_restriction='allowed_list'
        )
        
        # Create initial SMS balance
        self.sms_balance = SMSBalance.objects.create(
            tenant=self.tenant,
            credits=500,
            total_purchased=2000,
            total_used=1500
        )
    
    @patch('billing.zenopay_service.zenopay_service.create_payment')
    @patch('billing.zenopay_service.zenopay_service.verify_payment')
    def test_complete_payment_flow(self, mock_verify_payment, mock_create_payment):
        """Test complete payment flow from initiation to completion."""
        print("\n🔄 Testing Complete Payment Flow...")
        
        # Mock ZenoPay responses
        mock_create_payment.return_value = {
            'success': True,
            'order_id': 'ZENO-INTEGRATION-123456',
            'message': 'Payment request sent successfully'
        }
        
        mock_verify_payment.return_value = {
            'success': True,
            'status': 'completed',
            'payment_reference': 'MPESA-INTEGRATION-789',
            'amount': 40000.00
        }
        
        # Step 1: List available packages
        print("  📦 Step 1: Listing SMS packages...")
        packages_url = reverse('sms-package-list')
        packages_response = self.client.get(packages_url)
        
        self.assertEqual(packages_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', packages_response.data)
        self.assertTrue(len(packages_response.data['results']) > 0)
        
        # Find our test package
        test_package = next(
            p for p in packages_response.data['results'] 
            if p['name'] == 'Integration Test Package'
        )
        self.assertEqual(test_package['credits'], 2000)
        self.assertEqual(test_package['price'], '40000.00')
        
        # Step 2: Check current balance
        print("  💰 Step 2: Checking current SMS balance...")
        balance_url = reverse('sms-balance')
        balance_response = self.client.get(balance_url)
        
        self.assertEqual(balance_response.status_code, status.HTTP_200_OK)
        initial_credits = balance_response.data['credits']
        self.assertEqual(initial_credits, 500)
        
        # Step 3: Get mobile money providers
        print("  📱 Step 3: Getting mobile money providers...")
        providers_url = reverse('payment-providers')
        providers_response = self.client.get(providers_url)
        
        self.assertEqual(providers_response.status_code, status.HTTP_200_OK)
        self.assertTrue(providers_response.data['success'])
        self.assertIn('providers', providers_response.data)
        
        providers = providers_response.data['providers']
        self.assertTrue(len(providers) >= 4)  # vodacom, tigo, airtel, halotel
        
        # Step 4: Initiate payment
        print("  💳 Step 4: Initiating payment...")
        payment_url = reverse('payment-initiate')
        payment_data = {
            'package_id': str(self.sms_package.id),
            'buyer_email': 'integration@example.com',
            'buyer_name': 'Integration Tester',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'vodacom'
        }
        
        payment_response = self.client.post(payment_url, payment_data, format='json')
        
        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(payment_response.data['success'])
        
        payment_data = payment_response.data['data']
        transaction_id = payment_data['transaction_id']
        order_id = payment_data['order_id']
        
        self.assertEqual(payment_data['amount'], 40000.00)
        self.assertEqual(payment_data['credits'], 2000)
        self.assertEqual(payment_data['mobile_money_provider'], 'vodacom')
        self.assertEqual(payment_data['provider_name'], 'Vodacom M-Pesa')
        
        # Step 5: Track payment progress
        print("  📊 Step 5: Tracking payment progress...")
        progress_url = reverse('payment-progress', kwargs={'transaction_id': transaction_id})
        progress_response = self.client.get(progress_url)
        
        self.assertEqual(progress_response.status_code, status.HTTP_200_OK)
        self.assertTrue(progress_response.data['success'])
        
        progress_data = progress_response.data['data']
        self.assertIn('status', progress_data)
        self.assertIn('progress_percentage', progress_data)
        self.assertIn('current_step', progress_data)
        self.assertIn('steps', progress_data)
        
        # Step 6: Verify payment completion
        print("  ✅ Step 6: Verifying payment completion...")
        verify_url = reverse('payment-verify', kwargs={'order_id': order_id})
        verify_response = self.client.get(verify_url)
        
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertTrue(verify_response.data['success'])
        
        verify_data = verify_response.data['data']
        self.assertEqual(verify_data['status'], 'completed')
        self.assertEqual(verify_data['amount'], 40000.00)
        
        # Step 7: Check updated balance
        print("  💰 Step 7: Checking updated SMS balance...")
        updated_balance_response = self.client.get(balance_url)
        
        self.assertEqual(updated_balance_response.status_code, status.HTTP_200_OK)
        updated_credits = updated_balance_response.data['credits']
        self.assertEqual(updated_credits, initial_credits + 2000)  # 500 + 2000 = 2500
        
        # Step 8: Check purchase history
        print("  📋 Step 8: Checking purchase history...")
        purchases_url = reverse('sms-purchase-list')
        purchases_response = self.client.get(purchases_url)
        
        self.assertEqual(purchases_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', purchases_response.data)
        
        # Find our purchase
        purchases = purchases_response.data['results']
        our_purchase = next(
            p for p in purchases 
            if p['package_name'] == 'Integration Test Package'
        )
        self.assertEqual(our_purchase['amount'], '40000.00')
        self.assertEqual(our_purchase['credits'], 2000)
        self.assertEqual(our_purchase['status'], 'completed')
        
        print("  ✅ Complete payment flow test passed!")
    
    @patch('billing.zenopay_service.zenopay_service.create_payment')
    def test_custom_sms_purchase_flow(self, mock_create_payment):
        """Test complete custom SMS purchase workflow."""
        print("\n🔄 Testing Custom SMS Purchase Flow...")
        
        # Mock ZenoPay response
        mock_create_payment.return_value = {
            'success': True,
            'order_id': 'ZENO-CUSTOM-INTEGRATION-123',
            'message': 'Payment request sent successfully'
        }
        
        # Step 1: Calculate custom SMS pricing
        print("  💰 Step 1: Calculating custom SMS pricing...")
        calculate_url = reverse('custom-sms-calculate')
        calculate_data = {'credits': 3000}
        
        calculate_response = self.client.post(calculate_url, calculate_data, format='json')
        
        self.assertEqual(calculate_response.status_code, status.HTTP_200_OK)
        self.assertTrue(calculate_response.data['success'])
        
        pricing_data = calculate_response.data['data']
        self.assertEqual(pricing_data['credits'], 3000)
        self.assertEqual(pricing_data['unit_price'], 20.00)  # Standard tier
        self.assertEqual(pricing_data['total_price'], 60000.00)
        self.assertEqual(pricing_data['active_tier'], 'Standard')
        
        # Step 2: Initiate custom SMS purchase
        print("  💳 Step 2: Initiating custom SMS purchase...")
        initiate_url = reverse('custom-sms-initiate')
        initiate_data = {
            'credits': 3000,
            'buyer_email': 'integration@example.com',
            'buyer_name': 'Integration Tester',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'tigo'
        }
        
        initiate_response = self.client.post(initiate_url, initiate_data, format='json')
        
        self.assertEqual(initiate_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(initiate_response.data['success'])
        
        purchase_data = initiate_response.data['data']
        purchase_id = purchase_data['purchase_id']
        
        self.assertEqual(purchase_data['credits'], 3000)
        self.assertEqual(purchase_data['unit_price'], 20.00)
        self.assertEqual(purchase_data['total_price'], 60000.00)
        self.assertEqual(purchase_data['active_tier'], 'Standard')
        
        # Step 3: Check custom SMS purchase status
        print("  📊 Step 3: Checking custom SMS purchase status...")
        status_url = reverse('custom-sms-status', kwargs={'purchase_id': purchase_id})
        status_response = self.client.get(status_url)
        
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertTrue(status_response.data['success'])
        
        status_data = status_response.data['data']
        self.assertEqual(status_data['purchase_id'], purchase_id)
        self.assertEqual(status_data['credits'], 3000)
        self.assertEqual(status_data['status'], 'processing')
        
        print("  ✅ Custom SMS purchase flow test passed!")
    
    def test_subscription_management_flow(self):
        """Test complete subscription management workflow."""
        print("\n🔄 Testing Subscription Management Flow...")
        
        # Step 1: List billing plans
        print("  📋 Step 1: Listing billing plans...")
        plans_url = reverse('plan-list')
        plans_response = self.client.get(plans_url)
        
        self.assertEqual(plans_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', plans_response.data)
        
        plans = plans_response.data['results']
        self.assertTrue(len(plans) > 0)
        
        # Check plan structure
        plan = plans[0]
        required_fields = [
            'id', 'name', 'plan_type', 'description', 'price', 'currency',
            'billing_cycle', 'max_contacts', 'max_campaigns', 'max_sms_per_month',
            'features', 'is_active'
        ]
        for field in required_fields:
            self.assertIn(field, plan)
        
        # Step 2: Get subscription details
        print("  📊 Step 2: Getting subscription details...")
        subscription_url = reverse('subscription-detail')
        subscription_response = self.client.get(subscription_url)
        
        self.assertEqual(subscription_response.status_code, status.HTTP_200_OK)
        
        subscription_data = subscription_response.data
        self.assertIn('plan_name', subscription_data)
        self.assertIn('status', subscription_data)
        self.assertIn('is_active', subscription_data)
        
        # Step 3: Get billing overview
        print("  📈 Step 3: Getting billing overview...")
        overview_url = reverse('billing-overview')
        overview_response = self.client.get(overview_url)
        
        self.assertEqual(overview_response.status_code, status.HTTP_200_OK)
        self.assertTrue(overview_response.data['success'])
        
        overview_data = overview_response.data['data']
        required_sections = ['subscription', 'sms_balance', 'recent_purchases', 'usage_summary', 'active_payments']
        for section in required_sections:
            self.assertIn(section, overview_data)
        
        # Check subscription section
        subscription_section = overview_data['subscription']
        self.assertIn('plan_name', subscription_section)
        self.assertIn('status', subscription_section)
        self.assertIn('is_active', subscription_section)
        
        # Check SMS balance section
        sms_balance_section = overview_data['sms_balance']
        self.assertIn('credits', sms_balance_section)
        self.assertIn('total_purchased', sms_balance_section)
        self.assertIn('total_used', sms_balance_section)
        
        print("  ✅ Subscription management flow test passed!")
    
    def test_usage_statistics_flow(self):
        """Test complete usage statistics workflow."""
        print("\n🔄 Testing Usage Statistics Flow...")
        
        # Create some usage records
        now = timezone.now()
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=100,
            cost=Decimal('2500.00'),
            created_at=now
        )
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=200,
            cost=Decimal('5000.00'),
            created_at=now - timezone.timedelta(days=1)
        )
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=150,
            cost=Decimal('3750.00'),
            created_at=now - timezone.timedelta(days=7)
        )
        
        # Step 1: Get usage statistics
        print("  📊 Step 1: Getting usage statistics...")
        stats_url = reverse('sms-usage-statistics')
        stats_response = self.client.get(stats_url)
        
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertTrue(stats_response.data['success'])
        
        stats_data = stats_response.data['data']
        required_periods = ['current_balance', 'total_usage', 'monthly_usage', 'weekly_usage', 'daily_usage']
        for period in required_periods:
            self.assertIn(period, stats_data)
        
        # Check data structure for each period
        for period in required_periods:
            period_data = stats_data[period]
            self.assertIn('credits', period_data)
            self.assertIn('cost', period_data)
            self.assertIn('period', period_data)
        
        # Step 2: Test usage statistics with filters
        print("  🔍 Step 2: Testing usage statistics with filters...")
        
        # Test with start_date filter
        filtered_response = self.client.get(stats_url, {'start_date': '2024-01-01'})
        self.assertEqual(filtered_response.status_code, status.HTTP_200_OK)
        
        # Test with end_date filter
        filtered_response = self.client.get(stats_url, {'end_date': '2024-12-31'})
        self.assertEqual(filtered_response.status_code, status.HTTP_200_OK)
        
        # Test with period filter
        filtered_response = self.client.get(stats_url, {'period': 'daily'})
        self.assertEqual(filtered_response.status_code, status.HTTP_200_OK)
        
        print("  ✅ Usage statistics flow test passed!")
    
    def test_error_handling_flow(self):
        """Test error handling in various scenarios."""
        print("\n🔄 Testing Error Handling Flow...")
        
        # Test 1: Invalid package ID
        print("  ❌ Test 1: Invalid package ID...")
        payment_url = reverse('payment-initiate')
        invalid_data = {
            'package_id': str(uuid.uuid4()),  # Non-existent package
            'buyer_email': 'test@example.com',
            'buyer_name': 'Test User',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'vodacom'
        }
        
        response = self.client.post(payment_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Package not found', response.data['message'])
        
        # Test 2: Invalid phone number
        print("  ❌ Test 2: Invalid phone number...")
        invalid_phone_data = {
            'package_id': str(self.sms_package.id),
            'buyer_email': 'test@example.com',
            'buyer_name': 'Test User',
            'buyer_phone': '1234567890',  # Invalid format
            'mobile_money_provider': 'vodacom'
        }
        
        response = self.client.post(payment_url, invalid_phone_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid phone number', response.data['message'])
        
        # Test 3: Invalid mobile money provider
        print("  ❌ Test 3: Invalid mobile money provider...")
        invalid_provider_data = {
            'package_id': str(self.sms_package.id),
            'buyer_email': 'test@example.com',
            'buyer_name': 'Test User',
            'buyer_phone': '0744963858',
            'mobile_money_provider': 'invalid_provider'
        }
        
        response = self.client.post(payment_url, invalid_provider_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid mobile money provider', response.data['message'])
        
        # Test 4: Missing required fields
        print("  ❌ Test 4: Missing required fields...")
        empty_data = {}
        
        response = self.client.post(payment_url, empty_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['message'])
        
        print("  ✅ Error handling flow test passed!")


class DataConsistencyTests(APITestCase):
    """Test data consistency across different endpoints."""
    
    def setUp(self):
        """Set up test data for consistency tests."""
        # Create test user and tenant
        self.user = User.objects.create_user(
            email='consistency@example.com',
            password='testpass123',
            first_name='Consistency',
            last_name='Tester'
        )
        
        self.tenant = Tenant.objects.create(
            name='Consistency Test Company',
            subdomain='consistency-test'
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
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test data
        self.create_test_data()
    
    def create_test_data(self):
        """Create comprehensive test data."""
        # Create SMS packages
        self.package1 = SMSPackage.objects.create(
            name='Consistency Package 1',
            package_type='standard',
            credits=1000,
            price=Decimal('20000.00'),
            unit_price=Decimal('20.00'),
            is_popular=True,
            is_active=True,
            features=['1000 SMS Credits', 'Standard Support'],
            default_sender_id='ConsistencySender',
            allowed_sender_ids=['ConsistencySender'],
            sender_id_restriction='allowed_list'
        )
        
        self.package2 = SMSPackage.objects.create(
            name='Consistency Package 2',
            package_type='pro',
            credits=5000,
            price=Decimal('75000.00'),
            unit_price=Decimal('15.00'),
            is_popular=False,
            is_active=True,
            features=['5000 SMS Credits', 'Premium Support'],
            default_sender_id='ProSender',
            allowed_sender_ids=['ProSender', 'ConsistencySender'],
            sender_id_restriction='allowed_list'
        )
        
        # Create billing plan
        self.billing_plan = BillingPlan.objects.create(
            name='Consistency Plan',
            plan_type='professional',
            description='Consistency test plan',
            price=Decimal('50000.00'),
            currency='TZS',
            billing_cycle='monthly',
            max_contacts=5000,
            max_campaigns=50,
            max_sms_per_month=2000,
            features=['Consistency Features'],
            is_active=True
        )
        
        # Create subscription
        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.billing_plan,
            status='active',
            current_period_start=timezone.now().replace(day=1),
            current_period_end=timezone.now().replace(day=1) + timezone.timedelta(days=30),
            cancel_at_period_end=False
        )
        
        # Create SMS balance
        self.sms_balance = SMSBalance.objects.create(
            tenant=self.tenant,
            credits=1500,
            total_purchased=8000,
            total_used=6500
        )
        
        # Create purchases
        self.purchase1 = Purchase.objects.create(
            tenant=self.tenant,
            package=self.package1,
            amount=Decimal('20000.00'),
            credits=1000,
            unit_price=Decimal('20.00'),
            payment_method='zenopay_mobile_money',
            payment_reference='MPESA-CONSISTENCY-001',
            status='completed',
            completed_at=timezone.now() - timezone.timedelta(days=5)
        )
        
        self.purchase2 = Purchase.objects.create(
            tenant=self.tenant,
            package=self.package2,
            amount=Decimal('75000.00'),
            credits=5000,
            unit_price=Decimal('15.00'),
            payment_method='zenopay_mobile_money',
            payment_reference='MPESA-CONSISTENCY-002',
            status='completed',
            completed_at=timezone.now() - timezone.timedelta(days=2)
        )
        
        # Create usage records
        now = timezone.now()
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=100,
            cost=Decimal('2000.00'),
            created_at=now
        )
        UsageRecord.objects.create(
            tenant=self.tenant,
            credits_used=200,
            cost=Decimal('4000.00'),
            created_at=now - timezone.timedelta(days=1)
        )
    
    def test_package_data_consistency(self):
        """Test that package data is consistent across endpoints."""
        print("\n🔍 Testing Package Data Consistency...")
        
        # Get packages from list endpoint
        packages_url = reverse('sms-package-list')
        packages_response = self.client.get(packages_url)
        self.assertEqual(packages_response.status_code, status.HTTP_200_OK)
        
        packages = packages_response.data['results']
        package1_data = next(p for p in packages if p['name'] == 'Consistency Package 1')
        package2_data = next(p for p in packages if p['name'] == 'Consistency Package 2')
        
        # Verify package 1 data
        self.assertEqual(package1_data['credits'], 1000)
        self.assertEqual(package1_data['price'], '20000.00')
        self.assertEqual(package1_data['unit_price'], '20.00')
        self.assertTrue(package1_data['is_popular'])
        self.assertTrue(package1_data['is_active'])
        self.assertEqual(package1_data['savings_percentage'], 33.3)  # (30-20)/30 * 100
        self.assertEqual(package1_data['default_sender_id'], 'ConsistencySender')
        self.assertIn('ConsistencySender', package1_data['allowed_sender_ids'])
        self.assertEqual(package1_data['sender_id_restriction'], 'allowed_list')
        
        # Verify package 2 data
        self.assertEqual(package2_data['credits'], 5000)
        self.assertEqual(package2_data['price'], '75000.00')
        self.assertEqual(package2_data['unit_price'], '15.00')
        self.assertFalse(package2_data['is_popular'])
        self.assertTrue(package2_data['is_active'])
        self.assertEqual(package2_data['savings_percentage'], 50.0)  # (30-15)/30 * 100
        self.assertEqual(package2_data['default_sender_id'], 'ProSender')
        self.assertIn('ProSender', package2_data['allowed_sender_ids'])
        self.assertIn('ConsistencySender', package2_data['allowed_sender_ids'])
        self.assertEqual(package2_data['sender_id_restriction'], 'allowed_list')
        
        print("  ✅ Package data consistency verified!")
    
    def test_balance_data_consistency(self):
        """Test that balance data is consistent across endpoints."""
        print("\n🔍 Testing Balance Data Consistency...")
        
        # Get balance from balance endpoint
        balance_url = reverse('sms-balance')
        balance_response = self.client.get(balance_url)
        self.assertEqual(balance_response.status_code, status.HTTP_200_OK)
        
        balance_data = balance_response.data
        self.assertEqual(balance_data['credits'], 1500)
        self.assertEqual(balance_data['total_purchased'], 8000)
        self.assertEqual(balance_data['total_used'], 6500)
        
        # Get balance from overview endpoint
        overview_url = reverse('billing-overview')
        overview_response = self.client.get(overview_url)
        self.assertEqual(overview_response.status_code, status.HTTP_200_OK)
        
        overview_balance = overview_response.data['data']['sms_balance']
        self.assertEqual(overview_balance['credits'], 1500)
        self.assertEqual(overview_balance['total_purchased'], 8000)
        self.assertEqual(overview_balance['total_used'], 6500)
        
        # Verify calculations
        expected_balance = 8000 - 6500  # total_purchased - total_used
        self.assertEqual(balance_data['credits'], expected_balance)
        
        print("  ✅ Balance data consistency verified!")
    
    def test_purchase_data_consistency(self):
        """Test that purchase data is consistent across endpoints."""
        print("\n🔍 Testing Purchase Data Consistency...")
        
        # Get purchases from list endpoint
        purchases_url = reverse('sms-purchase-list')
        purchases_response = self.client.get(purchases_url)
        self.assertEqual(purchases_response.status_code, status.HTTP_200_OK)
        
        purchases = purchases_response.data['results']
        self.assertEqual(len(purchases), 2)
        
        # Find our purchases
        purchase1_data = next(p for p in purchases if p['package_name'] == 'Consistency Package 1')
        purchase2_data = next(p for p in purchases if p['package_name'] == 'Consistency Package 2')
        
        # Verify purchase 1 data
        self.assertEqual(purchase1_data['amount'], '20000.00')
        self.assertEqual(purchase1_data['credits'], 1000)
        self.assertEqual(purchase1_data['unit_price'], '20.00')
        self.assertEqual(purchase1_data['status'], 'completed')
        self.assertEqual(purchase1_data['payment_method_display'], 'ZenoPay Mobile Money')
        
        # Verify purchase 2 data
        self.assertEqual(purchase2_data['amount'], '75000.00')
        self.assertEqual(purchase2_data['credits'], 5000)
        self.assertEqual(purchase2_data['unit_price'], '15.00')
        self.assertEqual(purchase2_data['status'], 'completed')
        self.assertEqual(purchase2_data['payment_method_display'], 'ZenoPay Mobile Money')
        
        # Test individual purchase detail
        detail_url = reverse('sms-purchase-detail', kwargs={'pk': self.purchase1.id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        
        detail_data = detail_response.data
        self.assertEqual(detail_data['package_name'], 'Consistency Package 1')
        self.assertEqual(detail_data['amount'], '20000.00')
        self.assertEqual(detail_data['credits'], 1000)
        self.assertEqual(detail_data['status'], 'completed')
        
        print("  ✅ Purchase data consistency verified!")
    
    def test_subscription_data_consistency(self):
        """Test that subscription data is consistent across endpoints."""
        print("\n🔍 Testing Subscription Data Consistency...")
        
        # Get subscription from subscription endpoint
        subscription_url = reverse('subscription-detail')
        subscription_response = self.client.get(subscription_url)
        self.assertEqual(subscription_response.status_code, status.HTTP_200_OK)
        
        subscription_data = subscription_response.data
        self.assertEqual(subscription_data['plan_name'], 'Consistency Plan')
        self.assertEqual(subscription_data['status'], 'active')
        self.assertTrue(subscription_data['is_active'])
        
        # Get subscription from overview endpoint
        overview_url = reverse('billing-overview')
        overview_response = self.client.get(overview_url)
        self.assertEqual(overview_response.status_code, status.HTTP_200_OK)
        
        overview_subscription = overview_response.data['data']['subscription']
        self.assertEqual(overview_subscription['plan_name'], 'Consistency Plan')
        self.assertEqual(overview_subscription['status'], 'active')
        self.assertTrue(overview_subscription['is_active'])
        
        # Get plan from plans endpoint
        plans_url = reverse('plan-list')
        plans_response = self.client.get(plans_url)
        self.assertEqual(plans_response.status_code, status.HTTP_200_OK)
        
        plans = plans_response.data['results']
        plan_data = next(p for p in plans if p['name'] == 'Consistency Plan')
        self.assertEqual(plan_data['plan_type'], 'professional')
        self.assertEqual(plan_data['price'], '50000.00')
        self.assertEqual(plan_data['currency'], 'TZS')
        self.assertEqual(plan_data['billing_cycle'], 'monthly')
        self.assertEqual(plan_data['max_contacts'], 5000)
        self.assertEqual(plan_data['max_campaigns'], 50)
        self.assertEqual(plan_data['max_sms_per_month'], 2000)
        self.assertTrue(plan_data['is_active'])
        
        print("  ✅ Subscription data consistency verified!")
    
    def test_usage_statistics_consistency(self):
        """Test that usage statistics are consistent and accurate."""
        print("\n🔍 Testing Usage Statistics Consistency...")
        
        # Get usage statistics
        stats_url = reverse('sms-usage-statistics')
        stats_response = self.client.get(stats_url)
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        
        stats_data = stats_response.data['data']
        
        # Verify current balance matches SMS balance
        self.assertEqual(stats_data['current_balance'], 1500)
        
        # Verify total usage calculation
        total_usage = stats_data['total_usage']
        self.assertEqual(total_usage['credits'], 300)  # 100 + 200 from usage records
        self.assertEqual(total_usage['cost'], 6000.00)  # 2000 + 4000 from usage records
        
        # Verify period-specific usage
        daily_usage = stats_data['daily_usage']
        self.assertIn('credits', daily_usage)
        self.assertIn('cost', daily_usage)
        self.assertIn('period', daily_usage)
        
        # Verify usage trend data structure
        if 'usage_trend' in stats_data:
            trend_data = stats_data['usage_trend']
            self.assertIsInstance(trend_data, list)
            for trend_item in trend_data:
                self.assertIn('date', trend_item)
                self.assertIn('credits', trend_item)
                self.assertIn('cost', trend_item)
        
        print("  ✅ Usage statistics consistency verified!")


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['billing.integration_tests'])
