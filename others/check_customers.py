import os
import sys
import django
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

customers_to_check = ['عميل 1998', 'Zeka', 'Mohmmed Mohsen']

print("Checking customers with problematic phone numbers:")
print("-" * 50)

for name in customers_to_check:
    customers = Customer.objects.filter(name=name)
    for c in customers:
        print(f"Name: {c.name}")
        print(f"Phone: {c.phone_number}")
        print(f"ID: {c.id}")
        print(f"Created: {c.created_at}")
        print("-" * 50)