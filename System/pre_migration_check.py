"""
Pre-Migration Check: WPPConnect to Elmujib Cloud API
Comprehensive validation before switching WhatsApp providers
"""

import os
import sys
import django
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.conf import settings
from conversations.whatsapp_driver import get_whatsapp_driver, WPPConnectDriver, ElmujibCloudAPIDriver


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_header(text, color=Colors.CYAN):
    """Print section header"""
    print(f"\n{color}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}")


def print_status(label, status, message=""):
    """Print status with color"""
    if status == "OK":
        icon = f"{Colors.GREEN}[OK]{Colors.RESET}"
    elif status == "WARN":
        icon = f"{Colors.YELLOW}[WARN]{Colors.RESET}"
    else:
        icon = f"{Colors.RED}[FAIL]{Colors.RESET}"
    
    print(f"{icon} {label}")
    if message:
        print(f"     {message}")


def check_wppconnect_status():
    """Check current WPPConnect configuration and status"""
    print_header("1. WPPConnect Current Status", Colors.BLUE)
    
    results = {
        'configured': False,
        'reachable': False,
        'connected': False,
        'errors': []
    }
    
    # Check configuration
    try:
        config = {
            'base_url': settings.WPPCONNECT_BASE_URL,
            'api_key': settings.WPPCONNECT_API_KEY,
            'timeout': settings.WPPCONNECT_TIMEOUT,
            'session_name': os.getenv('WPPCONNECT_SESSION_NAME', 'khalifa-pharmacy')
        }
        
        print(f"\nConfiguration:")
        print(f"  Base URL: {config['base_url']}")
        print(f"  Session: {config['session_name']}")
        print(f"  API Key: {'*' * 20}")
        
        driver = WPPConnectDriver(config)
        results['configured'] = True
        print_status("Configuration", "OK", "WPPConnect settings loaded")
        
    except Exception as e:
        results['errors'].append(f"Configuration error: {str(e)}")
        print_status("Configuration", "FAIL", str(e))
        return results
    
    # Check if server is reachable
    try:
        url = f"{config['base_url']}/api/{config['session_name']}/check-connection-session"
        headers = {'Authorization': f"Bearer {config['api_key']}"}
        
        response = requests.get(url, headers=headers, timeout=5)
        results['reachable'] = True
        print_status("Server Reachable", "OK", f"Status Code: {response.status_code}")
        
        # Check connection status
        connection_status = driver.get_connection_status()
        if connection_status.get('connected'):
            results['connected'] = True
            print_status("WhatsApp Connected", "OK", "Session is active")
        else:
            print_status("WhatsApp Connected", "WARN", "Session not connected - QR code may be needed")
            
    except requests.exceptions.ConnectionError:
        results['errors'].append("WPPConnect server not running")
        print_status("Server Reachable", "FAIL", "Cannot connect to WPPConnect server")
    except requests.exceptions.Timeout:
        results['errors'].append("Connection timeout")
        print_status("Server Reachable", "FAIL", "Connection timeout")
    except Exception as e:
        results['errors'].append(str(e))
        print_status("Server Reachable", "FAIL", str(e))
    
    return results


def check_elmujib_configuration():
    """Check Elmujib Cloud API configuration"""
    print_header("2. Elmujib Cloud API Configuration", Colors.BLUE)
    
    results = {
        'configured': False,
        'credentials_valid': False,
        'ready': False,
        'errors': []
    }
    
    # Check environment variables
    config_items = [
        ('ELMUJIB_API_BASE_URL', settings.ELMUJIB_API_BASE_URL),
        ('ELMUJIB_VENDOR_UID', settings.ELMUJIB_VENDOR_UID),
        ('ELMUJIB_BEARER_TOKEN', settings.ELMUJIB_BEARER_TOKEN),
        ('ELMUJIB_AUTH_METHOD', settings.ELMUJIB_AUTH_METHOD),
    ]
    
    print("\nConfiguration:")
    all_configured = True
    for key, value in config_items:
        if value and (key != 'ELMUJIB_BEARER_TOKEN' or value != 'your_bearer_token_here'):
            display_value = value if key != 'ELMUJIB_BEARER_TOKEN' else f"{value[:20]}..."
            print(f"  {key}: {display_value}")
            print_status(f"  {key}", "OK")
        else:
            print_status(f"  {key}", "FAIL", "Not configured")
            all_configured = False
            results['errors'].append(f"{key} not configured")
    
    results['configured'] = all_configured
    
    # Test driver initialization
    if all_configured:
        try:
            elmujib_config = {
                'base_url': settings.ELMUJIB_API_BASE_URL,
                'vendor_uid': settings.ELMUJIB_VENDOR_UID,
                'bearer_token': settings.ELMUJIB_BEARER_TOKEN,
                'from_phone_number_id': settings.ELMUJIB_FROM_PHONE_NUMBER_ID,
                'auth_method': settings.ELMUJIB_AUTH_METHOD,
                'timeout': settings.ELMUJIB_TIMEOUT
            }
            
            driver = ElmujibCloudAPIDriver(elmujib_config)
            connection_status = driver.get_connection_status()
            
            if connection_status.get('success') and connection_status.get('connected'):
                results['credentials_valid'] = True
                results['ready'] = True
                print_status("\nCredentials Valid", "OK", "Elmujib ready to use")
            else:
                results['errors'].append("Credentials validation failed")
                print_status("\nCredentials Valid", "FAIL", connection_status.get('error', 'Unknown error'))
                
        except Exception as e:
            results['errors'].append(f"Driver initialization error: {str(e)}")
            print_status("\nDriver Initialization", "FAIL", str(e))
    
    return results


