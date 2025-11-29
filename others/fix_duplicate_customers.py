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

from conversations.models import Customer, Ticket, Message
from django.db.models import Count

print("=" * 60)
print("Fixing Duplicate Customers and Wrong IDs")
print("=" * 60)

# Find all Bahaa Elhawary customers
print("\n1. Analyzing Bahaa Elhawary customers:")
print("-" * 30)

bahaa_customers = Customer.objects.filter(name__icontains='Bahaa')
for c in bahaa_customers:
    ticket_count = Ticket.objects.filter(customer=c).count()
    message_count = Message.objects.filter(ticket__customer=c).count()
    print(f"ID: {c.id}, Name: {c.name}")
    print(f"  Phone: {c.phone_number}, wa_id: {c.wa_id}")
    print(f"  Tickets: {ticket_count}, Messages: {message_count}")
    print()

# Find all راجية الفردوس customers
print("\n2. Analyzing راجية الفردوس customers:")
print("-" * 30)

rajia_customers = Customer.objects.filter(name__icontains='راجية')
for c in rajia_customers:
    ticket_count = Ticket.objects.filter(customer=c).count()
    message_count = Message.objects.filter(ticket__customer=c).count()
    print(f"ID: {c.id}, Name: {c.name}")
    print(f"  Phone: {c.phone_number}, wa_id: {c.wa_id}")
    print(f"  Tickets: {ticket_count}, Messages: {message_count}")
    print()

# Merge duplicates
print("\n3. Merging duplicate customers:")
print("-" * 30)

# For Bahaa Elhawary - merge the wrong one into the correct one
correct_bahaa = Customer.objects.filter(phone_number='201013655361').first()
wrong_bahaa = Customer.objects.filter(phone_number='131748608372742').first()

if correct_bahaa and wrong_bahaa and correct_bahaa.id != wrong_bahaa.id:
    print(f"\nMerging Bahaa Elhawary:")
    print(f"  Keeping: ID {correct_bahaa.id} ({correct_bahaa.phone_number})")
    print(f"  Deleting: ID {wrong_bahaa.id} ({wrong_bahaa.phone_number})")
    
    # Move all tickets from wrong to correct
    tickets_moved = Ticket.objects.filter(customer=wrong_bahaa).update(customer=correct_bahaa)
    print(f"  Moved {tickets_moved} tickets")
    
    # Delete the wrong customer
    wrong_bahaa.delete()
    print(f"  ✅ Deleted duplicate customer")

# For راجية الفردوس - fix the phone number
wrong_rajia = Customer.objects.filter(phone_number='247201188036655').first()
if wrong_rajia:
    print(f"\nFixing راجية الفردوس:")
    print(f"  Current: {wrong_rajia.phone_number}")
    
    # Check if correct number already exists
    correct_phone = '201151218425'
    existing = Customer.objects.filter(phone_number=correct_phone).first()
    
    if existing and existing.id != wrong_rajia.id:
        print(f"  Found existing customer with correct number: ID {existing.id}")
        # Move tickets to existing
        tickets_moved = Ticket.objects.filter(customer=wrong_rajia).update(customer=existing)
        print(f"  Moved {tickets_moved} tickets")
        wrong_rajia.delete()
        print(f"  ✅ Deleted duplicate")
    else:
        # Update to correct number
        wrong_rajia.phone_number = correct_phone
        wrong_rajia.wa_id = correct_phone + '@c.us'
        wrong_rajia.save()
        print(f"  ✅ Updated to: {wrong_rajia.phone_number}")

# Final check
print("\n4. Final verification:")
print("-" * 30)

# Check Bahaa
bahaa_final = Customer.objects.filter(name__icontains='Bahaa')
print(f"Bahaa Elhawary customers remaining: {bahaa_final.count()}")
for c in bahaa_final:
    print(f"  - ID: {c.id}, Phone: {c.phone_number}, wa_id: {c.wa_id}")

# Check راجية
rajia_final = Customer.objects.filter(name__icontains='راجية')
print(f"\nراجية الفردوس customers remaining: {rajia_final.count()}")
for c in rajia_final:
    print(f"  - ID: {c.id}, Phone: {c.phone_number}, wa_id: {c.wa_id}")

print("\n" + "=" * 60)
print("Cleanup Complete!")
print("=" * 60)