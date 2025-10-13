#!/usr/bin/env python
"""
Test script for admin dashboard API with correct URL.
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
AUTH_URL = f"{BASE_URL}/auth/login/"
ADMIN_DASHBOARD_URL = f"{BASE_URL}/messaging/sender-requests/admin/dashboard/"

def test_admin_dashboard():
    """Test the admin dashboard API."""
    print("🧪 Testing Admin Dashboard API")
    print("=" * 50)

    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {
        "email": "admin2@mifumo.com",
        "password": "admin123"  # You may need to adjust this
    }

    try:
        login_response = requests.post(AUTH_URL, json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('tokens', {}).get('access')
            if not access_token:
                print("❌ No access token received")
                return
            print("✅ Admin login successful")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return

    # Set up headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 2: Test admin dashboard
    print("\n2. Testing admin dashboard...")
    try:
        dashboard_response = requests.get(ADMIN_DASHBOARD_URL, headers=headers)
        print(f"Status Code: {dashboard_response.status_code}")

        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ Admin dashboard working!")
            print(f"   Total requests: {dashboard_data.get('data', {}).get('stats', {}).get('total_requests', 0)}")
            print(f"   Pending requests: {dashboard_data.get('data', {}).get('stats', {}).get('pending_requests', 0)}")
            print(f"   Approved requests: {dashboard_data.get('data', {}).get('stats', {}).get('approved_requests', 0)}")
            print(f"   Rejected requests: {dashboard_data.get('data', {}).get('stats', {}).get('rejected_requests', 0)}")
            print(f"   Recent requests: {len(dashboard_data.get('data', {}).get('recent_requests', []))}")

            # Show recent requests
            recent_requests = dashboard_data.get('data', {}).get('recent_requests', [])
            if recent_requests:
                print("\n   Recent Requests:")
                for req in recent_requests[:3]:  # Show first 3
                    print(f"     - {req.get('sender_name')} ({req.get('status')})")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.text}")
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")

    # Step 3: Test regular user access
    print("\n3. Testing regular user access...")
    try:
        regular_stats_response = requests.get(f"{BASE_URL}/messaging/sender-requests/stats/", headers=headers)
        print(f"Regular stats - Status Code: {regular_stats_response.status_code}")

        if regular_stats_response.status_code == 200:
            print("✅ Regular user access working!")
        else:
            print(f"❌ Regular user access failed: {regular_stats_response.text}")
    except Exception as e:
        print(f"❌ Regular user access error: {str(e)}")

if __name__ == "__main__":
    test_admin_dashboard()
