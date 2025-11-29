
import os
import sys
import django
import logging

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.conf import settings
from conversations.whatsapp_driver import get_whatsapp_driver

# Configure logging to see details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_send_message():
    print("Initializing Elmujib Driver...")
    
    # Force the driver to use Elmujib settings
    # (Assuming the settings are already correctly loaded from .env as verified by previous tests)
    settings.WHATSAPP_DRIVER = 'elmujib_cloud'
    
    driver = get_whatsapp_driver()
    
    target_phone = "201205455559"
    message_body = "Hello from Khalifa Pharmacy System - Test Message"
    
    print(f"Attempting to send message to {target_phone}...")
    print(f"Provider: {driver.provider_name}")
    print(f"Base URL: {driver.base_url}")
    
    try:
        result = driver.send_text_message(target_phone, message_body)
        
        if result.get('success'):
            print("\nSUCCESS! Message sent.")
            print(f"Message ID: {result.get('message_id')}")
            print(f"Full Result: {result}")
        else:
            print("\nFAILURE! Message could not be sent.")
            print(f"Error: {result.get('error')}")
            print(f"Full Result: {result}")
            
    except Exception as e:
        print(f"\nEXCEPTION occurred: {str(e)}")

if __name__ == "__main__":
    test_send_message()
