"""
Management command to add SMS packages to the database.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from billing.models import SMSPackage


class Command(BaseCommand):
    help = 'Add SMS packages to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Package name (e.g., "Starter", "Business")'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['lite', 'standard', 'pro', 'enterprise', 'custom'],
            required=True,
            help='Package type'
        )
        parser.add_argument(
            '--credits',
            type=int,
            required=True,
            help='Number of SMS credits'
        )
        parser.add_argument(
            '--price',
            type=float,
            required=True,
            help='Price in TZS'
        )
        parser.add_argument(
            '--unit-price',
            type=float,
            required=True,
            help='Price per SMS in TZS'
        )
        parser.add_argument(
            '--popular',
            action='store_true',
            help='Mark as popular package'
        )
        parser.add_argument(
            '--active',
            action='store_true',
            default=True,
            help='Mark as active (default: True)'
        )
        parser.add_argument(
            '--features',
            type=str,
            nargs='*',
            default=[],
            help='List of features (e.g., "Priority Support" "API Access")'
        )
        parser.add_argument(
            '--default-sender-id',
            type=str,
            help='Default sender ID for this package'
        )
        parser.add_argument(
            '--sender-restriction',
            type=str,
            choices=['none', 'default_only', 'allowed_list', 'custom_only'],
            default='none',
            help='Sender ID restriction policy'
        )
        parser.add_argument(
            '--allowed-sender-ids',
            type=str,
            nargs='*',
            default=[],
            help='List of allowed sender IDs'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Check if package with same name already exists
                if SMSPackage.objects.filter(name=options['name']).exists():
                    raise CommandError(f'Package with name "{options["name"]}" already exists.')

                # Create the package
                package = SMSPackage.objects.create(
                    name=options['name'],
                    package_type=options['type'],
                    credits=options['credits'],
                    price=options['price'],
                    unit_price=options['unit_price'],
                    is_popular=options['popular'],
                    is_active=options['active'],
                    features=options['features'],
                    default_sender_id=options.get('default_sender_id'),
                    sender_id_restriction=options['sender_restriction'],
                    allowed_sender_ids=options['allowed_sender_ids']
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created SMS package: {package.name}\n'
                        f'  - Credits: {package.credits:,}\n'
                        f'  - Price: {package.price:,.2f} TZS\n'
                        f'  - Unit Price: {package.unit_price:,.2f} TZS\n'
                        f'  - Savings: {package.savings_percentage:.1f}%\n'
                        f'  - Popular: {"Yes" if package.is_popular else "No"}\n'
                        f'  - Active: {"Yes" if package.is_active else "No"}\n'
                        f'  - Features: {", ".join(package.features) if package.features else "None"}\n'
                        f'  - Sender ID Restriction: {package.sender_id_restriction}\n'
                        f'  - Allowed Sender IDs: {", ".join(package.allowed_sender_ids) if package.allowed_sender_ids else "None"}'
                    )
                )

        except Exception as e:
            raise CommandError(f'Error creating SMS package: {str(e)}')
