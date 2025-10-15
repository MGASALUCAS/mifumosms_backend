#!/usr/bin/env python
"""
Simple script to add test purchase data for testing.
Run this with: python manage.py shell < add_test_purchases.py
"""
from django.contrib.auth import get_user_model
from billing.models import SMSPackage, Purchase
from datetime import datetime, timedelta
import random

User = get_user_model()

# Get the admin user
try:
    user = User.objects.get(email='admin2@mifumo.com')
    print(f"✅ Found user: {user.email}")
except User.DoesNotExist:
    print("❌ User admin2@mifumo.com not found!")
    exit()

# Create test SMS packages if they don't exist
packages_data = [
    {
        'name': 'Starter Package',
        'package_type': 'lite',
        'credits': 50,
        'price': 1250.00,
        'unit_price': 25.00,
        'is_popular': False,
        'features': ['Basic SMS', 'Email Support']
    },
    {
        'name': 'Standard Package',
        'package_type': 'standard',
        'credits': 100,
        'price': 2250.00,
        'unit_price': 22.50,
        'is_popular': True,
        'features': ['SMS + WhatsApp', 'Priority Support', 'Analytics']
    },
    {
        'name': 'Professional Package',
        'package_type': 'pro',
        'credits': 500,
        'price': 10000.00,
        'unit_price': 20.00,
        'is_popular': False,
        'features': ['All Channels', 'Advanced Analytics', 'API Access']
    }
]

packages = []
for pkg_data in packages_data:
    package, created = SMSPackage.objects.get_or_create(
        name=pkg_data['name'],
        defaults=pkg_data
    )
    packages.append(package)
    if created:
        print(f"✅ Created package: {package.name}")
    else:
        print(f"✅ Using existing package: {package.name}")

# Clear existing test purchases for this user
Purchase.objects.filter(user=user).delete()
print("🧹 Cleared existing test purchases")

# Create test purchases
purchase_statuses = ['completed', 'pending', 'failed', 'cancelled']
payment_methods = ['mpesa', 'tigopesa', 'airtelmoney', 'bank_transfer']

base_date = datetime.now()
purchases_created = 0

for i in range(10):  # Create 10 test purchases
    # Random date within last 3 months
    days_ago = random.randint(0, 90)
    purchase_date = base_date - timedelta(days=days_ago)
    
    # Random package
    package = random.choice(packages)
    
    # Random status (weighted towards completed)
    status_weights = [0.7, 0.15, 0.1, 0.05]  # completed, pending, failed, cancelled
    status = random.choices(purchase_statuses, weights=status_weights)[0]
    
    # Random payment method
    payment_method = random.choice(payment_methods)
    
    # Generate invoice number
    invoice_number = f"INV-{purchase_date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # Create purchase
    purchase = Purchase.objects.create(
        user=user,
        package=package,
        invoice_number=invoice_number,
        amount=package.price,
        credits=package.credits,
        unit_price=package.unit_price,
        payment_method=payment_method,
        payment_reference=f"REF{random.randint(100000, 999999)}" if payment_method != 'bank_transfer' else '',
        status=status,
        created_at=purchase_date
    )
    
    # Set completed_at if status is completed
    if status == 'completed':
        purchase.completed_at = purchase_date + timedelta(minutes=random.randint(1, 30))
        purchase.save()
    
    purchases_created += 1

print(f"✅ Created {purchases_created} test purchases")

# Print some sample purchase IDs for testing
sample_purchases = Purchase.objects.filter(user=user)[:3]
print(f"\n🔍 Sample Purchase IDs for testing:")
for purchase in sample_purchases:
    print(f"   - {purchase.id} ({purchase.invoice_number}) - {purchase.status}")

print(f"\n🎯 Ready for Postman testing!")
print(f"   User: {user.email}")
print(f"   Purchases: {purchases_created}")
