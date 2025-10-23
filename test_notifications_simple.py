#!/usr/bin/env python3
"""
Simple test for notification endpoints.
"""
import requests
import json

def test_notifications():
    """Test notification endpoints."""
    print("=" * 60)
    print("TESTING NOTIFICATION ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8001"
    
    # Login
    print("\n1. Login")
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
        access_token = login_response.get('tokens', {}).get('access')
        if access_token:
            print("SUCCESS: Login successful")
        else:
            print("ERROR: No access token")
            print(f"Response: {login_response}")
            return
    else:
        print("ERROR: Login failed")
        print(f"Response: {response.text}")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test notification stats
    print("\n2. Notification Stats")
    response = requests.get(f"{base_url}/api/notifications/stats/", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print("SUCCESS: Stats retrieved")
        print(f"Total: {stats['data']['total']}")
        print(f"Unread: {stats['data']['unread']}")
    else:
        print("ERROR: Stats failed")
        print(f"Response: {response.text}")
    
    # Test unread count
    print("\n3. Unread Count")
    response = requests.get(f"{base_url}/api/notifications/unread-count/", headers=headers)
    if response.status_code == 200:
        unread_data = response.json()
        print("SUCCESS: Unread count retrieved")
        print(f"Unread: {unread_data['unread_count']}")
    else:
        print("ERROR: Unread count failed")
        print(f"Response: {response.text}")
    
    # Test recent notifications
    print("\n4. Recent Notifications")
    response = requests.get(f"{base_url}/api/notifications/recent/", headers=headers)
    if response.status_code == 200:
        recent_data = response.json()
        print("SUCCESS: Recent notifications retrieved")
        print(f"Count: {len(recent_data['notifications'])}")
        print(f"Unread: {recent_data['unread_count']}")
    else:
        print("ERROR: Recent notifications failed")
        print(f"Response: {response.text}")
    
    # Test create notification
    print("\n5. Create Notification")
    notification_data = {
        'title': 'Test Notification',
        'message': 'This is a test notification',
        'notification_type': 'info',
        'priority': 'medium'
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/",
        json=notification_data,
        headers=headers
    )
    
    if response.status_code == 201:
        notification = response.json()
        print("SUCCESS: Notification created")
        print(f"ID: {notification['id']}")
        notification_id = notification['id']
    else:
        print("ERROR: Create notification failed")
        print(f"Response: {response.text}")
        notification_id = None
    
    # Test SMS credit notification
    print("\n6. SMS Credit Test")
    sms_data = {
        'current_credits': 20,
        'total_credits': 100
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/sms-credit/test/",
        json=sms_data,
        headers=headers
    )
    
    if response.status_code == 200:
        sms_response = response.json()
        print("SUCCESS: SMS credit test completed")
        print(f"Percentage: {sms_response['percentage']:.1f}%")
    else:
        print("ERROR: SMS credit test failed")
        print(f"Response: {response.text}")
    
    # Test notification settings
    print("\n7. Notification Settings")
    response = requests.get(f"{base_url}/api/notifications/settings/", headers=headers)
    if response.status_code == 200:
        settings = response.json()
        print("SUCCESS: Settings retrieved")
        print(f"Email notifications: {settings['email_notifications']}")
        print(f"Warning threshold: {settings['credit_warning_threshold']}%")
    else:
        print("ERROR: Settings failed")
        print(f"Response: {response.text}")
    
    # Test templates
    print("\n8. Notification Templates")
    response = requests.get(f"{base_url}/api/notifications/templates/", headers=headers)
    if response.status_code == 200:
        templates = response.json()
        print("SUCCESS: Templates retrieved")
        print(f"Count: {len(templates['templates'])}")
    else:
        print("ERROR: Templates failed")
        print(f"Response: {response.text}")
    
    print("\n" + "=" * 60)
    print("NOTIFICATION SYSTEM TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_notifications()
