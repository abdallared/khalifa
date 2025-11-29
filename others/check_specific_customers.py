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
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

print("=" * 60)
print("Checking Specific Customers with Issues")
print("=" * 60)

# Search for the specific customers
customers_to_check = ['Bahaa Elhawary', 'راجية الفردوس']

for name in customers_to_check:
    print(f"\n{'='*40}")
    print(f"Searching for: {name}")
    print('='*40)
    
    # Search by name (case insensitive and partial match)
    customers = Customer.objects.filter(
        Q(name__icontains=name) | Q(name__icontains=name.lower())
    )
    
    if not customers.exists():
        print(f"❌ No customer found with name containing: {name}")
        continue
    
    for customer in customers:
        print(f"\n📋 Customer Details:")
        print(f"  ID: {customer.id}")
        print(f"  Name: {customer.name}")
        print(f"  Phone: {customer.phone_number}")
        print(f"  wa_id: {customer.wa_id}")
        print(f"  Created: {customer.created_at}")
        
        # Check phone number format
        phone = customer.phone_number
        print(f"\n📞 Phone Number Analysis:")
        print(f"  Original: {phone}")
        print(f"  Length: {len(phone)}")
        print(f"  Starts with +: {phone.startswith('+')}")
        print(f"  Contains spaces: {' ' in phone}")
        print(f"  Contains special chars: {any(c in phone for c in '()- ')}")
        
        # Check wa_id format
        if customer.wa_id:
            print(f"\n🔍 wa_id Analysis:")
            print(f"  wa_id: {customer.wa_id}")
            print(f"  Has @c.us: {'@c.us' in customer.wa_id}")
            print(f"  Has @lid: {'@lid' in customer.wa_id}")
            
            # Extract the number part
            if '@' in customer.wa_id:
                number_part = customer.wa_id.split('@')[0]
                print(f"  Number part: {number_part}")
                print(f"  Number length: {len(number_part)}")
        
        # Check recent tickets
        recent_tickets = Ticket.objects.filter(
            customer=customer
        ).order_by('-created_at')[:3]
        
        print(f"\n🎫 Recent Tickets: {recent_tickets.count()}")
        for ticket in recent_tickets:
            print(f"  - Ticket #{ticket.id}: {ticket.status} (Created: {ticket.created_at})")
            
            # Check messages in this ticket
            messages = Message.objects.filter(ticket=ticket).order_by('-created_at')[:5]
            print(f"    Messages: {messages.count()}")
            
            for msg in messages:
                status_icon = "✅" if msg.delivery_status == 'sent' else "❌"
                print(f"    {status_icon} {msg.direction}: {msg.delivery_status} - {msg.message_text[:30]}...")
                
            # Check for failed messages
            failed_msgs = Message.objects.filter(
                ticket=ticket,
                delivery_status='failed'
            ).count()
            if failed_msgs > 0:
                print(f"    ⚠️ Failed messages in this ticket: {failed_msgs}")

print("\n" + "=" * 60)
print("Analysis Complete")
print("=" * 60)