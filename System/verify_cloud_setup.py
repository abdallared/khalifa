"""
Verify WhatsApp Cloud API Setup
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

def verify_setup():
    """Verify Cloud API setup"""
    
    print("=" * 70)
    print("WhatsApp Business Cloud API Setup Verification")
    print("=" * 70)
    
    # Check credentials
    print("\n1. Checking Credentials...")
    
    checks = {
        'Access Token': settings.WHATSAPP_CLOUD_ACCESS_TOKEN,
        'Phone Number ID': settings.WHATSAPP_CLOUD_PHONE_NUMBER_ID,
        'Business Account ID': settings.WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID,
        'Webhook Verify Token': settings.WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN,
    }
    
    all_set = True
    for name, value in checks.items():
        if value:
            print(f"   [OK] {name}: {'*' * 20}{value[-4:]}")
        else:
            print(f"   [MISSING] {name}")
            all_set = False
    
    # Check driver implementation
    print("\n2. Checking Driver Implementation...")
    
    try:
        config = {
            'access_token': settings.WHATSAPP_CLOUD_ACCESS_TOKEN,
            'phone_number_id': settings.WHATSAPP_CLOUD_PHONE_NUMBER_ID,
            'business_account_id': settings.WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID,
        }
        
        driver = CloudAPIDriver(config)
        print(f"   [OK] Driver initialized: {driver.provider_name}")
        print(f"   [OK] Base URL: {driver.base_url}")
        print(f"   [OK] API Version: {driver.api_version}")
        
        # Check methods exist
        methods = ['send_text_message', 'send_media_message', 'get_connection_status', 'get_qr_code']
        for method in methods:
            if hasattr(driver, method):
                print(f"   [OK] Method exists: {method}")
            else:
                print(f"   [ERROR] Method missing: {method}")
                all_set = False
                
    except Exception as e:
        print(f"   [ERROR] Failed to initialize driver: {e}")
        all_set = False
    
    # Check webhook handler
    print("\n3. Checking Webhook Handler...")
    
    try:
        from conversations.views_whatsapp import whatsapp_cloud_webhook
        print(f"   [OK] Webhook handler exists: whatsapp_cloud_webhook")
    except ImportError as e:
        print(f"   [ERROR] Webhook handler missing: {e}")
        all_set = False
    
    # Check URL configuration
    print("\n4. Checking URL Configuration...")
    
    try:
        from django.urls import resolve
        from django.urls.exceptions import Resolver404
        
        try:
            resolver = resolve('/api/whatsapp/cloud/webhook/')
            print(f"   [OK] Cloud webhook URL configured: {resolver.view_name}")
        except Resolver404:
            print(f"   [ERROR] Cloud webhook URL not found")
            all_set = False
            
    except Exception as e:
        print(f"   [ERROR] URL check failed: {e}")
        all_set = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_set:
        print("Status: ALL CHECKS PASSED!")
        print("=" * 70)
        
        print("\nNext Steps:")
        print("1. Configure webhook in Meta Developer Dashboard:")
        print("   - URL: https://bloodlike-filiberto-collaboratively.ngrok-free.dev/api/whatsapp/cloud/webhook/")
        print(f"   - Verify Token: {settings.WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN}")
        print("   - Subscribe to: messages")
        print("\n2. Update .env to switch driver:")
        print("   WHATSAPP_DRIVER=cloud_api")
        print("\n3. Restart Django server")
        print("\n4. Test by sending a message from WhatsApp")
        
    else:
        print("Status: SETUP INCOMPLETE - Please fix the issues above")
        print("=" * 70)
    
    return all_set


if __name__ == '__main__':
    verify_setup()
