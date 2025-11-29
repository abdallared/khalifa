import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'System'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

django.setup()

from conversations.models import Customer, Ticket

print("=" * 60)
print("COMPARING WORKING VS NON-WORKING CLIENTS")
print("=" * 60)

# Find working client
print("\nWORKING CLIENT (Abdallah Reda Elsayed):")
print("-" * 60)
working = Customer.objects.filter(name__icontains='Abdallah')
if working.exists():
    for c in working:
        print(f"ID: {c.id}")
        print(f"Name: {c.name}")
        print(f"Phone: {c.phone_number}")
        print(f"wa_id: {c.wa_id}")
        print(f"wa_id format: {'VALID' if '@c.us' in c.wa_id or '@g.us' in c.wa_id else 'INVALID'}")
        
        # Check recent tickets
        recent_tickets = Ticket.objects.filter(customer=c).order_by('-created_at')[:3]
        print(f"Recent tickets: {recent_tickets.count()}")
        for t in recent_tickets:
            print(f"  - Ticket #{t.id}: {t.status} (Created: {t.created_at.strftime('%Y-%m-%d %H:%M')})")
else:
    print("NOT FOUND")

# Find other recent customers with tickets
print("\n\nOTHER RECENT CLIENTS:")
print("-" * 60)
others = Customer.objects.exclude(name__icontains='Abdallah').order_by('-id')[:10]
for c in others:
    has_tickets = Ticket.objects.filter(customer=c).exists()
    if has_tickets:
        print(f"\nID: {c.id} | Name: {c.name}")
        print(f"  Phone: {c.phone_number}")
        print(f"  wa_id: {c.wa_id}")
        print(f"  Format: {'VALID' if '@c.us' in c.wa_id or '@g.us' in c.wa_id else 'INVALID'}")
        recent_tickets = Ticket.objects.filter(customer=c).order_by('-created_at')[:2]
        print(f"  Tickets: {Ticket.objects.filter(customer=c).count()} total")
        for t in recent_tickets:
            print(f"    - #{t.id}: {t.status}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
all_customers = Customer.objects.all()
valid = all_customers.filter(wa_id__contains='@c.us').count() + all_customers.filter(wa_id__contains='@g.us').count()
invalid = all_customers.count() - valid
print(f"Total customers: {all_customers.count()}")
print(f"Valid wa_id: {valid}")
print(f"Invalid wa_id: {invalid}")
