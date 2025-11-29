import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

print("Checking for @lid entries in database...")
print("=" * 60)

problematic = Customer.objects.filter(wa_id__contains='@lid')
count = problematic.count()

print(f"\nFound {count} customers with @lid in wa_id\n")

if count > 0:
    print("Problematic entries:")
    print("-" * 60)
    for c in problematic[:20]:
        print(f"ID: {c.id:4d} | Phone: {c.phone_number:15s} | wa_id: {c.wa_id}")
    
    if count > 20:
        print(f"\n... and {count - 20} more entries")

print("\n" + "=" * 60)
print("\nTo fix these entries, run: python fix_lid_entries.py")
