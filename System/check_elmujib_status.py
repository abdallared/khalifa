"""
Quick Status Check for Elmujib Integration
فحص سريع لحالة تكامل Elmujib
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    from conversations.whatsapp_driver import get_whatsapp_driver, ElmujibCloudAPIDriver
    
    print("\n" + "="*60)
    print("  Elmujib Cloud Business API - Status Check")
    print("="*60 + "\n")
    
    # Current driver
    current_driver = settings.WHATSAPP_DRIVER
    print(f"Current Driver: {current_driver}")
    
    # Configuration status
    print("\nConfiguration:")
    print(f"  - API Base URL: {settings.ELMUJIB_API_BASE_URL}")
    print(f"  - Vendor UID: {settings.ELMUJIB_VENDOR_UID}")
    
    bearer_token = settings.ELMUJIB_BEARER_TOKEN
    if bearer_token and bearer_token != 'your_bearer_token_here':
        print(f"  - Bearer Token: {bearer_token[:20]}... (configured)")
    else:
        print(f"  - Bearer Token: NOT CONFIGURED")
    
    if settings.ELMUJIB_FROM_PHONE_NUMBER_ID:
        print(f"  - Phone Number ID: {settings.ELMUJIB_FROM_PHONE_NUMBER_ID}")
    else:
        print(f"  - Phone Number ID: (optional, not set)")
    
    # Try to create driver
    print("\nDriver Test:")
    try:
        original = settings.WHATSAPP_DRIVER
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        settings.WHATSAPP_DRIVER = original
        
        if isinstance(driver, ElmujibCloudAPIDriver):
            print(f"  [OK] ElmujibCloudAPIDriver initialized successfully")
            print(f"  [OK] Provider name: {driver.provider_name}")
            
            # Check methods
            methods = [
                'send_text_message',
                'send_media_message', 
                'send_template_message',
                'send_interactive_message',
                'create_contact',
                'update_contact',
                'get_contact'
            ]
            
            all_present = all(hasattr(driver, m) for m in methods)
            if all_present:
                print(f"  [OK] All required methods present ({len(methods)} methods)")
            else:
                print(f"  [FAIL] Some methods missing")
        else:
            print(f"  [FAIL] Wrong driver type: {type(driver).__name__}")
    except Exception as e:
        print(f"  [FAIL] Driver initialization failed: {e}")
    
    # Next steps
    print("\n" + "="*60)
    if bearer_token and bearer_token != 'your_bearer_token_here':
        print("Status: [OK] READY TO USE")
        print("\nTo activate Elmujib:")
        print("  1. Set in .env: WHATSAPP_DRIVER=elmujib_cloud")
        print("  2. Restart Django server")
        print("  3. System will use Elmujib automatically")
    else:
        print("Status: [PENDING] CONFIGURATION NEEDED")
        print("\nNext steps:")
        print("  1. Add bearer token to .env:")
        print("     ELMUJIB_BEARER_TOKEN=your_actual_token")
        print("  2. Run test: python test_elmujib_api.py")
        print("  3. Set: WHATSAPP_DRIVER=elmujib_cloud")
    
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