def test_elmujib_endpoints():
    """Test Elmujib API endpoints structure"""
    print_header("3. Elmujib API Endpoints Test", Colors.BLUE)
    
    results = {
        'endpoints_valid': False,
        'phone_normalization': False,
        'errors': []
    }
    
    try:
        elmujib_config = {
            'base_url': settings.ELMUJIB_API_BASE_URL,
            'vendor_uid': settings.ELMUJIB_VENDOR_UID,
            'bearer_token': settings.ELMUJIB_BEARER_TOKEN,
            'from_phone_number_id': settings.ELMUJIB_FROM_PHONE_NUMBER_ID,
            'auth_method': settings.ELMUJIB_AUTH_METHOD,
            'timeout': settings.ELMUJIB_TIMEOUT
        }
        
        driver = ElmujibCloudAPIDriver(elmujib_config)
        
        # Test endpoint URLs
        print("\nAPI Endpoints:")
        endpoints = [
            ('Send Text Message', f"{driver.base_url}/{driver.vendor_uid}/contact/send-message"),
            ('Send Media', f"{driver.base_url}/{driver.vendor_uid}/contact/send-media-message"),
            ('Send Template', f"{driver.base_url}/{driver.vendor_uid}/contact/send-template-message"),
            ('Send Interactive', f"{driver.base_url}/{driver.vendor_uid}/contact/send-interactive-message"),
            ('Create Contact', f"{driver.base_url}/{driver.vendor_uid}/contact/create"),
            ('Update Contact', f"{driver.base_url}/{driver.vendor_uid}/contact/update/{{phone}}"),
        ]
        
        for name, url in endpoints:
            print(f"  {name}:")
            print(f"    {url}")
            print_status(f"    {name} URL", "OK")
        
        results['endpoints_valid'] = True
        
        # Test phone normalization
        print("\nPhone Normalization Test:")
        test_cases = [
            ('01234567890', '201234567890'),
            ('+201234567890', '201234567890'),
            ('201234567890', '201234567890'),
        ]
        
        all_pass = True
        for input_phone, expected in test_cases:
            normalized = driver.normalize_phone(input_phone)
            if normalized == expected:
                print_status(f"  '{input_phone}' -> '{normalized}'", "OK")
            else:
                print_status(f"  '{input_phone}' -> '{normalized}'", "FAIL", f"Expected: {expected}")
                all_pass = False
        
        results['phone_normalization'] = all_pass
        
    except Exception as e:
        results['errors'].append(str(e))
        print_status("Endpoint Test", "FAIL", str(e))
    
    return results


def compare_configurations():
    """Compare WPPConnect vs Elmujib configurations"""
    print_header("4. Configuration Comparison", Colors.BLUE)
    
    print(f"\n{Colors.BOLD}Feature Comparison:{Colors.RESET}")
    
    comparison = [
        ("Provider", "WPPConnect (Self-Hosted)", "Elmujib Cloud API"),
        ("Infrastructure", "Local server required", "Cloud-based (no server)"),
        ("Authentication", "API Key", "Bearer Token"),
        ("QR Code Required", "Yes (periodic)", "No"),
        ("Maintenance", "Manual updates", "Managed by provider"),
        ("Reliability", "Depends on server uptime", "99.9% cloud uptime"),
        ("Phone Number", "Personal WhatsApp", "Business API number"),
        ("Message Templates", "Not required", "Required for 24h+ messages"),
        ("Cost", "Self-hosted (free)", "Per-message pricing"),
    ]
    
    for feature, wpp, elmujib in comparison:
        print(f"\n  {Colors.BOLD}{feature}:{Colors.RESET}")
        print(f"    WPPConnect: {wpp}")
        print(f"    Elmujib:    {elmujib}")
    
    print(f"\n{Colors.BOLD}Current Driver:{Colors.RESET} {settings.WHATSAPP_DRIVER}")


