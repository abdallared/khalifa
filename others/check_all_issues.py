import os
import sys
import django
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'System'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

django.setup()

from conversations.models import Customer

print("=" * 60)
print("CHECKING ALL POSSIBLE CAUSES")
print("=" * 60)

# 1. Check @lid entries in database
print("\n1. DATABASE @LID ENTRIES:")
print("-" * 60)
lid_customers = Customer.objects.filter(wa_id__contains='@lid')
print(f"Found {lid_customers.count()} customers with @lid")
if lid_customers.exists():
    for c in lid_customers[:10]:
        print(f"  ID: {c.id}, Name: {c.name}, wa_id: {c.wa_id}")
else:
    print("  OK - No @lid entries found")

# 2. Check invalid wa_id formats
print("\n2. INVALID WA_ID FORMATS:")
print("-" * 60)
invalid_customers = Customer.objects.exclude(wa_id__contains='@c.us').exclude(wa_id__contains='@g.us').exclude(wa_id__isnull=True).exclude(wa_id='')
print(f"Found {invalid_customers.count()} customers with invalid wa_id format")
if invalid_customers.exists():
    for c in invalid_customers[:10]:
        print(f"  ID: {c.id}, Name: {c.name}, wa_id: {c.wa_id}")
else:
    print("  OK - All wa_id formats are valid")

# 3. Check WPPConnect connection
print("\n3. WPPCONNECT CONNECTION STATUS:")
print("-" * 60)
try:
    response = requests.get(
        'http://localhost:21465/api/status',
        headers={'x-api-key': 'Bnjmj$G5BLj1ASpYEZVMiYgC5kEUfj'},
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: {data.get('state', 'Unknown')}")
        print(f"  Connected: {data.get('connected', False)}")
        if data.get('connected'):
            print("  OK - WPPConnect is connected")
        else:
            print("  ERROR - WPPConnect is not connected to WhatsApp")
    else:
        print(f"  ERROR - Server returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  ERROR - Cannot connect to WPPConnect server (not running?)")
except Exception as e:
    print(f"  ERROR - {str(e)}")

# 4. Check missing phone numbers
print("\n4. CUSTOMERS WITH MISSING WA_ID:")
print("-" * 60)
no_wa_id = Customer.objects.filter(wa_id__isnull=True) | Customer.objects.filter(wa_id='')
print(f"Found {no_wa_id.count()} customers without wa_id")
if no_wa_id.exists():
    for c in no_wa_id[:5]:
        print(f"  ID: {c.id}, Name: {c.name}, phone: {c.phone_number}")
else:
    print("  OK - All customers have wa_id")

# 5. Summary
print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)
total_issues = lid_customers.count() + invalid_customers.count() + no_wa_id.count()
if total_issues == 0:
    print("OK - No database issues found")
else:
    print(f"FOUND {total_issues} issues that need fixing")
    print("\nRun fix_all_issues.py to fix them")
