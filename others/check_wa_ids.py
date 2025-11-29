import os
import sys
import django

# Setup Django
sys.path.append('e:\\Hive_Work\\Projects\\Kh_Pharmacy\\final_kh\\V1\\Anas_S05\\Anas_S04\\st_9\\st_8\\khalifa\\System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

print("=== Checking Customer wa_id Values ===")
customers = Customer.objects.all()[:10]
for c in customers:
    print(f"Phone: {c.phone_number} -> wa_id: {c.wa_id}")
    
print(f"\nTotal customers checked: {len(customers)}")

# Check for empty wa_ids
empty_wa_id = Customer.objects.filter(wa_id__isnull=True).count()
empty_wa_id_blank = Customer.objects.filter(wa_id='').count()
print(f"Customers with NULL wa_id: {empty_wa_id}")
print(f"Customers with empty wa_id: {empty_wa_id_blank}")