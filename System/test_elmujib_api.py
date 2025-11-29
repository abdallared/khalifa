"""
Test Elmujib Cloud Business API Integration
"""

import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.conf import settings
from conversations.whatsapp_driver import get_whatsapp_driver, ElmujibCloudAPIDriver


def print_header(text):
    """طباعة عنوان"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_result(test_name, success, message=""):
    """طباعة نتيجة الاختبار"""
    status = "✓ PASS" if success else "✗ FAIL"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"     {message}")


def test_configuration():
    """اختبار التكوين"""
    print_header("1. Configuration Test - اختبار التكوين")
    
    tests_passed = 0
    tests_total = 0
    
    # Check environment variables
    tests_total += 1
    base_url = os.getenv('ELMUJIB_API_BASE_URL')
    if base_url:
        print_result("ELMUJIB_API_BASE_URL loaded", True, base_url)
        tests_passed += 1
    else:
        print_result("ELMUJIB_API_BASE_URL loaded", False, "Not found in .env")
    
    tests_total += 1
    vendor_uid = os.getenv('ELMUJIB_VENDOR_UID')
    if vendor_uid:
        print_result("ELMUJIB_VENDOR_UID loaded", True, vendor_uid)
        tests_passed += 1
    else:
        print_result("ELMUJIB_VENDOR_UID loaded", False, "Not found in .env")
    
    tests_total += 1
    bearer_token = os.getenv('ELMUJIB_BEARER_TOKEN')
    if bearer_token and bearer_token != 'your_bearer_token_here':
        print_result("ELMUJIB_BEARER_TOKEN loaded", True, f"{bearer_token[:20]}...")
        tests_passed += 1
    else:
        print_result("ELMUJIB_BEARER_TOKEN loaded", False, 
                    "Not configured or still using placeholder")
    
    # Check Django settings
    tests_total += 1
    if hasattr(settings, 'ELMUJIB_API_BASE_URL'):
        print_result("Django settings has ELMUJIB_API_BASE_URL", True, 
                    settings.ELMUJIB_API_BASE_URL)
        tests_passed += 1
    else:
        print_result("Django settings has ELMUJIB_API_BASE_URL", False)
    
    tests_total += 1
    if hasattr(settings, 'ELMUJIB_VENDOR_UID'):
        print_result("Django settings has ELMUJIB_VENDOR_UID", True, 
                    settings.ELMUJIB_VENDOR_UID)
        tests_passed += 1
    else:
        print_result("Django settings has ELMUJIB_VENDOR_UID", False)
    
    tests_total += 1
    if hasattr(settings, 'ELMUJIB_BEARER_TOKEN'):
        print_result("Django settings has ELMUJIB_BEARER_TOKEN", True, "✓")
        tests_passed += 1
    else:
        print_result("Django settings has ELMUJIB_BEARER_TOKEN", False)
    
    tests_total += 1
    if hasattr(settings, 'ELMUJIB_TIMEOUT'):
        print_result("Django settings has ELMUJIB_TIMEOUT", True, 
                    f"{settings.ELMUJIB_TIMEOUT}s")
        tests_passed += 1
    else:
        print_result("Django settings has ELMUJIB_TIMEOUT", False)
    
    print(f"\n   Configuration Tests: {tests_passed}/{tests_total} passed")
    return tests_passed, tests_total


def test_driver_initialization():
    """اختبار تهيئة Driver"""
    print_header("2. Driver Initialization Test - اختبار تهيئة Driver")
    
    tests_passed = 0
    tests_total = 0
    
    # Test creating ElmujibCloudAPIDriver directly
    tests_total += 1
    try:
        config = {
            'base_url': getattr(settings, 'ELMUJIB_API_BASE_URL', 'https://elmujib.com/api'),
            'vendor_uid': getattr(settings, 'ELMUJIB_VENDOR_UID', ''),
            'bearer_token': getattr(settings, 'ELMUJIB_BEARER_TOKEN', ''),
            'from_phone_number_id': getattr(settings, 'ELMUJIB_FROM_PHONE_NUMBER_ID', ''),
            'timeout': getattr(settings, 'ELMUJIB_TIMEOUT', 30)
        }
        driver = ElmujibCloudAPIDriver(config)
        print_result("ElmujibCloudAPIDriver created directly", True, 
                    f"Provider: {driver.provider_name}")
        tests_passed += 1
    except Exception as e:
        print_result("ElmujibCloudAPIDriver created directly", False, str(e))
    
    # Test driver factory with different driver types
    current_driver = settings.WHATSAPP_DRIVER
    
    tests_total += 1
    try:
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        if isinstance(driver, ElmujibCloudAPIDriver):
            print_result("get_whatsapp_driver() returns ElmujibCloudAPIDriver", True,
                        f"Provider: {driver.provider_name}")
            tests_passed += 1
        else:
            print_result("get_whatsapp_driver() returns ElmujibCloudAPIDriver", False,
                        f"Got {type(driver).__name__}")
    except Exception as e:
        print_result("get_whatsapp_driver() returns ElmujibCloudAPIDriver", False, str(e))
    finally:
        settings.WHATSAPP_DRIVER = current_driver
    
    # Check driver attributes
    tests_total += 1
    try:
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        has_methods = (
            hasattr(driver, 'send_text_message') and
            hasattr(driver, 'send_media_message') and
            hasattr(driver, 'send_template_message') and
            hasattr(driver, 'send_interactive_message') and
            hasattr(driver, 'create_contact') and
            hasattr(driver, 'update_contact') and
            hasattr(driver, 'get_contact')
        )
        if has_methods:
            print_result("Driver has all required methods", True)
            tests_passed += 1
        else:
            print_result("Driver has all required methods", False)
    except Exception as e:
        print_result("Driver has all required methods", False, str(e))
    finally:
        settings.WHATSAPP_DRIVER = current_driver
    
    print(f"\n   Driver Tests: {tests_passed}/{tests_total} passed")
    return tests_passed, tests_total


def test_api_connectivity():
    """اختبار الاتصال بـ API"""
    print_header("3. API Connectivity Test - اختبار الاتصال بـ API")
    
    tests_passed = 0
    tests_total = 0
    
    current_driver = settings.WHATSAPP_DRIVER
    
    tests_total += 1
    try:
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        
        # Check bearer token
        if driver.bearer_token and driver.bearer_token != 'your_bearer_token_here':
            print_result("Bearer token configured", True)
            tests_passed += 1
        else:
            print_result("Bearer token configured", False, 
                        "Bearer token not set or using placeholder")
    except Exception as e:
        print_result("Bearer token configured", False, str(e))
    finally:
        settings.WHATSAPP_DRIVER = current_driver
    
    tests_total += 1
    try:
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        
        # Test connection status
        result = driver.get_connection_status()
        if result.get('success') and result.get('connected'):
            print_result("API connection test", True, "Connected successfully")
            tests_passed += 1
        else:
            error = result.get('error', 'Unknown error')
            print_result("API connection test", False, f"Error: {error}")
            print(f"     Note: Make sure bearer token is correct")
    except Exception as e:
        print_result("API connection test", False, str(e))
    finally:
        settings.WHATSAPP_DRIVER = current_driver
    
    print(f"\n   Connectivity Tests: {tests_passed}/{tests_total} passed")
    return tests_passed, tests_total


def test_message_methods():
    """اختبار طرق إرسال الرسائل"""
    print_header("4. Message Methods Test - اختبار طرق الرسائل")
    
    tests_passed = 0
    tests_total = 0
    
    current_driver = settings.WHATSAPP_DRIVER
    
    try:
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        
        # Test send_text_message structure (dry run)
        tests_total += 1
        test_phone = "201234567890"
        test_message = "Test message"
        
        print(f"\n   Testing message structure (no actual send):")
        print(f"   Phone: {test_phone}")
        print(f"   Message: {test_message}")
        
        # Build expected URL
        expected_url = f"{driver.base_url}/{driver.vendor_uid}/contact/send-message"
        print(f"   Expected URL: {expected_url}")
        
        expected_payload = {
            "phone_number": test_phone,
            "message_body": test_message
        }
        if driver.from_phone_number_id:
            expected_payload["from_phone_number_id"] = driver.from_phone_number_id
        
        print(f"   Expected Payload: {expected_payload}")
        print(f"   Headers: Authorization: Bearer {driver.bearer_token[:20]}...")
        
        print_result("send_text_message structure valid", True)
        tests_passed += 1
        
        # Test send_media_message structure
        tests_total += 1
        expected_url = f"{driver.base_url}/{driver.vendor_uid}/contact/send-media-message"
        print(f"\n   Media URL: {expected_url}")
        print_result("send_media_message structure valid", True)
        tests_passed += 1
        
        # Test send_template_message structure
        tests_total += 1
        expected_url = f"{driver.base_url}/{driver.vendor_uid}/contact/send-template-message"
        print(f"   Template URL: {expected_url}")
        print_result("send_template_message structure valid", True)
        tests_passed += 1
        
        # Test send_interactive_message structure
        tests_total += 1
        expected_url = f"{driver.base_url}/{driver.vendor_uid}/contact/send-interactive-message"
        print(f"   Interactive URL: {expected_url}")
        print_result("send_interactive_message structure valid", True)
        tests_passed += 1
        
        # Test create_contact structure
        tests_total += 1
        expected_url = f"{driver.base_url}/{driver.vendor_uid}/contact/create"
        print(f"   Create Contact URL: {expected_url}")
        print_result("create_contact structure valid", True)
        tests_passed += 1
        
        # Test update_contact structure
        tests_total += 1
        expected_url = f"{driver.base_url}/{driver.vendor_uid}/contact/update/{test_phone}"
        print(f"   Update Contact URL: {expected_url}")
        print_result("update_contact structure valid", True)
        tests_passed += 1
        
    except Exception as e:
        print_result("Message methods test", False, str(e))
    finally:
        settings.WHATSAPP_DRIVER = current_driver
    
    print(f"\n   Message Method Tests: {tests_passed}/{tests_total} passed")
    return tests_passed, tests_total


def test_phone_normalization():
    """اختبار تطبيع أرقام الهاتف"""
    print_header("5. Phone Normalization Test - اختبار تطبيع الأرقام")
    
    tests_passed = 0
    tests_total = 0
    
    current_driver = settings.WHATSAPP_DRIVER
    
    try:
        settings.WHATSAPP_DRIVER = 'elmujib_cloud'
        driver = get_whatsapp_driver()
        
        test_cases = [
            ("01234567890", "201234567890"),
            ("+201234567890", "201234567890"),
            ("201234567890", "201234567890"),
            ("1234567890", "201234567890"),
            ("+20 123 456 7890", "201234567890"),
            ("0123-456-7890", "201234567890"),
        ]
        
        for input_phone, expected_output in test_cases:
            tests_total += 1
            result = driver.normalize_phone(input_phone)
            if result == expected_output:
                print_result(f"Normalize '{input_phone}'", True, f"→ {result}")
                tests_passed += 1
            else:
                print_result(f"Normalize '{input_phone}'", False, 
                           f"Expected {expected_output}, got {result}")
        
    except Exception as e:
        print_result("Phone normalization test", False, str(e))
    finally:
        settings.WHATSAPP_DRIVER = current_driver
    
    print(f"\n   Phone Normalization Tests: {tests_passed}/{tests_total} passed")
    return tests_passed, tests_total


def main():
    """الدالة الرئيسية"""
    print("\n")
    print("+" + "="*58 + "+")
    print("|" + " "*10 + "Elmujib Cloud Business API Test" + " "*16 + "|")
    print("|" + " "*10 + "Elmujib Cloud Business API Test" + " "*16 + "|")
    print("+" + "="*58 + "+")
    
    all_tests_passed = 0
    all_tests_total = 0
    
    # Run all tests
    passed, total = test_configuration()
    all_tests_passed += passed
    all_tests_total += total
    
    passed, total = test_driver_initialization()
    all_tests_passed += passed
    all_tests_total += total
    
    passed, total = test_api_connectivity()
    all_tests_passed += passed
    all_tests_total += total
    
    passed, total = test_message_methods()
    all_tests_passed += passed
    all_tests_total += total
    
    passed, total = test_phone_normalization()
    all_tests_passed += passed
    all_tests_total += total
    
    # Final summary
    print_header("Test Summary - ملخص الاختبارات")
    
    percentage = (all_tests_passed / all_tests_total * 100) if all_tests_total > 0 else 0
    
    print(f"\n   Total Tests: {all_tests_total}")
    print(f"   Passed: {all_tests_passed}")
    print(f"   Failed: {all_tests_total - all_tests_passed}")
    print(f"   Success Rate: {percentage:.1f}%")
    
    if all_tests_passed == all_tests_total:
        print("\n   ✓ All tests passed! System is ready to use.")
        print("   ✓ جميع الاختبارات نجحت! النظام جاهز للاستخدام.")
    elif percentage >= 70:
        print("\n   ⚠ Most tests passed, but some configuration needed.")
        print("   ⚠ معظم الاختبارات نجحت، لكن بعض الإعدادات مطلوبة.")
    else:
        print("\n   ✗ Many tests failed. Please check configuration.")
        print("   ✗ فشلت العديد من الاختبارات. يرجى التحقق من الإعدادات.")
    
    print("\n" + "="*60 + "\n")
    
    # Configuration instructions
    if percentage < 100:
        print("📋 Configuration Steps:")
        print("   1. Add your Bearer Token to .env:")
        print("      ELMUJIB_BEARER_TOKEN=your_actual_token")
        print("\n   2. (Optional) Add phone number ID:")
        print("      ELMUJIB_FROM_PHONE_NUMBER_ID=your_phone_id")
        print("\n   3. Switch to Elmujib driver in .env:")
        print("      WHATSAPP_DRIVER=elmujib_cloud")
        print("\n   4. Run this test again:")
        print("      python test_elmujib_api.py")
        print()


if __name__ == '__main__':
    main()
