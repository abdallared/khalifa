import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Fix Unicode output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
sys.path.append('e:\\Hive_Work\\Projects\\Kh_Pharmacy\\final_kh\\V1\\Anas_S05\\Anas_S04\\st_9\\st_8\\khalifa\\System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer, Ticket, Message
from conversations.whatsapp_driver import get_whatsapp_driver
from django.utils import timezone
from django.conf import settings

print("=" * 60)
print("WhatsApp Message Delivery Diagnostic")
print("=" * 60)

# 1. Check WhatsApp configuration
print("\n1. WhatsApp Configuration:")
print("-" * 30)
whatsapp_config = getattr(settings, 'WHATSAPP_CONFIG', {})
print(f"Base URL: {whatsapp_config.get('base_url', 'NOT SET')}")
print(f"API Key: {'SET' if whatsapp_config.get('api_key') else 'NOT SET'}")
print(f"Timeout: {whatsapp_config.get('timeout', 30)} seconds")

# 2. Test WPPConnect server connection
print("\n2. Testing WPPConnect Server:")
print("-" * 30)
try:
    base_url = whatsapp_config.get('base_url', 'http://localhost:3000')
    api_key = whatsapp_config.get('api_key', '')
    
    # Test server status
    response = requests.get(
        f"{base_url}/api/status",
        headers={'X-API-Key': api_key},
        timeout=5
    )
    print(f"Server Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"❌ Server connection failed: {e}")

# 3. Check recent messages
print("\n3. Recent Messages (Last 24 hours):")
print("-" * 30)
yesterday = timezone.now() - timedelta(days=1)
recent_messages = Message.objects.filter(created_at__gte=yesterday).order_by('-created_at')[:5]

for msg in recent_messages:
    print(f"\n  Time: {msg.created_at}")
    print(f"  Direction: {msg.direction}")
    print(f"  Type: {msg.message_type}")
    print(f"  Status: {msg.delivery_status}")
    print(f"  Text: {msg.message_text[:50]}..." if len(msg.message_text) > 50 else f"  Text: {msg.message_text}")

# 4. Check customers with recent activity
print("\n4. Customers with Recent Activity:")
print("-" * 30)
recent_tickets = Ticket.objects.filter(created_at__gte=yesterday).select_related('customer')[:5]

for ticket in recent_tickets:
    customer = ticket.customer
    print(f"\n  Customer: {customer.name}")
    print(f"  Phone: {customer.phone_number}")
    print(f"  wa_id: {customer.wa_id}")
    print(f"  Ticket Status: {ticket.status}")
    print(f"  Has Welcome: {ticket.messages.filter(message_text__contains='مرحبا').exists()}")

# 5. Test sending a message
print("\n5. Test Message Sending:")
print("-" * 30)
test_customer = Customer.objects.filter(wa_id__isnull=False).exclude(wa_id='').first()

if test_customer:
    print(f"Testing with customer: {test_customer.name} ({test_customer.wa_id})")
    
    # Initialize driver
    driver = get_whatsapp_driver()
    
    # Try to send a test message
    test_message = f"🔧 Test message from diagnostic tool - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"Sending to: {test_customer.wa_id}")
    print(f"Message: {test_message}")
    
    try:
        result = driver.send_text_message(
            phone=test_customer.wa_id,
            message=test_message
        )
        print(f"Result: {result}")
        
        if result.get('success'):
            print("✅ Message sent successfully!")
        else:
            print(f"❌ Failed to send: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception during send: {e}")
else:
    print("❌ No customers found with wa_id")

# 6. Check for common issues
print("\n6. Common Issues Check:")
print("-" * 30)

# Check for customers without wa_id
no_wa_id = Customer.objects.filter(wa_id__isnull=True).count()
empty_wa_id = Customer.objects.filter(wa_id='').count()
print(f"Customers without wa_id: {no_wa_id}")
print(f"Customers with empty wa_id: {empty_wa_id}")

# Check for @lid entries
lid_customers = Customer.objects.filter(wa_id__contains='@lid').count()
cus_customers = Customer.objects.filter(wa_id__contains='@c.us').count()
print(f"Customers with @lid: {lid_customers}")
print(f"Customers with @c.us: {cus_customers}")

# Check for failed messages
failed_messages = Message.objects.filter(
    delivery_status='failed',
    created_at__gte=yesterday
).count()
print(f"Failed messages (last 24h): {failed_messages}")

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)