#!/usr/bin/env python3
"""
Test notification endpoints and functionality.
"""
import requests
import json
import time

def test_notification_endpoints():
    """Test all notification endpoints."""
    print("=" * 80)
    print("TESTING NOTIFICATION ENDPOINTS")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Login to get authentication token
    print("\n1. Testing Authentication")
    print("-" * 40)
    
    login_data = {
        'email': 'admin@mifumo.com',
        'password': 'admin123'
    }
    
    response = requests.post(
        f"{base_url}/api/auth/login/",
        json=login_data,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    if response.status_code == 200:
        login_response = response.json()
        access_token = login_response.get('access') or login_response.get('access_token')
        if not access_token:
            print("ERROR: No access token in response")
            print(f"Response: {login_response}")
            return
        print("SUCCESS: Authentication successful")
        print(f"User: {login_response.get('user', {}).get('email', 'Unknown')}")
    else:
        print("ERROR: Authentication failed")
        print(f"Response: {response.text}")
        return
    
    # Set up headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test 2: Get notification stats
    print("\n2. Testing Notification Stats")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/stats/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        stats = response.json()
        print("SUCCESS: Notification stats retrieved")
        print(f"Total: {stats['data']['total']}")
        print(f"Unread: {stats['data']['unread']}")
        print(f"Recent (7 days): {stats['data']['recent_count']}")
    else:
        print("ERROR: Failed to get notification stats")
        print(f"Response: {response.text}")
    
    # Test 3: Get unread count
    print("\n3. Testing Unread Count")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/unread-count/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        unread_data = response.json()
        print("✅ Unread count retrieved")
        print(f"Unread notifications: {unread_data['unread_count']}")
    else:
        print("❌ Failed to get unread count")
        print(f"Response: {response.text}")
    
    # Test 4: Get recent notifications
    print("\n4. Testing Recent Notifications")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/recent/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        recent_data = response.json()
        print("✅ Recent notifications retrieved")
        print(f"Notifications count: {len(recent_data['notifications'])}")
        print(f"Unread count: {recent_data['unread_count']}")
        
        # Display first few notifications
        for i, notification in enumerate(recent_data['notifications'][:3]):
            print(f"  {i+1}. {notification['title']} - {notification['time_ago']}")
    else:
        print("❌ Failed to get recent notifications")
        print(f"Response: {response.text}")
    
    # Test 5: Create a test notification
    print("\n5. Testing Create Notification")
    print("-" * 40)
    
    notification_data = {
        'title': 'Test Notification',
        'message': 'This is a test notification created via API',
        'notification_type': 'info',
        'priority': 'medium',
        'action_url': 'https://example.com',
        'action_text': 'View Details'
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/",
        json=notification_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 201:
        notification = response.json()
        print("✅ Test notification created")
        print(f"ID: {notification['id']}")
        print(f"Title: {notification['title']}")
        notification_id = notification['id']
    else:
        print("❌ Failed to create test notification")
        print(f"Response: {response.text}")
        notification_id = None
    
    # Test 6: Mark notification as read
    if notification_id:
        print("\n6. Testing Mark Notification as Read")
        print("-" * 40)
        
        response = requests.post(
            f"{base_url}/api/notifications/{notification_id}/mark-read/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Notification marked as read")
        else:
            print("❌ Failed to mark notification as read")
            print(f"Response: {response.text}")
    
    # Test 7: Test SMS credit notification
    print("\n7. Testing SMS Credit Notification")
    print("-" * 40)
    
    sms_test_data = {
        'current_credits': 15,
        'total_credits': 100
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/sms-credit/test/",
        json=sms_test_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        sms_response = response.json()
        print("✅ SMS credit notification test completed")
        print(f"Current credits: {sms_response['current_credits']}")
        print(f"Total credits: {sms_response['total_credits']}")
        print(f"Percentage: {sms_response['percentage']:.1f}%")
    else:
        print("❌ Failed to test SMS credit notification")
        print(f"Response: {response.text}")
    
    # Test 8: Get notification settings
    print("\n8. Testing Notification Settings")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/settings/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        settings = response.json()
        print("✅ Notification settings retrieved")
        print(f"Email notifications: {settings['email_notifications']}")
        print(f"SMS notifications: {settings['sms_notifications']}")
        print(f"Credit warning threshold: {settings['credit_warning_threshold']}%")
        print(f"Credit critical threshold: {settings['credit_critical_threshold']}%")
    else:
        print("❌ Failed to get notification settings")
        print(f"Response: {response.text}")
    
    # Test 9: Update notification settings
    print("\n9. Testing Update Notification Settings")
    print("-" * 40)
    
    settings_update = {
        'credit_warning_threshold': 30,
        'credit_critical_threshold': 15,
        'email_sms_credit': True,
        'sms_credit_warning': True
    }
    
    response = requests.patch(
        f"{base_url}/api/notifications/settings/",
        json=settings_update,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ Notification settings updated")
        updated_settings = response.json()
        print(f"New warning threshold: {updated_settings['credit_warning_threshold']}%")
        print(f"New critical threshold: {updated_settings['credit_critical_threshold']}%")
    else:
        print("❌ Failed to update notification settings")
        print(f"Response: {response.text}")
    
    # Test 10: Get notification templates
    print("\n10. Testing Notification Templates")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/templates/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        templates = response.json()
        print("✅ Notification templates retrieved")
        print(f"Templates count: {len(templates['templates'])}")
        
        # Display first few templates
        for i, template in enumerate(templates['templates'][:5]):
            print(f"  {i+1}. {template['name']} - {template['notification_type']}")
    else:
        print("❌ Failed to get notification templates")
        print(f"Response: {response.text}")
    
    # Test 11: Create system notification (admin only)
    print("\n11. Testing Create System Notification")
    print("-" * 40)
    
    system_notification_data = {
        'title': 'System Announcement',
        'message': 'This is a system-wide announcement for all users.',
        'notification_type': 'info',
        'priority': 'medium',
        'action_url': 'https://mifumo.com/announcements',
        'action_text': 'Read More'
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/system/create/",
        json=system_notification_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        system_response = response.json()
        print("✅ System notification created")
        print(f"Notifications created: {system_response['notifications_created']}")
    else:
        print("❌ Failed to create system notification")
        print(f"Response: {response.text}")
    
    # Test 12: Final stats check
    print("\n12. Final Stats Check")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/stats/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        final_stats = response.json()
        print("✅ Final notification stats")
        print(f"Total: {final_stats['data']['total']}")
        print(f"Unread: {final_stats['data']['unread']}")
        print(f"Recent (7 days): {final_stats['data']['recent_count']}")
        
        # Show breakdown by type
        if final_stats['data']['by_type']:
            print("\nBy Type:")
            for type_name, count in final_stats['data']['by_type'].items():
                print(f"  {type_name}: {count}")
        
        # Show breakdown by priority
        if final_stats['data']['by_priority']:
            print("\nBy Priority:")
            for priority, count in final_stats['data']['by_priority'].items():
                print(f"  {priority}: {count}")
    else:
        print("❌ Failed to get final stats")
        print(f"Response: {response.text}")
    
    print("\n" + "=" * 80)
    print("NOTIFICATION SYSTEM TEST COMPLETED")
    print("=" * 80)
    
    print("\nAvailable Endpoints:")
    print("• GET /api/notifications/ - List notifications")
    print("• POST /api/notifications/ - Create notification")
    print("• GET /api/notifications/stats/ - Get statistics")
    print("• GET /api/notifications/unread-count/ - Get unread count")
    print("• GET /api/notifications/recent/ - Get recent notifications")
    print("• POST /api/notifications/{id}/mark-read/ - Mark as read")
    print("• POST /api/notifications/mark-all-read/ - Mark all as read")
    print("• GET /api/notifications/settings/ - Get settings")
    print("• PATCH /api/notifications/settings/ - Update settings")
    print("• POST /api/notifications/sms-credit/test/ - Test SMS credit notification")
    print("• POST /api/notifications/system/create/ - Create system notification")
    print("• GET /api/notifications/templates/ - Get templates")

if __name__ == "__main__":
    test_notification_endpoints()
