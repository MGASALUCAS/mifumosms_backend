#!/usr/bin/env python3
"""
Test enhanced notification system with real notifications and problem reporting.
"""
import requests
import json

def test_enhanced_notifications():
    """Test the enhanced notification system."""
    print("=" * 80)
    print("TESTING ENHANCED NOTIFICATION SYSTEM")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8001"
    
    # Login as admin
    print("\n1. Login as Admin")
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
        access_token = login_response.get('tokens', {}).get('access')
        if access_token:
            print("SUCCESS: Admin login successful")
        else:
            print("ERROR: No access token")
            return
    else:
        print("ERROR: Login failed")
        print(f"Response: {response.text}")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test system health check
    print("\n2. System Health Check")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/system/health-check/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        health_data = response.json()
        print("SUCCESS: System health check completed")
        health_status = health_data['health_status']
        print(f"System healthy: {health_status['healthy']}")
        print(f"Issues: {len(health_status['issues'])}")
        print(f"Warnings: {len(health_status['warnings'])}")
        
        for issue in health_status['issues']:
            print(f"  ISSUE: {issue['component']} - {issue['error']}")
        
        for warning in health_status['warnings']:
            print(f"  WARNING: {warning['component']} - {warning['error']}")
    else:
        print("ERROR: System health check failed")
        print(f"Response: {response.text}")
    
    # Test problem reporting
    print("\n3. Report System Problem")
    print("-" * 40)
    
    problem_data = {
        'problem_type': 'SMS_SERVICE_DOWN',
        'description': 'SMS service is experiencing downtime. Messages are not being delivered.',
        'priority': 'high',
        'data': {
            'service': 'Beem Africa',
            'error_code': 'SERVICE_UNAVAILABLE',
            'affected_users': 150
        }
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/system/report-problem/",
        json=problem_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        problem_response = response.json()
        print("SUCCESS: Problem reported")
        print(f"Notification ID: {problem_response['notification_id']}")
    else:
        print("ERROR: Problem reporting failed")
        print(f"Response: {response.text}")
    
    # Test get real notifications
    print("\n4. Get Real Notifications")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/real/?limit=10",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        real_data = response.json()
        print("SUCCESS: Real notifications retrieved")
        print(f"Count: {real_data['count']}")
        
        for i, notification in enumerate(real_data['notifications'][:5]):
            print(f"  {i+1}. {notification['title']} - {notification['time_ago']}")
            if notification.get('is_system'):
                print(f"      [SYSTEM] {notification['message']}")
    else:
        print("ERROR: Failed to get real notifications")
        print(f"Response: {response.text}")
    
    # Test recent notifications (enhanced)
    print("\n5. Recent Notifications (Enhanced)")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/recent/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        recent_data = response.json()
        print("SUCCESS: Recent notifications retrieved")
        print(f"Notifications: {len(recent_data['notifications'])}")
        print(f"Unread: {recent_data['unread_count']}")
        
        for i, notification in enumerate(recent_data['notifications'][:5]):
            status = "UNREAD" if notification.get('is_unread') else "READ"
            system = " [SYSTEM]" if notification.get('is_system') else ""
            print(f"  {i+1}. [{status}]{system} {notification['title']} - {notification['time_ago']}")
    else:
        print("ERROR: Failed to get recent notifications")
        print(f"Response: {response.text}")
    
    # Test notification stats
    print("\n6. Notification Statistics")
    print("-" * 40)
    
    response = requests.get(
        f"{base_url}/api/notifications/stats/",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        stats_data = response.json()
        print("SUCCESS: Notification stats retrieved")
        stats = stats_data['data']
        print(f"Total: {stats['total']}")
        print(f"Unread: {stats['unread']}")
        print(f"Recent (7 days): {stats['recent_count']}")
        
        if stats['by_type']:
            print("By Type:")
            for type_name, count in stats['by_type'].items():
                print(f"  {type_name}: {count}")
        
        if stats['by_priority']:
            print("By Priority:")
            for priority, count in stats['by_priority'].items():
                print(f"  {priority}: {count}")
    else:
        print("ERROR: Failed to get notification stats")
        print(f"Response: {response.text}")
    
    # Test cleanup notifications
    print("\n7. Cleanup Old Notifications")
    print("-" * 40)
    
    cleanup_data = {
        'days': 7  # Clean up notifications older than 7 days
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/system/cleanup/",
        json=cleanup_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        cleanup_response = response.json()
        print("SUCCESS: Notification cleanup completed")
        print(f"Deleted: {cleanup_response['deleted_count']} notifications")
    else:
        print("ERROR: Notification cleanup failed")
        print(f"Response: {response.text}")
    
    # Test SMS credit notification
    print("\n8. Test SMS Credit Notification")
    print("-" * 40)
    
    sms_data = {
        'current_credits': 5,  # Very low credits
        'total_credits': 100
    }
    
    response = requests.post(
        f"{base_url}/api/notifications/sms-credit/test/",
        json=sms_data,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        sms_response = response.json()
        print("SUCCESS: SMS credit notification test completed")
        print(f"Percentage: {sms_response['percentage']:.1f}%")
    else:
        print("ERROR: SMS credit notification test failed")
        print(f"Response: {response.text}")
    
    print("\n" + "=" * 80)
    print("ENHANCED NOTIFICATION SYSTEM TEST COMPLETED")
    print("=" * 80)
    
    print("\nNew Features Tested:")
    print("• System health monitoring")
    print("• Automatic problem detection")
    print("• Real notification fetching")
    print("• Problem reporting")
    print("• Notification cleanup")
    print("• Enhanced recent notifications with system notifications")

if __name__ == "__main__":
    test_enhanced_notifications()
