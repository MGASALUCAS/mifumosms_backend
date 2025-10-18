"""
Management command to list all SMS packages in the database.
"""
from django.core.management.base import BaseCommand
from billing.models import SMSPackage


class Command(BaseCommand):
    help = 'List all SMS packages in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active packages'
        )
        parser.add_argument(
            '--popular-only',
            action='store_true',
            help='Show only popular packages'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['lite', 'standard', 'pro', 'enterprise', 'custom'],
            help='Filter by package type'
        )

    def handle(self, *args, **options):
        # Build queryset based on filters
        queryset = SMSPackage.objects.all()
        
        if options['active_only']:
            queryset = queryset.filter(is_active=True)
            
        if options['popular_only']:
            queryset = queryset.filter(is_popular=True)
            
        if options['type']:
            queryset = queryset.filter(package_type=options['type'])

        # Order by price
        packages = queryset.order_by('price')

        if not packages.exists():
            self.stdout.write(
                self.style.WARNING('No SMS packages found matching the criteria.')
            )
            return

        # Display header
        self.stdout.write(
            self.style.SUCCESS(f'\nFound {packages.count()} SMS package(s):\n')
        )
        
        # Display packages in a table format
        self.stdout.write('-' * 120)
        self.stdout.write(
            f"{'Name':<15} {'Type':<10} {'Credits':<10} {'Price (TZS)':<15} "
            f"{'Unit Price':<12} {'Savings':<10} {'Popular':<8} {'Active':<8} {'Features':<20}"
        )
        self.stdout.write('-' * 120)

        for package in packages:
            features_str = ', '.join(package.features[:2]) if package.features else 'None'
            if len(package.features) > 2:
                features_str += '...'
                
            self.stdout.write(
                f"{package.name:<15} {package.package_type:<10} {package.credits:<10,} "
                f"{package.price:<15,.2f} {package.unit_price:<12,.2f} "
                f"{package.savings_percentage:<10.1f}% {'Yes' if package.is_popular else 'No':<8} "
                f"{'Yes' if package.is_active else 'No':<8} {features_str:<20}"
            )

        self.stdout.write('-' * 120)
        
        # Display summary statistics
        total_packages = packages.count()
        active_packages = packages.filter(is_active=True).count()
        popular_packages = packages.filter(is_popular=True).count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Total packages: {total_packages}')
        self.stdout.write(f'  Active packages: {active_packages}')
        self.stdout.write(f'  Popular packages: {popular_packages}')
        
        if packages.exists():
            min_price = packages.first().price
            max_price = packages.last().price
            self.stdout.write(f'  Price range: {min_price:,.2f} - {max_price:,.2f} TZS')
