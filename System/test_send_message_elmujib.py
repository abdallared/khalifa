"""
Quick Test - Send Message via Elmujib API
اختبار سريع - إرسال رسالة عبر Elmujib API

This will attempt to send a real message to verify the API is working.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    from conversations.whatsapp_driver import get_whatsapp_driver
    
    print("\n" + "="*60)
    print("  Elmujib API - Message Send Test")
    print("="*60 + "\n")
    
    # Configuration info
    print("Configuration:")
    print(f"  - Auth Method: {settings.ELMUJIB_AUTH_METHOD}")
    print(f"  - Base URL: {settings.ELMUJIB_API_BASE_URL}")
    print(f"  - Vendor UID: {settings.ELMUJIB_VENDOR_UID}")
    print(f"  - Token: {settings.ELMUJIB_BEARER_TOKEN[:20]}...\n")
    
    # Switch to Elmujib driver temporarily
    original_driver = settings.WHATSAPP_DRIVER
    settings.WHATSAPP_DRIVER = 'elmujib_cloud'
    
    # Get driver
    driver = get_whatsapp_driver()
    print(f"Driver: {driver.provider_name}")
    print(f"Auth Method: {driver.auth_method}\n")
    
    # Test phone number (replace with your actual test number)
    print("="*60)
    print("IMPORTANT: To test sending a real message,")
    print("edit this file and replace the phone number below")
    print("with your actual WhatsApp number.")
    print("="*60 + "\n")
    
    test_phone = "201234567890"  # Test number for live send
    
    if test_phone == "YOUR_PHONE_NUMBER_HERE":
        print("[INFO] Phone number not configured for actual send test.")
        print("[INFO] This is just a simulation.\n")
        
        # Show what would be sent
        print("Message Send Simulation:")
        print(f"  To: 201234567890 (example)")
        print(f"  Message: Test from Khalifa Pharmacy System")
        print(f"  URL: {driver.base_url}/{driver.vendor_uid}/contact/send-message")
        
        if driver.auth_method == 'query':
            print(f"  Full URL: {driver.base_url}/{driver.vendor_uid}/contact/send-message?token={driver.bearer_token[:20]}...")
        else:
            print(f"  Header: Authorization: Bearer {driver.bearer_token[:20]}...")
        
        print("\n[INFO] To test with a real number:")
        print("  1. Edit this file: test_send_message_elmujib.py")
        print("  2. Change test_phone = 'YOUR_PHONE_NUMBER_HERE'")
        print("  3. Use format: '201234567890' (with country code)")
        print("  4. Run again: python test_send_message_elmujib.py")
        
    else:
        print(f"Attempting to send message to: {test_phone}\n")
        
        # Try to send message
        result = driver.send_text_message(
            phone=test_phone,
            message="Test message from Khalifa Pharmacy System - Elmujib API Integration"
        )
        
        print("Result:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"  Message ID: {result.get('message_id')}")
            print(f"  Phone: {result.get('phone')}")
            print(f"  Provider: {result.get('provider')}")
            print("\n[SUCCESS] Message sent successfully!")
        else:
            print(f"  Error: {result.get('error')}")
            print("\n[FAILED] Message not sent.")
            print("\nPossible reasons:")
            print("  1. Token is invalid or expired")
            print("  2. Phone number is not registered")
            print("  3. Vendor UID is incorrect")
            print("  4. API endpoint has changed")
    
    # Restore original driver
    settings.WHATSAPP_DRIVER = original_driver
    
    print("\n" + "="*60 + "\n")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
