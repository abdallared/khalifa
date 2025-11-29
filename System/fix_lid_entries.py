import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

print("Fixing @lid entries in database...")
print("=" * 60)

problematic = Customer.objects.filter(wa_id__contains='@lid')
count = problematic.count()

print(f"\nFound {count} customers with @lid in wa_id")

if count == 0:
    print("\nNo @lid entries found. Database is clean!")
else:
    print("\nFixing entries...")
    print("-" * 60)
    
    fixed_count = 0
    for customer in problematic:
        old_wa_id = customer.wa_id
        new_wa_id = old_wa_id.replace('@lid', '@c.us')
        
        customer.wa_id = new_wa_id
        customer.save(update_fields=['wa_id'])
        
        print(f"ID: {customer.id:4d} | {old_wa_id:30s} -> {new_wa_id}")
        fixed_count += 1
    
    print("-" * 60)
    print(f"\nSuccessfully fixed {fixed_count} entries!")
    
    remaining = Customer.objects.filter(wa_id__contains='@lid').count()
    print(f"Remaining @lid entries: {remaining}")

print("\n" + "=" * 60)
print("Done!")
