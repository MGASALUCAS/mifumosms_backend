#!/usr/bin/env python3
"""
Phone number normalization and duplicate detection script.
This script checks for phone number duplicates across all tables and normalizes them.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.db import connection
from accounts.models import User
from messaging.models import Contact, Conversation, Message
from tenants.models import Tenant
import re

def normalize_phone_number(phone_number):
    """
    Normalize phone number to a standard format.
    
    Examples:
    +25514852618 -> 25514852618 (this is 255 + 14852618)
    0614853618 -> 255614853618 (this is 255 + 614853618)
    
    The issue: +25514852618 and 0614853618 are DIFFERENT numbers!
    +25514852618 = 255 + 14852618 (11 digits total)
    0614853618 = 255 + 614853618 (12 digits total)
    """
    if not phone_number:
        return None
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', str(phone_number))
    
    # Remove leading +
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Handle different formats
    if len(cleaned) == 10 and cleaned.startswith('0'):
        # Local format: 0614853618 -> 255614853618
        cleaned = '255' + cleaned[1:]
    elif len(cleaned) == 9 and cleaned.startswith('6'):
        # Local format without 0: 614853618 -> 255614853618
        cleaned = '255' + cleaned
    elif len(cleaned) == 12 and cleaned.startswith('255'):
        # Already in international format: 255614853618
        pass
    elif len(cleaned) == 11 and cleaned.startswith('255'):
        # International format: 25514852618
        pass
    
    return cleaned

def find_phone_number_duplicates():
    """Find all phone number duplicates across the database."""
    print("=" * 80)
    print("PHONE NUMBER DUPLICATE DETECTION")
    print("=" * 80)
    
    duplicates_found = []
    
    # Check Users table
    print("\n1. Checking Users table...")
    users = User.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
    user_phones = {}
    
    for user in users:
        normalized = normalize_phone_number(user.phone_number)
        if normalized:
            if normalized not in user_phones:
                user_phones[normalized] = []
            user_phones[normalized].append({
                'id': user.id,
                'email': user.email,
                'phone': user.phone_number,
                'normalized': normalized
            })
    
    # Find duplicates in users
    for normalized_phone, users_list in user_phones.items():
        if len(users_list) > 1:
            duplicates_found.append({
                'table': 'User',
                'normalized_phone': normalized_phone,
                'records': users_list
            })
            print(f"  DUPLICATE FOUND: {normalized_phone}")
            for user in users_list:
                print(f"    User ID {user['id']}: {user['email']} - {user['phone']}")
    
    # Check Contacts table
    print("\n2. Checking Contacts table...")
    contacts = Contact.objects.exclude(phone_e164__isnull=True).exclude(phone_e164='')
    contact_phones = {}
    
    for contact in contacts:
        normalized = normalize_phone_number(contact.phone_e164)
        if normalized:
            if normalized not in contact_phones:
                contact_phones[normalized] = []
            contact_phones[normalized].append({
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone_e164,
                'normalized': normalized,
                'tenant': contact.tenant.name if contact.tenant else 'No Tenant'
            })
    
    # Find duplicates in contacts
    for normalized_phone, contacts_list in contact_phones.items():
        if len(contacts_list) > 1:
            duplicates_found.append({
                'table': 'Contact',
                'normalized_phone': normalized_phone,
                'records': contacts_list
            })
            print(f"  DUPLICATE FOUND: {normalized_phone}")
            for contact in contacts_list:
                print(f"    Contact ID {contact['id']}: {contact['name']} - {contact['phone']} (Tenant: {contact['tenant']})")
    
    # Check Messages table for recipient numbers
    print("\n3. Checking Messages table...")
    messages = Message.objects.exclude(recipient_number__isnull=True).exclude(recipient_number='')
    message_phones = {}
    
    for message in messages:
        normalized = normalize_phone_number(message.recipient_number)
        if normalized:
            if normalized not in message_phones:
                message_phones[normalized] = []
            message_phones[normalized].append({
                'id': message.id,
                'recipient': message.recipient_number,
                'normalized': normalized,
                'tenant': message.tenant.name if message.tenant else 'No Tenant',
                'created_at': message.created_at
            })
    
    # Find duplicates in messages
    for normalized_phone, messages_list in message_phones.items():
        if len(messages_list) > 1:
            duplicates_found.append({
                'table': 'Message',
                'normalized_phone': normalized_phone,
                'records': messages_list
            })
            print(f"  DUPLICATE FOUND: {normalized_phone}")
            for message in messages_list:
                print(f"    Message ID {message['id']}: {message['recipient']} (Tenant: {message['tenant']}, Date: {message['created_at']})")
    
    # Summary
    print(f"\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total duplicates found: {len(duplicates_found)}")
    
    if duplicates_found:
        print("\nDuplicate groups:")
        for i, duplicate in enumerate(duplicates_found, 1):
            print(f"{i}. {duplicate['table']} - {duplicate['normalized_phone']} ({len(duplicate['records'])} records)")
    else:
        print("No duplicates found!")
    
    return duplicates_found

def normalize_all_phone_numbers():
    """Normalize all phone numbers in the database."""
    print("\n" + "=" * 80)
    print("PHONE NUMBER NORMALIZATION")
    print("=" * 80)
    
    # Normalize Users
    print("\n1. Normalizing Users...")
    users_updated = 0
    users = User.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
    
    for user in users:
        original = user.phone_number
        normalized = normalize_phone_number(original)
        if normalized and normalized != original:
            user.phone_number = normalized
            user.save(update_fields=['phone_number'])
            users_updated += 1
            print(f"  Updated User {user.id}: {original} -> {normalized}")
    
    print(f"  Users updated: {users_updated}")
    
    # Normalize Contacts
    print("\n2. Normalizing Contacts...")
    contacts_updated = 0
    contacts = Contact.objects.exclude(phone_e164__isnull=True).exclude(phone_e164='')
    
    for contact in contacts:
        original = contact.phone_e164
        normalized = normalize_phone_number(original)
        if normalized and normalized != original:
            contact.phone_e164 = normalized
            contact.save(update_fields=['phone_e164'])
            contacts_updated += 1
            print(f"  Updated Contact {contact.id}: {original} -> {normalized}")
    
    print(f"  Contacts updated: {contacts_updated}")
    
    # Normalize Messages
    print("\n3. Normalizing Messages...")
    messages_updated = 0
    messages = Message.objects.exclude(recipient_number__isnull=True).exclude(recipient_number='')
    
    for message in messages:
        original = message.recipient_number
        normalized = normalize_phone_number(original)
        if normalized and normalized != original:
            message.recipient_number = normalized
            message.save(update_fields=['recipient_number'])
            messages_updated += 1
            print(f"  Updated Message {message.id}: {original} -> {normalized}")
    
    print(f"  Messages updated: {messages_updated}")
    
    print(f"\nTotal records updated: {users_updated + contacts_updated + messages_updated}")

def test_phone_normalization():
    """Test phone number normalization with examples."""
    print("\n" + "=" * 80)
    print("PHONE NORMALIZATION TEST")
    print("=" * 80)
    
    test_numbers = [
        "+25514852618",
        "0614853618", 
        "25514852618",
        "614853618",
        "0689726060",
        "+255689726060",
        "255689726060",
        "689726060"
    ]
    
    print("Testing phone number normalization:")
    for number in test_numbers:
        normalized = normalize_phone_number(number)
        print(f"  {number:15} -> {normalized}")
    
    # Test the specific example
    print(f"\nSpecific test:")
    print(f"  +25514852618 -> {normalize_phone_number('+25514852618')}")
    print(f"  0614853618    -> {normalize_phone_number('0614853618')}")
    print(f"  Are they equal? {normalize_phone_number('+25514852618') == normalize_phone_number('0614853618')}")

def main():
    """Main function to run phone number analysis."""
    print("Starting phone number analysis...")
    
    # Test normalization
    test_phone_normalization()
    
    # Find duplicates
    duplicates = find_phone_number_duplicates()
    
    # Automatically normalize all phone numbers
    print(f"\nFound {len(duplicates)} duplicate groups.")
    print("Running normalization to ensure consistency...")
    normalize_all_phone_numbers()
    print("\nNormalization complete!")
    
    # Run duplicate check again to verify
    print("\nVerifying normalization...")
    duplicates_after = find_phone_number_duplicates()
    if len(duplicates_after) == 0:
        print("SUCCESS: All phone numbers are now normalized and no duplicates remain!")
    else:
        print(f"WARNING: {len(duplicates_after)} duplicate groups still exist after normalization.")

if __name__ == "__main__":
    main()
