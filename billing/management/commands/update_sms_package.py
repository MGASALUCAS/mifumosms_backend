"""
Management command to update existing SMS packages.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from billing.models import SMSPackage


class Command(BaseCommand):
    help = 'Update existing SMS packages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=str,
            help='Package ID (UUID) to update'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Package name to search for'
        )
        parser.add_argument(
            '--new-name',
            type=str,
            help='New package name'
        )
        parser.add_argument(
            '--credits',
            type=int,
            help='New number of SMS credits'
        )
        parser.add_argument(
            '--price',
            type=float,
            help='New price in TZS'
        )
        parser.add_argument(
            '--unit-price',
            type=float,
            help='New price per SMS in TZS'
        )
        parser.add_argument(
            '--popular',
            action='store_true',
            help='Mark as popular package'
        )
        parser.add_argument(
            '--not-popular',
            action='store_true',
            help='Remove popular status'
        )
        parser.add_argument(
            '--active',
            action='store_true',
            help='Mark as active'
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Mark as inactive'
        )
        parser.add_argument(
            '--features',
            type=str,
            nargs='*',
            help='List of features'
        )

    def handle(self, *args, **options):
        # Find the package
        package = None
        
        if options['id']:
            try:
                package = SMSPackage.objects.get(id=options['id'])
            except SMSPackage.DoesNotExist:
                raise CommandError(f'Package with ID "{options["id"]}" not found.')
        elif options['name']:
            try:
                package = SMSPackage.objects.get(name=options['name'])
            except SMSPackage.DoesNotExist:
                raise CommandError(f'Package with name "{options["name"]}" not found.')
        else:
            raise CommandError('You must provide either --id or --name to identify the package.')

        try:
            with transaction.atomic():
                # Track changes
                changes = []
                
                # Update fields if provided
                if options['new_name']:
                    if SMSPackage.objects.filter(name=options['new_name']).exclude(id=package.id).exists():
                        raise CommandError(f'Package with name "{options["new_name"]}" already exists.')
                    package.name = options['new_name']
                    changes.append(f'Name: {options["new_name"]}')
                
                if options['credits'] is not None:
                    package.credits = options['credits']
                    changes.append(f'Credits: {options["credits"]:,}')
                
                if options['price'] is not None:
                    package.price = options['price']
                    changes.append(f'Price: {options["price"]:,.2f} TZS')
                
                if options['unit_price'] is not None:
                    package.unit_price = options['unit_price']
                    changes.append(f'Unit Price: {options["unit_price"]:,.2f} TZS')
                
                if options['popular']:
                    package.is_popular = True
                    changes.append('Popular: Yes')
                
                if options['not_popular']:
                    package.is_popular = False
                    changes.append('Popular: No')
                
                if options['active']:
                    package.is_active = True
                    changes.append('Active: Yes')
                
                if options['inactive']:
                    package.is_active = False
                    changes.append('Active: No')
                
                if options['features'] is not None:
                    package.features = options['features']
                    changes.append(f'Features: {", ".join(options["features"])}')
                
                if not changes:
                    self.stdout.write(
                        self.style.WARNING('No changes specified. Package remains unchanged.')
                    )
                    return
                
                # Save the package
                package.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated SMS package: {package.name}\n'
                        f'Changes made:\n' + 
                        '\n'.join(f'  - {change}' for change in changes) + '\n' +
                        f'Updated package details:\n'
                        f'  - Credits: {package.credits:,}\n'
                        f'  - Price: {package.price:,.2f} TZS\n'
                        f'  - Unit Price: {package.unit_price:,.2f} TZS\n'
                        f'  - Savings: {package.savings_percentage:.1f}%\n'
                        f'  - Popular: {"Yes" if package.is_popular else "No"}\n'
                        f'  - Active: {"Yes" if package.is_active else "No"}\n'
                        f'  - Features: {", ".join(package.features) if package.features else "None"}'
                    )
                )

        except Exception as e:
            raise CommandError(f'Error updating SMS package: {str(e)}')
