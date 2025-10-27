#!/usr/bin/env python3
"""
Management command to setup SMS packages with proper sender ID configurations.
This ensures all packages are created with the correct pricing and sender ID settings.
"""

from django.core.management.base import BaseCommand
from billing.models import SMSPackage
from decimal import Decimal


class Command(BaseCommand):
    help = 'Setup SMS packages with proper sender ID configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing packages before creating new ones',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing packages with new configurations',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing SMS packages...')
            SMSPackage.objects.all().delete()

        self.stdout.write('Setting up SMS packages...')
        self.setup_sms_packages(update=options['update'])
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup SMS packages!')
        )

    def setup_sms_packages(self, update=False):
        """Create SMS packages with proper configurations."""
        packages = [
            {
                'name': 'Lite',
                'package_type': 'lite',
                'credits': 5000,
                'price': Decimal('90000.00'),  # 5000 * 18
                'unit_price': Decimal('18.00'),
                'is_popular': False,
                'is_active': True,
                'features': [
                    'Instant top-up',
                    'Basic delivery reports',
                    'Email receipt',
                    'Standard sender ID support'
                ],
                'default_sender_id': 'MIFUMO',
                'allowed_sender_ids': ['MIFUMO', 'SMS', 'INFO'],
                'sender_id_restriction': 'allowed_list'
            },
            {
                'name': 'Standard',
                'package_type': 'standard',
                'credits': 50000,
                'price': Decimal('700000.00'),  # 50000 * 14
                'unit_price': Decimal('14.00'),
                'is_popular': True,
                'is_active': True,
                'features': [
                    'Priority top-up & support',
                    'Advanced delivery analytics',
                    'Campaign scheduling',
                    'Team access',
                    'Custom sender ID support'
                ],
                'default_sender_id': 'MIFUMO',
                'allowed_sender_ids': ['MIFUMO', 'SMS', 'INFO', 'ALERT', 'NOTIFY'],
                'sender_id_restriction': 'allowed_list'
            },
            {
                'name': 'Pro',
                'package_type': 'pro',
                'credits': 250000,
                'price': Decimal('3000000.00'),  # 250000 * 12
                'unit_price': Decimal('12.00'),
                'is_popular': False,
                'is_active': True,
                'features': [
                    'Bulk campaign tools',
                    'Advanced analytics',
                    'API access',
                    'Custom sender ID support',
                    'Priority support'
                ],
                'default_sender_id': 'MIFUMO',
                'allowed_sender_ids': ['MIFUMO', 'SMS', 'INFO', 'ALERT', 'NOTIFY', 'PRO', 'BIZ'],
                'sender_id_restriction': 'allowed_list'
            }
        ]

        for package_data in packages:
            if update:
                # Update existing package
                try:
                    package = SMSPackage.objects.get(name=package_data['name'])
                    for key, value in package_data.items():
                        setattr(package, key, value)
                    package.save()
                    self.stdout.write(f'Updated SMS package: {package.name}')
                except SMSPackage.DoesNotExist:
                    # Create if doesn't exist
                    package = SMSPackage.objects.create(**package_data)
                    self.stdout.write(f'Created SMS package: {package.name}')
            else:
                # Create or get existing
                package, created = SMSPackage.objects.get_or_create(
                    name=package_data['name'],
                    defaults=package_data
                )
                if created:
                    self.stdout.write(f'Created SMS package: {package.name}')
                else:
                    self.stdout.write(f'SMS package already exists: {package.name}')

        # Display current packages
        self.stdout.write('\nCurrent SMS Packages:')
        for package in SMSPackage.objects.all().order_by('price'):
            self.stdout.write(
                f'- {package.name}: {package.credits:,} credits, '
                f'{package.price:,.2f} TZS, {package.unit_price:.2f} TZS/SMS '
                f'({package.savings_percentage:.1f}% savings)'
            )
