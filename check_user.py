# #!/usr/bin/env python
# """
# Script to check user status and tenant assignment.
# """

# import os
# import sys
# import django

# # Add the project directory to Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # Set up Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
# django.setup()

# from django.contrib.auth import get_user_model
# from tenants.models import Tenant

# def check_user_status():
#     """Check the status of the admin user."""
#     User = get_user_model()
    
#     try:
#         # Get the admin user
#         user = User.objects.get(email='admin@mifumo.com')
        
#         print("👤 User Status:")
#         print(f"   Email: {user.email}")
#         print(f"   Name: {user.get_full_name()}")
#         print(f"   Is Superuser: {user.is_superuser}")
#         print(f"   Is Staff: {user.is_staff}")
#         print(f"   Is Active: {user.is_active}")
#         print(f"   Tenant: {user.tenant if hasattr(user, 'tenant') else 'No tenant field'}")
        
#         # Check tenants
#         print("\n🏢 Available Tenants:")
#         tenants = Tenant.objects.all()
#         if tenants.exists():
#             for tenant in tenants:
#                 print(f"   - {tenant.name} ({tenant.subdomain})")
#         else:
#             print("   No tenants found")
        
#         return True
        
#     except User.DoesNotExist:
#         print("❌ Admin user not found!")
#         return False
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return False

# if __name__ == '__main__':
#     check_user_status()


import requests
from requests.auth import HTTPBasicAuth

url = "https://apisms.beem.africa/v1/send"

data = {
    "source_addr": "Taarifa-SMS",
    "encoding": 0,
    "message": "SMS Test from Python API",
    "recipients": [
        {
            "recipient_id": 1,
            "dest_addr": "255689726060"
        }
    ]
}

username = "62f8c3a2cb510335"
password = "YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ=="

response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print("SMS sent successfully!")
else:
    print("SMS sending failed. Status code:", response.status_code)
    print("Response:", response.text)
