#!/usr/bin/env python
"""
Test script to verify all authenticated users can submit sender name requests.
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
AUTH_URL = f"{BASE_URL}/auth/login/"
SUBMIT_URL = f"{BASE_URL}/messaging/sender-requests/submit/"

def test_user_submission():
    """Test that any authenticated user can submit a sender name request."""
    print("🧪 Testing User Sender Name Request Submission")
    print("=" * 60)

    # Test with different user types
    test_users = [
        {
            "email": "admin2@mifumo.com",
            "password": "admin123",
            "user_type": "Admin"
        },
        {
            "email": "www.florencesway@gmail.com",
            "password": "password123",
            "user_type": "Regular User"
        },
        {
            "email": "mgasa.lucas@sinnovate.com",
            "password": "password123",
            "user_type": "Regular User"
        }
    ]

    for user_data in test_users:
        print(f"\n🔍 Testing {user_data['user_type']}: {user_data['email']}")
        print("-" * 40)

        # Step 1: Login
        try:
            login_response = requests.post(AUTH_URL, json={
                "email": user_data["email"],
                "password": user_data["password"]
            })

            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get('tokens', {}).get('access')
                user_info = token_data.get('user', {})

                if access_token:
                    print(f"✅ Login successful")
                    print(f"   User: {user_info.get('first_name')} {user_info.get('last_name')}")
                    print(f"   Staff: {user_info.get('is_staff', False)}")
                else:
                    print(f"❌ No access token received")
                    continue
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                continue

        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            continue

        # Step 2: Submit sender name request
        try:
            # Create form data
            form_data = {
                'sender_name': f'TEST{user_data["user_type"].replace(" ", "")[:8].upper()}',
                'use_case': f'This is a test sender name request from {user_data["user_type"]} to verify access permissions.'
            }

            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            submit_response = requests.post(SUBMIT_URL, data=form_data, headers=headers)

            print(f"   Submit Status: {submit_response.status_code}")

            if submit_response.status_code == 201:
                response_data = submit_response.json()
                print(f"✅ Request submitted successfully!")
                print(f"   Request ID: {response_data.get('data', {}).get('id', 'N/A')}")
                print(f"   Sender Name: {response_data.get('data', {}).get('sender_name', 'N/A')}")
                print(f"   Status: {response_data.get('data', {}).get('status', 'N/A')}")
            elif submit_response.status_code == 400:
                response_data = submit_response.json()
                print(f"⚠️  Validation error:")
                print(f"   Message: {response_data.get('message', 'N/A')}")
                if 'errors' in response_data:
                    for field, errors in response_data['errors'].items():
                        print(f"   {field}: {errors}")
            elif submit_response.status_code == 403:
                print(f"❌ Permission denied - User cannot submit requests")
            else:
                print(f"❌ Submit failed: {submit_response.status_code}")
                print(f"   Response: {submit_response.text}")

        except Exception as e:
            print(f"❌ Submit error: {str(e)}")

        print()

def test_anonymous_user():
    """Test that anonymous users cannot submit requests."""
    print("\n🔒 Testing Anonymous User Access")
    print("-" * 40)

    try:
        form_data = {
            'sender_name': 'ANONYMOUS',
            'use_case': 'This should fail for anonymous users'
        }

        submit_response = requests.post(SUBMIT_URL, data=form_data)

        print(f"Anonymous submit status: {submit_response.status_code}")

        if submit_response.status_code == 401:
            print("✅ Anonymous access correctly blocked")
        else:
            print(f"❌ Anonymous access should be blocked but got: {submit_response.status_code}")

    except Exception as e:
        print(f"❌ Anonymous test error: {str(e)}")

def test_duplicate_sender_name():
    """Test that duplicate sender names are handled properly."""
    print("\n🔄 Testing Duplicate Sender Name Handling")
    print("-" * 40)

    # First, login as a user
    try:
        login_response = requests.post(AUTH_URL, json={
            "email": "admin2@mifumo.com",
            "password": "admin123"
        })

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('tokens', {}).get('access')

            if access_token:
                # Submit first request
                form_data = {
                    'sender_name': 'DUPLICATETEST',
                    'use_case': 'First request with this sender name'
                }

                headers = {'Authorization': f'Bearer {access_token}'}

                first_response = requests.post(SUBMIT_URL, data=form_data, headers=headers)
                print(f"First request status: {first_response.status_code}")

                if first_response.status_code == 201:
                    print("✅ First request submitted successfully")

                    # Try to submit duplicate
                    duplicate_response = requests.post(SUBMIT_URL, data=form_data, headers=headers)
                    print(f"Duplicate request status: {duplicate_response.status_code}")

                    if duplicate_response.status_code == 400:
                        print("✅ Duplicate request correctly rejected")
                    else:
                        print("⚠️  Duplicate request handling needs review")
                else:
                    print("❌ First request failed")
            else:
                print("❌ No access token received")
        else:
            print("❌ Login failed")

    except Exception as e:
        print(f"❌ Duplicate test error: {str(e)}")

if __name__ == "__main__":
    test_user_submission()
    test_anonymous_user()
    test_duplicate_sender_name()
    print("\n🎯 Test completed!")
