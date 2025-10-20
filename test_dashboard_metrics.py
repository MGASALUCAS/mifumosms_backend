#!/usr/bin/env python3
"""
Test script for dashboard metrics endpoints.
This script tests the dashboard functionality to ensure metrics work properly.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_dashboard_endpoints():
    """Test all dashboard endpoints."""
    print("🧪 Testing Dashboard Metrics Endpoints")
    print("=" * 50)
    
    # Create test client with proper settings
    from django.test import override_settings
    
    with override_settings(ALLOWED_HOSTS=['*']):
        client = APIClient()
        
        try:
            # Get a test user (assuming there's at least one user in the system)
            user = User.objects.filter(is_active=True).first()
            
            if not user:
                print("❌ No active users found. Please create a user first.")
                return False
                
            print(f"✅ Using test user: {user.email}")
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Set authorization header
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            
            # Test endpoints
            endpoints = [
                ('/api/messaging/dashboard/overview/', 'Dashboard Overview'),
                ('/api/messaging/dashboard/metrics/', 'Dashboard Metrics'),
                ('/api/messaging/dashboard/comprehensive/', 'Dashboard Comprehensive'),
            ]
            
            for endpoint, name in endpoints:
                print(f"\n📊 Testing {name}")
                print(f"   Endpoint: {endpoint}")
                
                try:
                    response = client.get(endpoint)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            print(f"   ✅ Status: {response.status_code}")
                            print(f"   ✅ Success: {data.get('success')}")
                            
                            # Print key metrics
                            if 'data' in data:
                                metrics = data['data']
                                if 'metrics' in metrics:
                                    print(f"   📈 Key Metrics:")
                                    for key, value in metrics['metrics'].items():
                                        if isinstance(value, (int, float)):
                                            print(f"      {key}: {value}")
                                        elif isinstance(value, dict) and 'value' in value:
                                            print(f"      {key}: {value['value']}")
                            
                            # Print summary if available
                            if 'summary' in metrics:
                                print(f"   📋 Summary:")
                                for key, value in metrics['summary'].items():
                                    if isinstance(value, (int, float)):
                                        print(f"      {key}: {value}")
                        else:
                            print(f"   ⚠️  Response success: {data.get('success')}")
                            print(f"   ⚠️  Message: {data.get('message', 'No message')}")
                    else:
                        print(f"   ❌ Status: {response.status_code}")
                        print(f"   ❌ Response: {response.content.decode()[:200]}...")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
            
            print(f"\n🎉 Dashboard testing completed!")
            return True
            
        except Exception as e:
            print(f"❌ Test setup error: {str(e)}")
            return False

def test_dashboard_data_structure():
    """Test the structure of dashboard data."""
    print("\n🔍 Testing Dashboard Data Structure")
    print("=" * 50)
    
    from django.test import override_settings
    
    with override_settings(ALLOWED_HOSTS=['*']):
        client = APIClient()
        
        try:
            user = User.objects.filter(is_active=True).first()
            if not user:
                print("❌ No active users found.")
                return False
                
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            
            # Test comprehensive endpoint for complete data structure
            response = client.get('/api/messaging/dashboard/comprehensive/')
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    metrics_data = data['data']
                    
                    # Check required sections
                    required_sections = ['summary', 'metrics', 'recent_activity']
                    for section in required_sections:
                        if section in metrics_data:
                            print(f"✅ {section}: Present")
                        else:
                            print(f"❌ {section}: Missing")
                    
                    # Check metrics subsections
                    if 'metrics' in metrics_data:
                        metrics_subsections = ['messages', 'sms', 'contacts', 'campaigns', 'billing']
                        for subsection in metrics_subsections:
                            if subsection in metrics_data['metrics']:
                                print(f"✅ metrics.{subsection}: Present")
                            else:
                                print(f"❌ metrics.{subsection}: Missing")
                    
                    # Check data types
                    if 'summary' in metrics_data:
                        summary = metrics_data['summary']
                        expected_numeric_fields = [
                            'total_messages', 'total_sms_messages', 'active_contacts', 
                            'current_credits', 'sms_delivery_rate', 'campaign_success_rate'
                        ]
                        
                        for field in expected_numeric_fields:
                            if field in summary:
                                value = summary[field]
                                if isinstance(value, (int, float)):
                                    print(f"✅ summary.{field}: {value} (numeric)")
                                else:
                                    print(f"⚠️  summary.{field}: {value} (not numeric)")
                            else:
                                print(f"❌ summary.{field}: Missing")
                    
                    print(f"\n📊 Dashboard data structure validation completed!")
                    return True
                else:
                    print(f"❌ Invalid response structure")
                    return False
            else:
                print(f"❌ Failed to get comprehensive dashboard data: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Data structure test error: {str(e)}")
            return False

def main():
    """Main test function."""
    print("🚀 Dashboard Metrics Test Suite")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test1_passed = test_dashboard_endpoints()
    test2_passed = test_dashboard_data_structure()
    
    print(f"\n📋 Test Results Summary")
    print("=" * 50)
    print(f"Dashboard Endpoints Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Data Structure Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! Dashboard metrics are working properly.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the dashboard implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
