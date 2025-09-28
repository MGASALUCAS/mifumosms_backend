"""
Django management command to create an admin user with tenant assignment.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin user with tenant assignment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@mifumo.com',
            help='Admin email address'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='Admin first name'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Admin last name'
        )
        parser.add_argument(
            '--tenant-name',
            type=str,
            default='Mifumo Admin',
            help='Tenant name'
        )
        parser.add_argument(
            '--tenant-subdomain',
            type=str,
            default='admin',
            help='Tenant subdomain'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        tenant_name = options['tenant_name']
        tenant_subdomain = options['tenant_subdomain']

        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'User with email {email} already exists!')
                )
                user = User.objects.get(email=email)
            else:
                # Create superuser
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created superuser: {email}')
                )

            # Check if tenant already exists
            if Tenant.objects.filter(subdomain=tenant_subdomain).exists():
                self.stdout.write(
                    self.style.WARNING(f'Tenant with subdomain {tenant_subdomain} already exists!')
                )
                tenant = Tenant.objects.get(subdomain=tenant_subdomain)
            else:
                # Create tenant
                tenant = Tenant.objects.create(
                    name=tenant_name,
                    subdomain=tenant_subdomain,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created tenant: {tenant_name}')
                )

            # Create membership for user
            from tenants.models import Membership
            membership, created = Membership.objects.get_or_create(
                user=user,
                tenant=tenant,
                defaults={
                    'role': 'owner',
                    'status': 'active'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created membership: {user.email} -> {tenant.name} (owner)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Membership already exists: {user.email} -> {tenant.name}')
                )

            # Display summary
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('🎉 Setup completed successfully!'))
            self.stdout.write('='*50)
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🔑 Password: {password}')
            self.stdout.write(f'👤 Name: {first_name} {last_name}')
            self.stdout.write(f'🏢 Tenant: {tenant.name} ({tenant.subdomain})')
            self.stdout.write(f'🌐 Admin URL: http://localhost:8000/admin/')
            self.stdout.write('='*50)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            raise
