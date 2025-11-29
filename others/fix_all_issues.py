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
print("FIXING ALL ISSUES")
print("=" * 60)

# Fix 1: Convert @lid to @c.us (if any exist)
print("\n1. FIXING @LID ENTRIES:")
print("-" * 60)
lid_customers = Customer.objects.filter(wa_id__contains='@lid')
if lid_customers.exists():
    for customer in lid_customers:
        old_wa_id = customer.wa_id
        new_wa_id = customer.wa_id.replace('@lid', '@c.us')
        customer.wa_id = new_wa_id
        customer.save()
        print(f"  Fixed ID {customer.id}: {old_wa_id} -> {new_wa_id}")
    print(f"\nFixed {lid_customers.count()} customers")
else:
    print("  OK - No @lid entries to fix")

# Fix 2: Add @c.us suffix to wa_id that don't have it
print("\n2. FIXING MISSING @c.us SUFFIX:")
print("-" * 60)
invalid_customers = Customer.objects.exclude(wa_id__contains='@c.us').exclude(wa_id__contains='@g.us').exclude(wa_id__isnull=True).exclude(wa_id='')
if invalid_customers.exists():
    for customer in invalid_customers:
        old_wa_id = customer.wa_id
        # Only add @c.us if it's a number without any @ symbol
        if '@' not in customer.wa_id:
            new_wa_id = customer.wa_id + '@c.us'
            customer.wa_id = new_wa_id
            customer.save()
            print(f"  Fixed ID {customer.id}: {old_wa_id} -> {new_wa_id}")
        else:
            print(f"  Skipped ID {customer.id}: {old_wa_id} (already has @)")
    print(f"\nFixed {invalid_customers.count()} customers")
else:
    print("  OK - All wa_id have proper format")

# Fix 3: Remove invalid wa_id entries (just @ or empty)
print("\n3. CLEANING INVALID WA_ID:")
print("-" * 60)
only_suffix = Customer.objects.filter(wa_id__startswith='@').exclude(wa_id__contains='c.us').exclude(wa_id__contains='g.us')
if only_suffix.exists():
    for customer in only_suffix:
        old_wa_id = customer.wa_id
        # Use phone_number as fallback
        if customer.phone_number:
            new_wa_id = customer.phone_number + '@c.us'
            customer.wa_id = new_wa_id
            customer.save()
            print(f"  Fixed ID {customer.id}: {old_wa_id} -> {new_wa_id}")
        else:
            print(f"  WARNING: ID {customer.id} has no phone_number, keeping {old_wa_id}")
    print(f"\nFixed {only_suffix.count()} customers")
else:
    print("  OK - No invalid wa_id entries")

print("\n" + "=" * 60)
print("ALL FIXES COMPLETED!")
print("=" * 60)
print("\nRun check_all_issues.py to verify")
