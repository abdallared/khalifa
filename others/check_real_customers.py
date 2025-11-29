import os
import sys
import django

# Setup Django
sys.path.append('e:\\Hive_Work\\Projects\\Kh_Pharmacy\\final_kh\\V1\\Anas_S05\\Anas_S04\\st_9\\st_8\\khalifa\\System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer, Message
from django.utils import timezone
from datetime import timedelta

print("=== Checking for Real WhatsApp Customers ===")

# Get customers who have sent messages in the last 7 days
recent_date = timezone.now() - timedelta(days=7)
recent_messages = Message.objects.filter(
    direction='incoming',
    created_at__gte=recent_date
).select_related('ticket__customer').order_by('-created_at')

seen_customers = set()
for msg in recent_messages[:20]:
    customer = msg.ticket.customer
    if customer.wa_id and customer.wa_id not in seen_customers:
        seen_customers.add(customer.wa_id)
        print(f"\nCustomer: {customer.name}")
        print(f"Phone: {customer.phone_number}")
        print(f"wa_id: {customer.wa_id}")
        print(f"Last message: {msg.created_at}")
        
        # Check if it's a real number (not test data)
        if not any(test in customer.phone_number for test in ['12345', '00000', '11111']):
            print("✅ Looks like a real customer")
        else:
            print("⚠️ Looks like test data")
            
print(f"\n\nTotal unique customers found: {len(seen_customers)}")