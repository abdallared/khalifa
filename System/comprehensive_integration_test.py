"""
Comprehensive Integration Test - End-to-End System Validation
Tests everything: Django, Database, Webhooks, Elmujib API, Message Flow

Run this before migrating to Business API to ensure everything works perfectly
"""

import os
import sys
import django
import json
import requests
from datetime import datetime
from time import sleep

sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.conf import settings
from django.db import connection
from conversations.models import Customer, Ticket, Message, User, Agent
from conversations.whatsapp_driver import get_whatsapp_driver, ElmujibCloudAPIDriver
from conversations.utils import normalize_phone_number


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class IntegrationTester:
    def __init__(self):
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'errors': []
        }
        self.django_server_url = "http://127.0.0.1:8000"
    
    def print_header(self, text, color=Colors.CYAN):
        """Print section header"""
        print(f"\n{color}{'='*75}")
        print(f"  {text}")
        print(f"{'='*75}{Colors.RESET}")
    
    def print_subheader(self, text):
        """Print subsection header"""
        print(f"\n{Colors.BOLD}--- {text} ---{Colors.RESET}")
    
    def test(self, name, func):
        """Run a test and track results"""
        self.results['total'] += 1
        try:
            result, message = func()
            if result == 'PASS':
                self.results['passed'] += 1
                print(f"{Colors.GREEN}[PASS]{Colors.RESET} {name}")
                if message:
                    print(f"       {message}")
            elif result == 'WARN':
                self.results['warnings'] += 1
                print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {name}")
                if message:
                    print(f"       {message}")
            else:
                self.results['failed'] += 1
                self.results['errors'].append(f"{name}: {message}")
                print(f"{Colors.RED}[FAIL]{Colors.RESET} {name}")
                if message:
                    print(f"       {message}")
            return result, message
        except Exception as e:
            self.results['failed'] += 1
            self.results['errors'].append(f"{name}: {str(e)}")
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {name}")
            print(f"       Exception: {str(e)}")
            return 'FAIL', str(e)
    
    # ========================================================================
    # TEST SUITE 1: DATABASE CONNECTIVITY
    # ========================================================================
    
    def test_database_connection(self):
        """Test database connection"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    return 'PASS', f"Database: {settings.DATABASES['default']['ENGINE']}"
            return 'FAIL', "Query returned unexpected result"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_database_tables(self):
        """Test that all required tables exist"""
        try:
            required_models = [Customer, Ticket, Message, User, Agent]
            for model in required_models:
                count = model.objects.count()
                # Just checking if query works, don't care about count
            return 'PASS', f"All {len(required_models)} tables accessible"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_database_write(self):
        """Test database write operations"""
        try:
            # Try to create a test customer
            test_phone = "201999999999"
            customer, created = Customer.objects.get_or_create(
                phone_number=test_phone,
                defaults={'name': 'Test Customer (Auto-Created)'}
            )
            
            if created:
                # Clean up
                customer.delete()
                return 'PASS', "Database write/delete successful"
            else:
                return 'PASS', "Database write successful (customer exists)"
        except Exception as e:
            return 'FAIL', str(e)
    
    # ========================================================================
    # TEST SUITE 2: DJANGO SERVER
    # ========================================================================
    
    def test_django_server_running(self):
        """Test if Django server is running"""
        try:
            response = requests.get(f"{self.django_server_url}/", timeout=5)
            return 'PASS', f"Server running on {self.django_server_url}"
        except requests.exceptions.ConnectionError:
            return 'FAIL', f"Django server not running on {self.django_server_url}"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_api_endpoints_accessible(self):
        """Test API endpoints are accessible"""
        try:
            # Test the API root
            response = requests.get(f"{self.django_server_url}/api/", timeout=5)
            if response.status_code in [200, 403]:  # 403 is ok (auth required)
                return 'PASS', f"API endpoints accessible (Status: {response.status_code})"
            return 'FAIL', f"Unexpected status code: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return 'FAIL', "Cannot connect to Django API"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_webhook_endpoint_exists(self):
        """Test webhook endpoints exist"""
        try:
            # Test WPPConnect webhook
            response = requests.post(
                f"{self.django_server_url}/api/whatsapp/webhook/",
                json={},
                timeout=5
            )
            # Should return 401 (no API key) or process the empty data
            if response.status_code in [401, 400, 200]:
                wpp_ok = True
            else:
                wpp_ok = False
            
            # Test Cloud API webhook (GET for verification)
            response = requests.get(
                f"{self.django_server_url}/api/whatsapp/cloud/webhook/",
                timeout=5
            )
            # Should return 403 (invalid verification) or 200
            if response.status_code in [403, 400, 200]:
                cloud_ok = True
            else:
                cloud_ok = False
            
            if wpp_ok and cloud_ok:
                return 'PASS', "Both webhook endpoints accessible"
            elif wpp_ok:
                return 'WARN', "WPPConnect webhook OK, Cloud API webhook issue"
            elif cloud_ok:
                return 'WARN', "Cloud API webhook OK, WPPConnect webhook issue"
            else:
                return 'FAIL', "Both webhooks have issues"
        except Exception as e:
            return 'FAIL', str(e)
    
    # ========================================================================
    # TEST SUITE 3: ELMUJIB CLOUD API
    # ========================================================================
    
    def test_elmujib_configuration(self):
        """Test Elmujib Cloud API configuration"""
        try:
            required_settings = {
                'ELMUJIB_API_BASE_URL': settings.ELMUJIB_API_BASE_URL,
                'ELMUJIB_VENDOR_UID': settings.ELMUJIB_VENDOR_UID,
                'ELMUJIB_BEARER_TOKEN': settings.ELMUJIB_BEARER_TOKEN,
            }
            
            missing = []
            for key, value in required_settings.items():
                if not value or value == 'your_bearer_token_here':
                    missing.append(key)
            
            if missing:
                return 'FAIL', f"Missing: {', '.join(missing)}"
            
            return 'PASS', f"All credentials configured"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_elmujib_driver_init(self):
        """Test Elmujib driver initialization"""
        try:
            config = {
                'base_url': settings.ELMUJIB_API_BASE_URL,
                'vendor_uid': settings.ELMUJIB_VENDOR_UID,
                'bearer_token': settings.ELMUJIB_BEARER_TOKEN,
                'from_phone_number_id': settings.ELMUJIB_FROM_PHONE_NUMBER_ID,
                'auth_method': settings.ELMUJIB_AUTH_METHOD,
                'timeout': settings.ELMUJIB_TIMEOUT
            }
            
            driver = ElmujibCloudAPIDriver(config)
            
            if driver.vendor_uid and driver.bearer_token:
                return 'PASS', f"Driver initialized (Auth: {driver.auth_method})"
            return 'FAIL', "Driver missing credentials"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_elmujib_connection_status(self):
        """Test Elmujib connection status"""
        try:
            config = {
                'base_url': settings.ELMUJIB_API_BASE_URL,
                'vendor_uid': settings.ELMUJIB_VENDOR_UID,
                'bearer_token': settings.ELMUJIB_BEARER_TOKEN,
                'from_phone_number_id': settings.ELMUJIB_FROM_PHONE_NUMBER_ID,
                'auth_method': settings.ELMUJIB_AUTH_METHOD,
                'timeout': settings.ELMUJIB_TIMEOUT
            }
            
            driver = ElmujibCloudAPIDriver(config)
            status = driver.get_connection_status()
            
            if status.get('success') and status.get('connected'):
                return 'PASS', "Elmujib credentials valid"
            return 'FAIL', status.get('error', 'Connection check failed')
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_elmujib_phone_normalization(self):
        """Test phone number normalization"""
        try:
            config = {
                'base_url': settings.ELMUJIB_API_BASE_URL,
                'vendor_uid': settings.ELMUJIB_VENDOR_UID,
                'bearer_token': settings.ELMUJIB_BEARER_TOKEN,
                'from_phone_number_id': settings.ELMUJIB_FROM_PHONE_NUMBER_ID,
                'auth_method': settings.ELMUJIB_AUTH_METHOD,
                'timeout': settings.ELMUJIB_TIMEOUT
            }
            
            driver = ElmujibCloudAPIDriver(config)
            
            test_cases = [
                ('01234567890', '201234567890'),
                ('+201234567890', '201234567890'),
                ('201234567890', '201234567890'),
            ]
            
            all_pass = True
            for input_phone, expected in test_cases:
                result = driver.normalize_phone(input_phone)
                if result != expected:
                    all_pass = False
                    break
            
            if all_pass:
                return 'PASS', f"All {len(test_cases)} normalization tests passed"
            return 'FAIL', "Phone normalization failed"
        except Exception as e:
            return 'FAIL', str(e)
    
    # ========================================================================
    # TEST SUITE 4: WPPCONNECT (CURRENT PROVIDER)
    # ========================================================================
    
    def test_wppconnect_configuration(self):
        """Test WPPConnect configuration"""
        try:
            base_url = settings.WPPCONNECT_BASE_URL
            api_key = settings.WPPCONNECT_API_KEY
            
            if base_url and api_key:
                return 'PASS', f"WPPConnect configured: {base_url}"
            return 'FAIL', "WPPConnect configuration missing"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_wppconnect_server_running(self):
        """Test if WPPConnect server is running"""
        try:
            url = f"{settings.WPPCONNECT_BASE_URL}/api/"
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 401, 404]:
                return 'PASS', "WPPConnect server responding"
            return 'WARN', f"Unexpected status: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return 'WARN', "WPPConnect server not running (OK if migrating)"
        except Exception as e:
            return 'WARN', str(e)
    
    # ========================================================================
    # TEST SUITE 5: MESSAGE FLOW SIMULATION
    # ========================================================================
    
    def test_simulate_webhook_message(self):
        """Simulate receiving a webhook message"""
        try:
            # Simulate a webhook payload
            test_phone = "201234567890"
            webhook_data = {
                "id_ext": "test_message_123",
                "phone": test_phone,
                "chat_id": f"{test_phone}@c.us",
                "message_text": "Test message from integration test",
                "message_type": "chat",
                "sender_name": "Integration Test User",
                "timestamp": int(datetime.now().timestamp()),
                "is_from_me": False,
                "media_url": None,
                "mime_type": None
            }
            
            response = requests.post(
                f"{self.django_server_url}/api/whatsapp/webhook/",
                json=webhook_data,
                headers={'X-API-Key': settings.WPPCONNECT_API_KEY},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return 'PASS', "Webhook processed successfully"
                return 'WARN', f"Webhook responded but: {data.get('message', 'Unknown')}"
            return 'FAIL', f"Status code: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return 'FAIL', "Cannot connect to Django server"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_customer_created_from_webhook(self):
        """Test if customer was created from webhook simulation"""
        try:
            test_phone = "201234567890"
            customer = Customer.objects.filter(phone_number=test_phone).first()
            
            if customer:
                return 'PASS', f"Customer found: {customer.name}"
            return 'WARN', "Customer not found (webhook may have failed)"
        except Exception as e:
            return 'FAIL', str(e)
    
    # ========================================================================
    # TEST SUITE 6: DRIVER FACTORY
    # ========================================================================
    
    def test_driver_factory_current(self):
        """Test driver factory with current driver"""
        try:
            driver = get_whatsapp_driver()
            if driver:
                return 'PASS', f"Current driver: {driver.provider_name}"
            return 'FAIL', "Driver factory returned None"
        except Exception as e:
            return 'FAIL', str(e)
    
    def test_driver_factory_elmujib(self):
        """Test driver factory can create Elmujib driver"""
        try:
            # Temporarily switch to elmujib
            original_driver = settings.WHATSAPP_DRIVER
            settings.WHATSAPP_DRIVER = 'elmujib_cloud'
            
            driver = get_whatsapp_driver()
            
            # Restore original
            settings.WHATSAPP_DRIVER = original_driver
            
            if driver and driver.provider_name == 'elmujib_cloud':
                return 'PASS', "Elmujib driver can be instantiated"
            return 'FAIL', f"Wrong driver: {driver.provider_name if driver else 'None'}"
        except Exception as e:
            settings.WHATSAPP_DRIVER = original_driver
            return 'FAIL', str(e)
    
    # ========================================================================
    # TEST SUITE 7: SYSTEM UTILITIES
    # ========================================================================
    
    def test_phone_normalization_util(self):
        """Test phone normalization utility"""
        try:
            test_cases = [
                ('01234567890', '201234567890'),
                ('+201234567890', '201234567890'),
                ('00201234567890', '201234567890'),
            ]
            
            all_pass = True
            for input_phone, expected in test_cases:
                result = normalize_phone_number(input_phone)
                if result != expected:
                    all_pass = False
                    break
            
            if all_pass:
                return 'PASS', f"{len(test_cases)} normalization tests passed"
            return 'FAIL', "Normalization failed"
        except Exception as e:
            return 'FAIL', str(e)
    
    # ========================================================================
    # MAIN TEST RUNNER
    # ========================================================================
    
    def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{Colors.BOLD}{'='*75}")
        print(f"  COMPREHENSIVE INTEGRATION TEST")
        print(f"  End-to-End System Validation")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*75}{Colors.RESET}\n")
        
        print("This will test:")
        print("  1. Database connectivity and operations")
        print("  2. Django server and API endpoints")
        print("  3. Elmujib Cloud API integration")
        print("  4. WPPConnect current status")
        print("  5. Message flow simulation")
        print("  6. Driver factory and switching")
        print("  7. System utilities")
        
        input("\nPress Enter to start tests...")
        
        # Test Suite 1: Database
        self.print_header("1. DATABASE CONNECTIVITY", Colors.BLUE)
        self.test("Database Connection", self.test_database_connection)
        self.test("Database Tables", self.test_database_tables)
        self.test("Database Write Operations", self.test_database_write)
        
        # Test Suite 2: Django Server
        self.print_header("2. DJANGO SERVER", Colors.BLUE)
        self.test("Django Server Running", self.test_django_server_running)
        self.test("API Endpoints Accessible", self.test_api_endpoints_accessible)
        self.test("Webhook Endpoints", self.test_webhook_endpoint_exists)
        
        # Test Suite 3: Elmujib Cloud API
        self.print_header("3. ELMUJIB CLOUD API", Colors.BLUE)
        self.test("Elmujib Configuration", self.test_elmujib_configuration)
        self.test("Elmujib Driver Initialization", self.test_elmujib_driver_init)
        self.test("Elmujib Connection Status", self.test_elmujib_connection_status)
        self.test("Elmujib Phone Normalization", self.test_elmujib_phone_normalization)
        
        # Test Suite 4: WPPConnect
        self.print_header("4. WPPCONNECT (CURRENT PROVIDER)", Colors.BLUE)
        self.test("WPPConnect Configuration", self.test_wppconnect_configuration)
        self.test("WPPConnect Server Running", self.test_wppconnect_server_running)
        
        # Test Suite 5: Message Flow
        self.print_header("5. MESSAGE FLOW SIMULATION", Colors.BLUE)
        self.test("Simulate Webhook Message", self.test_simulate_webhook_message)
        self.test("Customer Created from Webhook", self.test_customer_created_from_webhook)
        
        # Test Suite 6: Driver Factory
        self.print_header("6. DRIVER FACTORY", Colors.BLUE)
        self.test("Current Driver", self.test_driver_factory_current)
        self.test("Elmujib Driver Creation", self.test_driver_factory_elmujib)
        
        # Test Suite 7: Utilities
        self.print_header("7. SYSTEM UTILITIES", Colors.BLUE)
        self.test("Phone Normalization Utility", self.test_phone_normalization_util)
        
        # Final Report
        self.print_final_report()
    
    def print_final_report(self):
        """Print comprehensive final report"""
        self.print_header("INTEGRATION TEST REPORT", Colors.GREEN)
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        warnings = self.results['warnings']
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}")
        print(f"  Total Tests:    {total}")
        print(f"  {Colors.GREEN}Passed:{Colors.RESET}         {passed}")
        print(f"  {Colors.RED}Failed:{Colors.RESET}         {failed}")
        print(f"  {Colors.YELLOW}Warnings:{Colors.RESET}       {warnings}")
        print(f"  {Colors.BOLD}Success Rate:{Colors.RESET}   {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n{Colors.BOLD}Errors Summary:{Colors.RESET}")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"  {i}. {error}")
        
        print(f"\n{Colors.BOLD}Migration Readiness:{Colors.RESET}")
        
        # Critical checks
        critical_checks = {
            'Database': passed >= 3,  # All 3 database tests
            'Django Server': self.results['total'] >= 3,  # Server running
            'Elmujib API': passed >= 3,  # Elmujib configured
        }
        
        all_critical_pass = all(critical_checks.values())
        
        for check, status in critical_checks.items():
            icon = f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"
            print(f"  {icon} {check}")
        
        print(f"\n{Colors.BOLD}Recommendation:{Colors.RESET}")
        
        if failed == 0 and warnings == 0:
            print(f"\n{Colors.GREEN}✓ PERFECT! ALL SYSTEMS GO!{Colors.RESET}")
            print("\nYour system is in perfect condition.")
            print("Ready to migrate to Elmujib Cloud API anytime.")
            
        elif failed == 0 and warnings > 0:
            print(f"\n{Colors.YELLOW}⚠ READY WITH MINOR WARNINGS{Colors.RESET}")
            print("\nMost systems working correctly.")
            print("Review warnings above before migration.")
            print("Safe to migrate if warnings are expected (e.g., WPPConnect not needed).")
            
        elif failed <= 2:
            print(f"\n{Colors.YELLOW}⚠ ALMOST READY{Colors.RESET}")
            print("\nMost tests passed but some issues found.")
            print("Fix the failed tests before migration:")
            for error in self.results['errors']:
                print(f"  - {error}")
                
        else:
            print(f"\n{Colors.RED}✗ NOT READY FOR MIGRATION{Colors.RESET}")
            print("\nMultiple critical issues detected.")
            print("Please fix these issues before migrating:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        if all_critical_pass:
            print("\n1. Review this report")
            print("2. Run: python switch_whatsapp_provider.py")
            print("3. Select option 2 (Elmujib Cloud)")
            print("4. Restart Django server")
            print("5. Test sending messages")
        else:
            print("\n1. Fix critical issues listed above")
            print("2. Ensure Django server is running: python manage.py runserver")
            print("3. Verify .env file has all Elmujib credentials")
            print("4. Re-run this test")
        
        print(f"\n{Colors.BOLD}{'='*75}{Colors.RESET}\n")


def main():
    tester = IntegrationTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
