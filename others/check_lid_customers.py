import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'System'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

django.setup()

from conversations.models import Customer

print("=" * 60)
print("CHECKING CUSTOMERS WITH @LID NUMBERS")
print("=" * 60)

# These are the @lid numbers found in the database
lid_numbers = [
    '247201188036655',  # Customer #98 - already fixed
    '25516987932689',   # Customer #97
    '92908883587323',   # Customer #96
    '131748608372742',  # Customer #95
]

print("\nKnown @lid numbers from message history:")
for number in lid_numbers:
    print(f"  - {number}")

print("\n" + "-" * 60)
print("CHECKING CUSTOMER STATUS")
print("-" * 60)

for number in lid_numbers:
    customers = Customer.objects.filter(phone_number=number)
    
    if customers.exists():
        for customer in customers:
            is_lid_format = number in customer.wa_id and '@c.us' in customer.wa_id
            
            print(f"\nCustomer ID: {customer.id}")
            print(f"  Name: {customer.name}")
            print(f"  Phone: {customer.phone_number}")
            print(f"  wa_id: {customer.wa_id}")
            
            if is_lid_format:
                print(f"  Status: PROBLEM - This is an @lid number with @c.us")
                print(f"  Issue: Cannot send messages to {customer.wa_id}")
                print(f"  Fix: Customer needs to send a new message")
            else:
                print(f"  Status: OK - Has been updated with real number")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

problem_customers = []
for number in lid_numbers:
    customers = Customer.objects.filter(phone_number=number, wa_id__startswith=number)
    problem_customers.extend(customers)

if problem_customers:
    print(f"\nFound {len(problem_customers)} customers with @lid issues:")
    for c in problem_customers:
        print(f"  - ID {c.id}: {c.name} ({c.wa_id})")
    
    print("\nThese customers need to send a NEW WhatsApp message")
    print("so WPPConnect can extract their real phone number.")
else:
    print("\nAll customers have valid WhatsApp numbers!")