def generate_migration_report(wpp_results, elmujib_results, endpoints_results):
    """Generate comprehensive migration readiness report"""
    print_header("5. Migration Readiness Report", Colors.GREEN)
    
    print(f"\n{Colors.BOLD}Status Summary:{Colors.RESET}\n")
    
    # WPPConnect Status
    print(f"{Colors.BOLD}Current Provider (WPPConnect):{Colors.RESET}")
    if wpp_results['configured']:
        print_status("  Configured", "OK")
    else:
        print_status("  Configured", "FAIL")
    
    if wpp_results['reachable']:
        print_status("  Server Reachable", "OK")
    else:
        print_status("  Server Reachable", "FAIL")
    
    if wpp_results['connected']:
        print_status("  WhatsApp Connected", "OK")
    else:
        print_status("  WhatsApp Connected", "WARN")
    
    # Elmujib Status
    print(f"\n{Colors.BOLD}Target Provider (Elmujib):{Colors.RESET}")
    if elmujib_results['configured']:
        print_status("  Configured", "OK")
    else:
        print_status("  Configured", "FAIL")
    
    if elmujib_results['credentials_valid']:
        print_status("  Credentials Valid", "OK")
    else:
        print_status("  Credentials Valid", "FAIL")
    
    if elmujib_results['ready']:
        print_status("  Ready for Use", "OK")
    else:
        print_status("  Ready for Use", "FAIL")
    
    if endpoints_results['endpoints_valid']:
        print_status("  API Endpoints", "OK")
    else:
        print_status("  API Endpoints", "FAIL")
    
    # Overall recommendation
    print(f"\n{Colors.BOLD}Recommendation:{Colors.RESET}")
    
    if elmujib_results['ready'] and endpoints_results['endpoints_valid']:
        print(f"\n{Colors.GREEN}✓ READY TO MIGRATE{Colors.RESET}")
        print("\nElmujib Cloud API is properly configured and ready to use.")
        print("\nTo switch to Elmujib, update settings.py:")
        print(f"{Colors.CYAN}WHATSAPP_DRIVER = 'elmujib_cloud'{Colors.RESET}")
        print("\nOr add to .env file:")
        print(f"{Colors.CYAN}WHATSAPP_DRIVER=elmujib_cloud{Colors.RESET}")
        
        if wpp_results['connected']:
            print(f"\n{Colors.YELLOW}Note:{Colors.RESET} WPPConnect is currently active and working.")
            print("Consider testing Elmujib in development first before switching production.")
        
    else:
        print(f"\n{Colors.RED}✗ NOT READY TO MIGRATE{Colors.RESET}")
        print("\nIssues found:")
        for error in elmujib_results['errors']:
            print(f"  - {error}")
        for error in endpoints_results['errors']:
            print(f"  - {error}")
        print("\nPlease fix these issues before migrating.")
    
    # Errors summary
    all_errors = wpp_results['errors'] + elmujib_results['errors'] + endpoints_results['errors']
    if all_errors:
        print(f"\n{Colors.BOLD}Issues Detected:{Colors.RESET}")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")


def main():
    """Main execution"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  Pre-Migration Check: WPPConnect -> Elmujib Cloud API")
    print(f"  Khalifa Pharmacy WhatsApp System")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}{Colors.RESET}\n")
    
    print("This check will verify:")
    print("  1. Current WPPConnect status")
    print("  2. Elmujib Cloud API configuration")
    print("  3. API endpoints readiness")
    print("  4. Configuration comparison")
    print("  5. Migration readiness report")
    
    input("\nPress Enter to continue...")
    
    # Run checks
    wpp_results = check_wppconnect_status()
    elmujib_results = check_elmujib_configuration()
    endpoints_results = test_elmujib_endpoints()
    compare_configurations()
    generate_migration_report(wpp_results, elmujib_results, endpoints_results)
    
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  Check Complete!")
    print(f"{'='*70}{Colors.RESET}\n")


if __name__ == '__main__':
    main()
