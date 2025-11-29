import os
import sys
import django
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'System'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

django.setup()

from conversations.models import Customer

print("=" * 60)
print("FINDING CUSTOMERS WITH @LID HISTORY")
print("=" * 60)

# Search for @lid in the database file directly
db_path = os.path.join(os.path.dirname(__file__), 'System', 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find all chat_ids that contain @lid in messages
cursor.execute("""
    SELECT DISTINCT chat_id 
    FROM conversations_message 
    WHERE chat_id LIKE '%@lid%'
""")

lid_chat_ids = cursor.fetchall()
print(f"\nFound {len(lid_chat_ids)} unique @lid chat IDs in message history")

# Extract the phone numbers from @lid format
lid_numbers = []
for (chat_id,) in lid_chat_ids:
    if '@lid' in chat_id:
        number = chat_id.split('@')[0]
        lid_numbers.append(number)
        print(f"  - {chat_id} -> {number}")

print("\n" + "-" * 60)
print("CHECKING CUSTOMERS WITH THESE NUMBERS")
print("-" * 60)

# Find customers with these phone numbers
for number in lid_numbers:
    # Check by phone_number or wa_id
    customers = Customer.objects.filter(phone_number=number) | Customer.objects.filter(wa_id__startswith=number)
    
    if customers.exists():
        for customer in customers:
            print(f"\nCustomer ID: {customer.id}")
            print(f"  Name: {customer.name}")
            print(f"  Phone: {customer.phone_number}")
            print(f"  wa_id: {customer.wa_id}")
            print(f"  Status: {'INVALID - @lid number' if number in customer.wa_id else 'OK'}")
    else:
        print(f"\n{number}: No customer found")

conn.close()

print("\n" + "=" * 60)
print("SOLUTION")
print("=" * 60)
print("""
These customers have @lid numbers stored as wa_id.
@lid are LOCAL IDs, not real WhatsApp numbers.

To fix:
1. Ask these customers to send a NEW message
2. WPPConnect will extract their REAL phone number
3. Django will auto-update their wa_id
4. Then agent messages will reach them

Alternatively, manually update their wa_id if you know
their real WhatsApp number.
""")
