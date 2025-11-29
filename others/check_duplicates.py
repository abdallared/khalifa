import os
import sys
import django
import io
from django.db.models import Count

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

# Check for customers with similar names
names_to_check = ['Zeka', 'Mohmmed Mohsen', 'عميل 1998', 'عميل 7323', 'عميل 2689']

print("Checking for duplicate customers or similar names...")
print("-" * 80)

for name in names_to_check:
    print(f"\n🔍 Searching for: {name}")
    
    # Exact match
    exact = Customer.objects.filter(name=name)
    if exact.exists():
        print(f"  Exact matches ({exact.count()}):")
        for c in exact:
            print(f"    - ID: {c.id}, Phone: {c.phone_number}, Name: {c.name}")
    
    # Contains match
    contains = Customer.objects.filter(name__icontains=name.replace('[INVALID PHONE] ', ''))
    if contains.exists():
        print(f"  Contains '{name}' ({contains.count()}):")
        for c in contains:
            print(f"    - ID: {c.id}, Phone: {c.phone_number}, Name: {c.name}")
    
    # Check for similar patterns (for numbered customers)
    if 'عميل' in name:
        # Extract number
        import re
        number = re.search(r'\d+', name)
        if number:
            num = number.group()
            similar = Customer.objects.filter(name__icontains=num)
            if similar.exists():
                print(f"  Contains number '{num}' ({similar.count()}):")
                for c in similar:
                    if c.phone_number.startswith('20') and len(c.phone_number) == 12:
                        print(f"    - ✅ ID: {c.id}, Phone: {c.phone_number}, Name: {c.name}")

print("\n" + "=" * 80)
print("Checking all customers to find potential real phones...")
print("-" * 80)

# Get all customers with valid Egyptian phone numbers
valid_customers = Customer.objects.filter(
    phone_number__regex=r'^20\d{10}$'
).order_by('-created_at')[:20]

print(f"Recent customers with valid phone numbers:")
for c in valid_customers:
    print(f"  - ID: {c.id}, Phone: {c.phone_number}, Name: {c.name}, Created: {c.created_at}")

print("\n" + "=" * 80)
print("Checking for customers created around the same time as invalid ones...")

# Get invalid customers
invalid_customers = Customer.objects.filter(
    phone_number__in=['128355097681998', '2744568045622', '59000284524547', '92908883587323', '25516987932689']
)

for invalid in invalid_customers:
    print(f"\n🔍 {invalid.name} (ID: {invalid.id}, Created: {invalid.created_at})")
    
    # Find customers created within 5 minutes
    from datetime import timedelta
    time_range = timedelta(minutes=5)
    start_time = invalid.created_at - time_range
    end_time = invalid.created_at + time_range
    
    nearby = Customer.objects.filter(
        created_at__range=(start_time, end_time)
    ).exclude(id=invalid.id)
    
    if nearby.exists():
        print(f"  Customers created around the same time:")
        for c in nearby:
            if c.phone_number.startswith('20') and len(c.phone_number) == 12:
                print(f"    - ✅ POSSIBLE MATCH: ID: {c.id}, Phone: {c.phone_number}, Name: {c.name}")
            else:
                print(f"    - ID: {c.id}, Phone: {c.phone_number}, Name: {c.name}")