import os
import sys
import django
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer
from django.db import models

# Find customers with invalid phone numbers (15+ digits or unusual patterns)
invalid_customers = Customer.objects.filter(
    models.Q(phone_number__regex=r'^\d{14,}$') |  # 14+ digit numbers
    models.Q(phone_number__startswith='1283550') |  # Suspicious prefix
    models.Q(phone_number__startswith='274456') |  # Suspicious prefix  
    models.Q(phone_number__startswith='59000')  # Suspicious prefix
)

print(f"Found {invalid_customers.count()} customers with invalid phone numbers:")
print("-" * 50)

for customer in invalid_customers:
    if not customer.name.startswith('[INVALID PHONE]'):
        old_name = customer.name
        customer.name = f"[INVALID PHONE] {customer.name}"
        customer.save()
        print(f"Updated: {old_name} -> {customer.name}")
        print(f"  Phone: {customer.phone_number}")
    else:
        print(f"Already marked: {customer.name}")
        print(f"  Phone: {customer.phone_number}")

print("-" * 50)
print("Done! These customers need their real phone numbers to be updated.")