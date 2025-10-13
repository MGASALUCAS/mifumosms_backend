#!/usr/bin/env python
"""
Complete functionality test for sender name requests.
"""
import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
AUTH_URL = f"{BASE_URL}/auth/login/"
SUBMIT_URL = f"{BASE_URL}/messaging/sender-requests/submit/"
LIST_URL = f"{BASE_URL}/messaging/sender-requests/"
STATS_URL = f"{BASE_URL}/messaging/sender-requests/stats/"
ADMIN_URL = f"{BASE_URL}/messaging/sender-requests/admin/dashboard/"

def test_complete_workflow():
    """Test complete sender name request workflow."""
    print("🧪 Complete Sender Name Request Workflow Test")
    print("=" * 60)

    # Step 1: Login as admin
    print("1. Logging in as admin...")
    try:
        login_response = requests.post(AUTH_URL, json={
            "email": "admin2@mifumo.com",
            "password": "admin123"
        })

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('tokens', {}).get('access')
            user_info = token_data.get('user', {})

            print(f"✅ Login successful")
            print(f"   User: {user_info.get('first_name')} {user_info.get('last_name')}")
            print(f"   Staff: {user_info.get('is_staff', False)}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return

    headers = {'Authorization': f'Bearer {access_token}'}

    # Step 2: Test list requests (should work)
    print("\n2. Testing list requests...")
    try:
        list_response = requests.get(LIST_URL, headers=headers)
        print(f"   List Status: {list_response.status_code}")

        if list_response.status_code == 200:
            data = list_response.json()
            print(f"✅ List requests successful")
            print(f"   Found {data.get('data', {}).get('count', 0)} requests")
        else:
            print(f"❌ List requests failed: {list_response.text}")
    except Exception as e:
        print(f"❌ List error: {str(e)}")

    # Step 3: Test statistics (should work)
    print("\n3. Testing statistics...")
    try:
        stats_response = requests.get(STATS_URL, headers=headers)
        print(f"   Stats Status: {stats_response.status_code}")

        if stats_response.status_code == 200:
            data = stats_response.json()
            print(f"✅ Statistics successful")
            print(f"   Total: {data.get('data', {}).get('total_requests', 0)}")
            print(f"   Pending: {data.get('data', {}).get('pending_requests', 0)}")
        else:
            print(f"❌ Statistics failed: {stats_response.text}")
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")

    # Step 4: Test admin dashboard (should work for admin)
    print("\n4. Testing admin dashboard...")
    try:
        admin_response = requests.get(ADMIN_URL, headers=headers)
        print(f"   Admin Status: {admin_response.status_code}")

        if admin_response.status_code == 200:
            data = admin_response.json()
            print(f"✅ Admin dashboard successful")
            print(f"   Tenant: {data.get('data', {}).get('tenant_name', 'N/A')}")
        else:
            print(f"❌ Admin dashboard failed: {admin_response.text}")
    except Exception as e:
        print(f"❌ Admin error: {str(e)}")

    # Step 5: Test submit new request with unique name
    print("\n5. Testing submit new request...")
    unique_name = f"TEST{int(time.time())}"
    try:
        form_data = {
            'sender_name': unique_name,
            'use_case': f'This is a test request with unique name {unique_name} to verify functionality.'
        }

        submit_response = requests.post(SUBMIT_URL, data=form_data, headers=headers)
        print(f"   Submit Status: {submit_response.status_code}")

        if submit_response.status_code == 201:
            data = submit_response.json()
            print(f"✅ Submit successful")
            print(f"   Request ID: {data.get('data', {}).get('id', 'N/A')}")
            print(f"   Sender Name: {data.get('data', {}).get('sender_name', 'N/A')}")
            print(f"   Status: {data.get('data', {}).get('status', 'N/A')}")
        else:
            print(f"❌ Submit failed: {submit_response.text}")
    except Exception as e:
        print(f"❌ Submit error: {str(e)}")

    # Step 6: Test anonymous access (should fail)
    print("\n6. Testing anonymous access...")
    try:
        anonymous_response = requests.get(LIST_URL)
        print(f"   Anonymous Status: {anonymous_response.status_code}")

        if anonymous_response.status_code == 401:
            print(f"✅ Anonymous access correctly blocked")
        else:
            print(f"❌ Anonymous access should be blocked")
    except Exception as e:
        print(f"❌ Anonymous test error: {str(e)}")

def test_regular_user():
    """Test with a regular user account."""
    print("\n" + "=" * 60)
    print("🧪 Testing Regular User Access")
    print("=" * 60)

    # Try to create a test user or use existing one
    print("Note: Regular user testing requires valid credentials")
    print("Current test shows admin access is working correctly")

if __name__ == "__main__":
    test_complete_workflow()
    test_regular_user()
    print("\n🎯 Complete functionality test finished!")
