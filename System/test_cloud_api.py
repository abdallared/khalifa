"""
Test WhatsApp Cloud API Implementation
"""

import os
import sys
import django

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.whatsapp_driver import get_whatsapp_driver
from django.conf import settings

def test_cloud_api_driver():
    """Test CloudAPIDriver implementation"""
    
    print("=" * 60)
    print("Testing WhatsApp Cloud API Driver")
    print("=" * 60)
    
    # Test 1: Driver Configuration
    print("\n1. Testing Driver Configuration...")
    print(f"   WHATSAPP_DRIVER: {settings.WHATSAPP_DRIVER}")
    print(f"   ACCESS_TOKEN: {'✓ Set' if settings.WHATSAPP_CLOUD_ACCESS_TOKEN else '✗ Missing'}")
    print(f"   PHONE_NUMBER_ID: {settings.WHATSAPP_CLOUD_PHONE_NUMBER_ID or '✗ Missing'}")
    print(f"   BUSINESS_ACCOUNT_ID: {settings.WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID or '✗ Missing'}")
    print(f"   WEBHOOK_VERIFY_TOKEN: {'✓ Set' if settings.WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN else '✗ Missing'}")
    
    # Test 2: Get Driver Instance
    print("\n2. Getting Driver Instance...")
    try:
        driver = get_whatsapp_driver()
        print(f"   ✓ Driver created: {driver.provider_name}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Test 3: Check Connection Status
    print("\n3. Testing Connection Status...")
    try:
        status = driver.get_connection_status()
        if status.get('success'):
            print(f"   ✓ Connected: {status.get('connected')}")
            print(f"   Phone: {status.get('phone')}")
            print(f"   Verified Name: {status.get('verified_name')}")
            print(f"   Quality Rating: {status.get('quality_rating')}")
        else:
            print(f"   ✗ Error: {status.get('error')}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
    
    # Test 4: QR Code (should return not available)
    print("\n4. Testing QR Code Method...")
    try:
        qr_result = driver.get_qr_code()
        if not qr_result.get('success'):
            print(f"   ✓ Expected behavior: {qr_result.get('message')}")
        else:
            print(f"   ✗ Unexpected success")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
    
    # Test 5: Send Test Message (Optional - Commented out to avoid sending)
    print("\n5. Testing Send Message (Dry Run)...")
    test_phone = "201234567890"  # Replace with a test number
    test_message = "Test message from Khalifa Pharmacy System"
    print(f"   Would send to: {test_phone}")
    print(f"   Message: {test_message}")
    print(f"   ⚠️  Uncomment code in test_cloud_api.py to actually send")
    
    # Uncomment to actually send:
    # try:
    #     result = driver.send_text_message(test_phone, test_message)
    #     if result.get('success'):
    #         print(f"   ✓ Message sent: {result.get('message_id')}")
    #     else:
    #         print(f"   ✗ Error: {result.get('error')}")
    # except Exception as e:
    #     print(f"   ✗ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    # Summary
    print("\n📋 Configuration Summary:")
    print(f"   Driver Type: {driver.provider_name}")
    print(f"   Base URL: {driver.base_url}")
    print(f"   Phone Number ID: {driver.phone_number_id}")
    print(f"\n🔗 Webhook URL for Meta:")
    print(f"   https://bloodlike-filiberto-collaboratively.ngrok-free.dev/api/whatsapp/cloud/webhook/")
    print(f"\n🔑 Verify Token for Meta:")
    print(f"   {settings.WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN}")


if __name__ == '__main__':
    # Make sure we're using cloud_api driver
    if settings.WHATSAPP_DRIVER != 'cloud_api':
        print(f"\n⚠️  WARNING: Current driver is '{settings.WHATSAPP_DRIVER}'")
        print("   Set WHATSAPP_DRIVER=cloud_api in .env to test Cloud API")
        print("\n   Continue anyway? (y/n): ", end='')
        response = input().strip().lower()
        if response != 'y':
            print("   Test cancelled.")
            sys.exit(0)
    
    test_cloud_api_driver()
