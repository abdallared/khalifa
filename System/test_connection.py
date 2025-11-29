"""
Test WhatsApp Cloud API Connection
"""

import os
import sys

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.conf import settings
from conversations.whatsapp_driver import CloudAPIDriver

def test_connection():
    """Test connection to WhatsApp Cloud API"""
    
    print("Testing WhatsApp Business Cloud API Connection...")
    print("-" * 60)
    
    config = {
        'access_token': settings.WHATSAPP_CLOUD_ACCESS_TOKEN,
        'phone_number_id': settings.WHATSAPP_CLOUD_PHONE_NUMBER_ID,
        'business_account_id': settings.WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID,
    }
    
    driver = CloudAPIDriver(config)
    
    print("\nGetting connection status...")
    result = driver.get_connection_status()
    
    print("\nResult:")
    print("-" * 60)
    
    if result.get('success'):
        print("Status: CONNECTED")
        print(f"Phone: {result.get('phone')}")
        print(f"Verified Name: {result.get('verified_name')}")
        print(f"Quality Rating: {result.get('quality_rating')}")
        print(f"ID: {result.get('id')}")
        print("\n[OK] Connection test successful!")
    else:
        print("Status: FAILED")
        print(f"Error: {result.get('error')}")
        print("\n[ERROR] Connection test failed!")
        print("\nPossible reasons:")
        print("1. Invalid access token")
        print("2. Invalid phone number ID")
        print("3. Network connection issue")
        print("4. Access token expired")
    
    print("-" * 60)


if __name__ == '__main__':
    test_connection()
