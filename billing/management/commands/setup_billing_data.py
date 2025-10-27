#!/usr/bin/env python3
"""
Management command to setup billing data for Mifumo WMS.
Creates SMS packages, billing plans, and sample data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from billing.models import SMSPackage, BillingPlan, SMSBalance
from messaging.models import Contact, Message, Campaign, Conversation
from messaging.models_sms import SMSMessage
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup billing data and sample data for Mifumo WMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            self.reset_data()

        self.stdout.write('Setting up billing data...')
        self.setup_sms_packages()
        self.setup_billing_plans()
        self.setup_sample_data()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup billing data!')
        )

    def reset_data(self):
        """Reset existing data."""
        SMSMessage.objects.all().delete()
        Message.objects.all().delete()
        Campaign.objects.all().delete()
        Conversation.objects.all().delete()
        Contact.objects.all().delete()
        SMSBalance.objects.all().delete()
        SMSPackage.objects.all().delete()
        BillingPlan.objects.all().delete()

    def setup_sms_packages(self):
        """Create SMS packages."""
        packages = [
            {
                'name': 'Lite',
                'package_type': 'lite',
                'credits': 5000,
                'price': 90000,  # 5000 * 18
                'unit_price': 18,
                'features': [
                    'Instant top-up',
                    'Basic delivery reports',
                    'Email receipt',
                ]
            },
            {
                'name': 'Standard',
                'package_type': 'standard',
                'credits': 50000,
                'price': 700000,  # 50000 * 14
                'unit_price': 14,
                'is_popular': True,
                'features': [
                    'Priority top-up & support',
                    'Advanced delivery analytics',
                    'Campaign scheduling',
                    'Team access',
                ]
            },
            {
                'name': 'Pro',
                'package_type': 'pro',
                'credits': 250000,
                'price': 3000000,  # 250000 * 12
                'unit_price': 12,
                'features': [
                    'Bulk campaign tools',
                    'Advanced analytics',
                    'API access',
                ]
            }
        ]

        for package_data in packages:
            package, created = SMSPackage.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            if created:
                self.stdout.write(f'Created SMS package: {package.name}')

    def setup_billing_plans(self):
        """Create billing plans."""
        plans = [
            {
                'name': 'Free Plan',
                'plan_type': 'free',
                'description': 'Perfect for getting started',
                'price': 0,
                'currency': 'TZS',
                'billing_cycle': 'monthly',
                'max_contacts': 100,
                'max_campaigns': 5,
                'max_sms_per_month': 100,
                'features': [
                    'Basic SMS sending',
                    'Contact management',
                    'Basic analytics',
                ]
            },
            {
                'name': 'Basic Plan',
                'plan_type': 'basic',
                'description': 'For small businesses',
                'price': 50000,
                'currency': 'TZS',
                'billing_cycle': 'monthly',
                'max_contacts': 1000,
                'max_campaigns': 50,
                'max_sms_per_month': 1000,
                'features': [
                    'SMS & WhatsApp messaging',
                    'Advanced contact management',
                    'Campaign scheduling',
                    'Basic analytics',
                ]
            },
            {
                'name': 'Professional Plan',
                'plan_type': 'professional',
                'description': 'For growing businesses',
                'price': 150000,
                'currency': 'TZS',
                'billing_cycle': 'monthly',
                'max_contacts': 10000,
                'max_campaigns': 500,
                'max_sms_per_month': 10000,
                'features': [
                    'All messaging features',
                    'Advanced analytics',
                    'API access',
                    'Priority support',
                ]
            },
            {
                'name': 'Enterprise Plan',
                'plan_type': 'enterprise',
                'description': 'For large organizations',
                'price': 500000,
                'currency': 'TZS',
                'billing_cycle': 'monthly',
                'max_contacts': None,  # Unlimited
                'max_campaigns': None,  # Unlimited
                'max_sms_per_month': None,  # Unlimited
                'features': [
                    'Unlimited everything',
                    'Custom integrations',
                    'Dedicated support',
                    'White-label options',
                ]
            }
        ]

        for plan_data in plans:
            plan, created = BillingPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created billing plan: {plan.name}')

    def setup_sample_data(self):
        """Create sample data for testing."""
        # Get or create a test tenant
        tenant, created = Tenant.objects.get_or_create(
            subdomain='demo-tenant',
            defaults={
                'name': 'Demo Tenant',
                'business_name': 'Demo Business Ltd',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'Created tenant: {tenant.name}')

        # Get or create a test user
        user, created = User.objects.get_or_create(
            email='demo@mifumo.com',
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'is_verified': True
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(f'Created user: {user.email}')

        # Create membership
        membership, created = Membership.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={
                'role': 'owner',
                'status': 'active'
            }
        )

        # Create SMS balance
        balance, created = SMSBalance.objects.get_or_create(
            tenant=tenant,
            defaults={'credits': 10000}
        )

        # Create sample contacts
        self.create_sample_contacts(tenant)
        
        # Create sample messages
        self.create_sample_messages(tenant)
        
        # Create sample campaigns
        self.create_sample_campaigns(tenant)

    def create_sample_contacts(self, tenant):
        """Create sample contacts."""
        contacts_data = [
            {'name': 'John Doe', 'phone_e164': '+255700000001', 'email': 'john@example.com'},
            {'name': 'Jane Smith', 'phone_e164': '+255700000002', 'email': 'jane@example.com'},
            {'name': 'Mike Johnson', 'phone_e164': '+255700000003', 'email': 'mike@example.com'},
            {'name': 'Sarah Wilson', 'phone_e164': '+255700000004', 'email': 'sarah@example.com'},
            {'name': 'David Brown', 'phone_e164': '+255700000005', 'email': 'david@example.com'},
        ]

        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                tenant=tenant,
                phone_e164=contact_data['phone_e164'],
                defaults={
                    'name': contact_data['name'],
                    'email': contact_data['email'],
                    'is_active': True,
                    'tags': ['demo', 'customer']
                }
            )
            if created:
                self.stdout.write(f'Created contact: {contact.name}')

    def create_sample_messages(self, tenant):
        """Create sample messages."""
        contacts = Contact.objects.filter(tenant=tenant)
        
        if not contacts.exists():
            return

        messages_data = [
            'Welcome to our service!',
            'Thank you for your purchase.',
            'Your order has been shipped.',
            'Don\'t forget to check out our new products.',
            'Happy holidays from our team!',
        ]

        for i in range(50):  # Create 50 sample messages
            contact = random.choice(contacts)
            message_text = random.choice(messages_data)
            
            # Create conversation if it doesn't exist
            conversation, created = Conversation.objects.get_or_create(
                tenant=tenant,
                contact=contact,
                defaults={'status': 'active'}
            )

            # Create message
            message = Message.objects.create(
                tenant=tenant,
                conversation=conversation,
                direction='out',
                provider='sms',
                text=message_text,
                status='delivered',
                sent_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )

            # Create SMS message record
            SMSMessage.objects.create(
                tenant=tenant,
                base_message=message,
                recipient=contact.phone_e164,
                message_text=message_text,
                status='delivered',
                cost_micro=25000  # 25 TZS in micro units
            )

        self.stdout.write('Created sample messages')

    def create_sample_campaigns(self, tenant):
        """Create sample campaigns."""
        campaigns_data = [
            {
                'name': 'Mother\'s Day Special Offers',
                'status': 'completed',
                'sent_count': 1250,
                'delivered_count': 1225,
                'read_count': 890,
                'total_recipients': 1250,
                'created_at': timezone.now() - timedelta(hours=2)
            },
            {
                'name': 'Product Launch - African Textiles',
                'status': 'running',
                'sent_count': 450,
                'delivered_count': 420,
                'read_count': 0,
                'total_recipients': 1000,
                'created_at': timezone.now() - timedelta(days=1)
            },
            {
                'name': 'Customer Satisfaction Survey',
                'status': 'scheduled',
                'sent_count': 0,
                'delivered_count': 0,
                'read_count': 0,
                'total_recipients': 500,
                'created_at': timezone.now() - timedelta(days=3)
            }
        ]

        for campaign_data in campaigns_data:
            campaign, created = Campaign.objects.get_or_create(
                tenant=tenant,
                name=campaign_data['name'],
                defaults=campaign_data
            )
            if created:
                self.stdout.write(f'Created campaign: {campaign.name}')

        self.stdout.write('Created sample campaigns')
