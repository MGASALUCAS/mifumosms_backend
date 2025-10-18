"""
Management command to delete SMS packages.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from billing.models import SMSPackage, Purchase


class Command(BaseCommand):
    help = 'Delete SMS packages from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=str,
            help='Package ID (UUID) to delete'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Package name to delete'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete even if packages have associated purchases'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
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

        # Check for associated purchases
        purchases = Purchase.objects.filter(package=package)
        if purchases.exists() and not options['force']:
            raise CommandError(
                f'Cannot delete package "{package.name}" because it has {purchases.count()} '
                f'associated purchase(s). Use --force to delete anyway, or consider '
                f'deactivating the package instead.'
            )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete package "{package.name}"\n'
                    f'  - ID: {package.id}\n'
                    f'  - Credits: {package.credits:,}\n'
                    f'  - Price: {package.price:,.2f} TZS\n'
                    f'  - Associated purchases: {purchases.count()}\n'
                    f'  - Force delete: {"Yes" if options["force"] else "No"}'
                )
            )
            return

        try:
            with transaction.atomic():
                # Store package info for display
                package_name = package.name
                package_credits = package.credits
                package_price = package.price
                purchase_count = purchases.count()
                
                # Delete the package
                package.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted SMS package: {package_name}\n'
                        f'  - Credits: {package_credits:,}\n'
                        f'  - Price: {package_price:,.2f} TZS\n'
                        f'  - Associated purchases: {purchase_count}'
                    )
                )

        except Exception as e:
            raise CommandError(f'Error deleting SMS package: {str(e)}')
