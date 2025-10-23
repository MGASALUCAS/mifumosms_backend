#!/usr/bin/env python3
"""
Clear duplicate phone numbers and generate random unique ones
"""

import os
import sys
import django
import random
import string

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from django.db.models import Count

def generate_random_phone():
    """Generate a random Tanzanian phone number."""
    # Tanzanian mobile prefixes
    prefixes = ['061', '062', '063', '064', '065', '066', '067', '068', '069', '071', '072', '073', '074', '075', '076', '077', '078', '079']
    
    # Select random prefix
    prefix = random.choice(prefixes)
    
    # Generate 7 random digits
    suffix = ''.join(random.choices(string.digits, k=7))
    
    return f"{prefix}{suffix}"

def clear_duplicate_phones():
    """Clear duplicate phone numbers and generate random unique ones."""
    print("=" * 80)
    print("CLEARING DUPLICATE PHONE NUMBERS AND GENERATING RANDOM UNIQUE ONES")
    print("=" * 80)
    
    try:
        # Find all users with phone numbers
        users_with_phones = User.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
        print(f"Total users with phone numbers: {users_with_phones.count()}")
        
        # Find duplicate phone numbers
        duplicates = User.objects.values('phone_number') \
                                 .annotate(phone_count=Count('phone_number')) \
                                 .filter(phone_count__gt=1, phone_number__isnull=False) \
                                 .exclude(phone_number='')
        
        print(f"Duplicate phone numbers found: {duplicates.count()}")
        
        # Process each duplicate phone number
        for duplicate in duplicates:
            phone_number = duplicate['phone_number']
            count = duplicate['phone_count']
            
            print(f"\nProcessing phone number: {phone_number} (used by {count} users)")
            
            # Get all users with this phone number
            users_with_duplicate_phone = User.objects.filter(phone_number=phone_number).order_by('created_at')
            
            # Keep the first user (oldest), change others to random numbers
            for i, user in enumerate(users_with_duplicate_phone):
                if i == 0:
                    print(f"  Keeping original phone for: {user.email}")
                    continue
                
                # Generate a new random phone number
                new_phone = generate_random_phone()
                
                # Make sure the new phone number is unique
                while User.objects.filter(phone_number=new_phone).exists():
                    new_phone = generate_random_phone()
                
                # Update the user's phone number
                old_phone = user.phone_number
                user.phone_number = new_phone
                user.save(update_fields=['phone_number'])
                
                print(f"  Changed {user.email}: {old_phone} -> {new_phone}")
        
        # Also clear any empty phone numbers and set them to random ones
        print(f"\n" + "=" * 50)
        print("PROCESSING USERS WITH EMPTY PHONE NUMBERS")
        print("=" * 50)
        
        users_with_empty_phones = User.objects.filter(phone_number__isnull=True) | User.objects.filter(phone_number='')
        print(f"Users with empty phone numbers: {users_with_empty_phones.count()}")
        
        for user in users_with_empty_phones:
            # Generate a new random phone number
            new_phone = generate_random_phone()
            
            # Make sure the new phone number is unique
            while User.objects.filter(phone_number=new_phone).exists():
                new_phone = generate_random_phone()
            
            # Update the user's phone number
            user.phone_number = new_phone
            user.save(update_fields=['phone_number'])
            
            print(f"  Set phone for {user.email}: {new_phone}")
        
        # Final verification
        print(f"\n" + "=" * 50)
        print("FINAL VERIFICATION")
        print("=" * 50)
        
        # Check for remaining duplicates
        remaining_duplicates = User.objects.values('phone_number') \
                                          .annotate(phone_count=Count('phone_number')) \
                                          .filter(phone_count__gt=1, phone_number__isnull=False) \
                                          .exclude(phone_number='')
        
        if remaining_duplicates.count() == 0:
            print("SUCCESS: No duplicate phone numbers found!")
        else:
            print(f"WARNING: {remaining_duplicates.count()} duplicate phone numbers still exist!")
            for duplicate in remaining_duplicates:
                print(f"  {duplicate['phone_number']}: {duplicate['phone_count']} users")
        
        # Show final statistics
        total_users = User.objects.count()
        users_with_phones = User.objects.exclude(phone_number__isnull=True).exclude(phone_number='').count()
        unique_phones = User.objects.exclude(phone_number__isnull=True).exclude(phone_number='').values('phone_number').distinct().count()
        
        print(f"\nFinal Statistics:")
        print(f"  Total users: {total_users}")
        print(f"  Users with phone numbers: {users_with_phones}")
        print(f"  Unique phone numbers: {unique_phones}")
        
        if users_with_phones == unique_phones:
            print("SUCCESS: All phone numbers are now unique!")
        else:
            print("WARNING: Some phone numbers are still duplicated!")
        
    except Exception as e:
        print(f"Error clearing duplicate phones: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the script."""
    print("Clearing Duplicate Phone Numbers and Generating Random Unique Ones")
    print("=" * 80)
    
    clear_duplicate_phones()

if __name__ == "__main__":
    main()
