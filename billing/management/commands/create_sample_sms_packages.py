"""
Management command to create sample SMS packages for testing.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from billing.models import SMSPackage


class Command(BaseCommand):
    help = 'Create sample SMS packages for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear all existing packages before creating new ones'
        )
        parser.add_argument(
            '--package-set',
            type=str,
            choices=['basic', 'comprehensive', 'enterprise'],
            default='basic',
            help='Package set to create (default: basic)'
        )

    def handle(self, *args, **options):
        if options['clear_existing']:
            if SMSPackage.objects.exists():
                self.stdout.write(
                    self.style.WARNING('Clearing existing SMS packages...')
                )
                SMSPackage.objects.all().delete()

        try:
            with transaction.atomic():
                packages = self.get_package_data(options['package_set'])
                created_packages = []

                for package_data in packages:
                    # Check if package already exists
                    if SMSPackage.objects.filter(name=package_data['name']).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Package "{package_data["name"]}" already exists. Skipping...'
                            )
                        )
                        continue

                    package = SMSPackage.objects.create(**package_data)
                    created_packages.append(package)

                if created_packages:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created {len(created_packages)} SMS package(s):\n'
                        )
                    )
                    
                    for package in created_packages:
                        self.stdout.write(
                            f'  ✓ {package.name} - {package.credits:,} credits - '
                            f'{package.price:,.2f} TZS - {package.savings_percentage:.1f}% savings'
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING('No new packages were created.')
                    )

        except Exception as e:
            raise CommandError(f'Error creating sample packages: {str(e)}')

    def get_package_data(self, package_set):
        """Get package data based on the selected set."""
        
        if package_set == 'basic':
            return [
                {
                    'name': 'Starter',
                    'package_type': 'lite',
                    'credits': 1000,
                    'price': 50000,
                    'unit_price': 50.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Basic SMS', 'Email Support'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Business',
                    'package_type': 'standard',
                    'credits': 10000,
                    'price': 400000,
                    'unit_price': 40.00,
                    'is_popular': True,
                    'is_active': True,
                    'features': ['Priority SMS', 'Phone Support', 'API Access'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Professional',
                    'package_type': 'pro',
                    'credits': 50000,
                    'price': 1500000,
                    'unit_price': 30.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Priority SMS', '24/7 Support', 'API Access', 'Analytics'],
                    'sender_id_restriction': 'none'
                }
            ]
        
        elif package_set == 'comprehensive':
            return [
                {
                    'name': 'Starter',
                    'package_type': 'lite',
                    'credits': 1000,
                    'price': 50000,
                    'unit_price': 50.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Basic SMS', 'Email Support'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Growth',
                    'package_type': 'standard',
                    'credits': 5000,
                    'price': 200000,
                    'unit_price': 40.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Priority SMS', 'Email Support', 'Basic Analytics'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Business',
                    'package_type': 'standard',
                    'credits': 25000,
                    'price': 800000,
                    'unit_price': 32.00,
                    'is_popular': True,
                    'is_active': True,
                    'features': ['Priority SMS', 'Phone Support', 'API Access', 'Analytics'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Professional',
                    'package_type': 'pro',
                    'credits': 100000,
                    'price': 2500000,
                    'unit_price': 25.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Priority SMS', '24/7 Support', 'API Access', 'Advanced Analytics', 'Webhooks'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Enterprise',
                    'package_type': 'enterprise',
                    'credits': 500000,
                    'price': 10000000,
                    'unit_price': 20.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Priority SMS', 'Dedicated Support', 'Full API Access', 'Advanced Analytics', 'Webhooks', 'Custom Integration'],
                    'sender_id_restriction': 'none'
                }
            ]
        
        elif package_set == 'enterprise':
            return [
                {
                    'name': 'Basic Enterprise',
                    'package_type': 'enterprise',
                    'credits': 100000,
                    'price': 2000000,
                    'unit_price': 20.00,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Enterprise SMS', 'Dedicated Support', 'API Access'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Advanced Enterprise',
                    'package_type': 'enterprise',
                    'credits': 500000,
                    'price': 8000000,
                    'unit_price': 16.00,
                    'is_popular': True,
                    'is_active': True,
                    'features': ['Enterprise SMS', '24/7 Dedicated Support', 'Full API Access', 'Advanced Analytics', 'Webhooks'],
                    'sender_id_restriction': 'none'
                },
                {
                    'name': 'Ultimate Enterprise',
                    'package_type': 'enterprise',
                    'credits': 2000000,
                    'price': 25000000,
                    'unit_price': 12.50,
                    'is_popular': False,
                    'is_active': True,
                    'features': ['Enterprise SMS', 'White-label Support', 'Full API Access', 'Advanced Analytics', 'Webhooks', 'Custom Integration', 'SLA Guarantee'],
                    'sender_id_restriction': 'none'
                }
            ]

