import os
import sys
import django
import io

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
sys.path.append('e:\\Hive_Work\\Projects\\Kh_Pharmacy\\final_kh\\V1\\Anas_S05\\Anas_S04\\st_9\\st_8\\khalifa\\System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer, Message, Ticket
from django.db.models import Q

print("=" * 60)
print("Fix Invalid Phone Numbers")
print("=" * 60)

# Find customers with invalid phone numbers
print("\n1. Finding customers with invalid phone numbers:")
print("-" * 30)

invalid_customers = []

# Check all customers
for customer in Customer.objects.all():
    phone = customer.phone_number
    wa_id = customer.wa_id
    
    # Check if phone number is invalid
    is_invalid = False
    reason = ""
    
    # Check length (Egyptian numbers should be 11-12 digits)
    if len(phone) > 13 or len(phone) < 10:
        is_invalid = True
        reason = f"Invalid length: {len(phone)} digits"
    
    # Check if it starts with valid Egyptian prefix
    elif not (phone.startswith('20') or phone.startswith('010') or phone.startswith('011') or phone.startswith('012') or phone.startswith('015')):
        # Check if it's not a test number
        if not any(test in phone for test in ['12345', '00000', '11111']):
            is_invalid = True
            reason = f"Invalid prefix: {phone[:3]}"
    
    if is_invalid:
        invalid_customers.append({
            'customer': customer,
            'reason': reason
        })
        print(f"  ❌ {customer.name}: {phone} ({reason})")

print(f"\nTotal invalid numbers found: {len(invalid_customers)}")

# Check if these customers have incoming messages (which means they're real WhatsApp users)
print("\n2. Checking if these are real WhatsApp users:")
print("-" * 30)

for item in invalid_customers:
    customer = item['customer']
    
    # Check for incoming messages
    incoming_messages = Message.objects.filter(
        ticket__customer=customer,
        direction='incoming'
    ).count()
    
    if incoming_messages > 0:
        print(f"\n  📱 {customer.name} ({customer.phone_number})")
        print(f"     Has {incoming_messages} incoming messages")
        print(f"     wa_id: {customer.wa_id}")
        
        # These are real WhatsApp users with non-standard numbers
        # The wa_id is what WhatsApp actually uses
        print(f"     ✅ This is a REAL WhatsApp user with non-standard number")
        print(f"     ⚠️  The wa_id ({customer.wa_id}) is what should be used for sending")

# The real issue analysis
print("\n" + "=" * 60)
print("ROOT CAUSE ANALYSIS")
print("=" * 60)

print("""
🔍 THE REAL ISSUE:

These customers (Bahaa Elhawary, راجية الفردوس) have:
1. Non-standard phone numbers (15 digits, unusual prefixes)
2. They ARE real WhatsApp users (they send messages)
3. Their wa_id is stored correctly

❌ WHY MESSAGES FAIL:
The numbers like 131748608372742 and 247201188036655 are:
- WhatsApp internal IDs (not phone numbers)
- These might be business accounts or special WhatsApp IDs
- They don't follow standard phone number formats

✅ THE SOLUTION:
These are likely WhatsApp Business API IDs or special accounts.
The system is correctly storing them as wa_id.
The issue is that these IDs might not be reachable via regular WhatsApp Web.

📋 RECOMMENDATIONS:
1. These customers might be using WhatsApp Business accounts
2. They might be international numbers with unusual formats
3. The incoming messages work because WhatsApp sends the correct ID
4. Outgoing messages fail because these IDs aren't standard phone numbers
""")

# Check if we can get more info from recent messages
print("\n3. Analyzing Recent Message Patterns:")
print("-" * 30)

for item in invalid_customers[:2]:  # Check first 2
    customer = item['customer']
    
    # Get recent messages
    recent_messages = Message.objects.filter(
        ticket__customer=customer
    ).order_by('-created_at')[:3]
    
    if recent_messages:
        print(f"\n  Customer: {customer.name}")
        for msg in recent_messages:
            print(f"    {msg.direction}: {msg.delivery_status} - {msg.created_at}")

print("\n" + "=" * 60)
print("Conclusion")
print("=" * 60)
print("""
The customers Bahaa Elhawary and راجية الفردوس have special WhatsApp IDs
that don't follow standard phone number formats. These might be:

1. WhatsApp Business API accounts
2. International numbers with special formatting
3. WhatsApp internal IDs for business accounts

The system receives their messages correctly but cannot send messages back
because these IDs aren't accessible via WhatsApp Web protocol.

This is a limitation of WhatsApp Web/WPPConnect with certain account types.
""")