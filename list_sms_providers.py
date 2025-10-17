#!/usr/bin/env python3
"""
List All SMS Providers
This script lists all SMS providers and their configurations
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID
from django.conf import settings
import requests
import base64
import json

def list_configured_providers():
    """List all SMS providers configured in the system"""
    print("📱 SMS Providers in Database")
    print("=" * 50)
    
    # Get all tenants
    tenants = Tenant.objects.all()
    
    if not tenants.exists():
        print("❌ No tenants found!")
        return
    
    for tenant in tenants:
        print(f"\n🏢 Tenant: {tenant.name} ({tenant.subdomain})")
        print("-" * 40)
        
        # Get SMS providers for this tenant
        providers = SMSProvider.objects.filter(tenant=tenant)
        
        if not providers.exists():
            print("   ❌ No SMS providers configured")
            continue
        
        for provider in providers:
            print(f"   📡 Provider: {provider.name}")
            print(f"      Type: {provider.provider_type}")
            print(f"      Status: {'✅ Active' if provider.is_active else '❌ Inactive'}")
            print(f"      Default: {'✅ Yes' if provider.is_default else '❌ No'}")
            print(f"      API URL: {provider.api_url}")
            print(f"      Cost: {provider.cost_per_sms} {provider.currency}")
            print(f"      Created: {provider.created_at}")
            
            # Get sender IDs for this provider
            sender_ids = SMSSenderID.objects.filter(provider=provider)
            if sender_ids.exists():
                print(f"      📞 Sender IDs:")
                for sender in sender_ids:
                    status_icon = "✅" if sender.status == "active" else "❌"
                    print(f"         {status_icon} {sender.sender_id} ({sender.status})")
            else:
                print(f"      📞 No sender IDs configured")
            print()

def list_settings_providers():
    """List SMS providers from Django settings"""
    print("⚙️  SMS Providers in Settings")
    print("=" * 50)
    
    # Beem Africa
    print("📱 Beem Africa SMS:")
    print(f"   API Key: {getattr(settings, 'BEEM_API_KEY', 'Not set')}")
    print(f"   Secret Key: {getattr(settings, 'BEEM_SECRET_KEY', 'Not set')[:20]}...")
    print(f"   Default Sender ID: {getattr(settings, 'BEEM_DEFAULT_SENDER_ID', 'Not set')}")
    print(f"   Send URL: {getattr(settings, 'BEEM_SEND_URL', 'Not set')}")
    print(f"   Balance URL: {getattr(settings, 'BEEM_BALANCE_URL', 'Not set')}")
    print(f"   Sender URL: {getattr(settings, 'BEEM_SENDER_URL', 'Not set')}")
    
    # Twilio
    print("\n📱 Twilio SMS:")
    print(f"   Account SID: {getattr(settings, 'TWILIO_ACCOUNT_SID', 'Not set')}")
    print(f"   Auth Token: {getattr(settings, 'TWILIO_AUTH_TOKEN', 'Not set')[:20]}...")
    print(f"   Phone Number: {getattr(settings, 'TWILIO_PHONE_NUMBER', 'Not set')}")
    
    # Africa's Talking (if configured)
    print("\n📱 Africa's Talking SMS:")
    print(f"   API Key: {getattr(settings, 'AFRICASTALKING_API_KEY', 'Not set')}")
    print(f"   Username: {getattr(settings, 'AFRICASTALKING_USERNAME', 'Not set')}")
    print(f"   Sender ID: {getattr(settings, 'AFRICASTALKING_SENDER_ID', 'Not set')}")

def test_provider_connections():
    """Test connections to all configured providers"""
    print("\n🔗 Testing Provider Connections")
    print("=" * 50)
    
    # Test Beem Africa
    print("📱 Testing Beem Africa...")
    try:
        beem_api_key = getattr(settings, 'BEEM_API_KEY', '')
        beem_secret = getattr(settings, 'BEEM_SECRET_KEY', '')
        balance_url = getattr(settings, 'BEEM_BALANCE_URL', '')
        
        if beem_api_key and beem_secret:
            # Test balance check
            auth_string = f"{beem_api_key}:{beem_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {'Authorization': f'Basic {auth_b64}'}
            response = requests.get(balance_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                balance = data.get('data', {}).get('credit_balance', 'Unknown')
                print(f"   ✅ Connection successful - Balance: {balance}")
            else:
                print(f"   ❌ Connection failed - Status: {response.status_code}")
        else:
            print("   ❌ Credentials not configured")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test Twilio
    print("\n📱 Testing Twilio...")
    try:
        twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        
        if twilio_sid and twilio_token:
            # Test account info
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            account = client.api.accounts(twilio_sid).fetch()
            print(f"   ✅ Connection successful - Account: {account.friendly_name}")
        else:
            print("   ❌ Credentials not configured")
    except ImportError:
        print("   ❌ Twilio library not installed")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

def list_available_sender_ids():
    """List available sender IDs from Beem"""
    print("\n📞 Available Sender IDs from Beem")
    print("=" * 50)
    
    try:
        beem_api_key = getattr(settings, 'BEEM_API_KEY', '')
        beem_secret = getattr(settings, 'BEEM_SECRET_KEY', '')
        sender_url = getattr(settings, 'BEEM_SENDER_URL', '')
        
        if beem_api_key and beem_secret and sender_url:
            auth_string = f"{beem_api_key}:{beem_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {'Authorization': f'Basic {auth_b64}'}
            response = requests.get(sender_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                senders = data.get('data', [])
                
                if senders:
                    print(f"   Found {len(senders)} sender IDs:")
                    for sender in senders:
                        status_icon = "✅" if sender.get('status') == 'active' else "❌"
                        print(f"   {status_icon} {sender.get('senderid', 'Unknown')} - {sender.get('status', 'Unknown')}")
                        print(f"      Sample: {sender.get('sample_content', 'No sample')}")
                else:
                    print("   ❌ No sender IDs found")
            else:
                print(f"   ❌ Failed to fetch sender IDs - Status: {response.status_code}")
        else:
            print("   ❌ Beem credentials not configured")
    except Exception as e:
        print(f"   ❌ Error fetching sender IDs: {e}")

def main():
    print("📱 SMS Providers Overview")
    print("=" * 60)
    
    # List providers in database
    list_configured_providers()
    
    # List providers in settings
    list_settings_providers()
    
    # Test connections
    test_provider_connections()
    
    # List available sender IDs
    list_available_sender_ids()
    
    print("\n💡 Summary:")
    print("- Check which providers are active in your database")
    print("- Verify credentials are correctly configured")
    print("- Test connections to ensure they're working")
    print("- Use registered sender IDs for SMS sending")

if __name__ == "__main__":
    main()
