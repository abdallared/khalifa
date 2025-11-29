import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

phone = '247201188036655'

print(f"Searching for customer with phone: {phone}")
print("=" * 60)

customers = Customer.objects.filter(phone_number__contains=phone)

if customers.exists():
    for c in customers:
        print(f"\nID: {c.id}")
        print(f"Phone: {c.phone_number}")
        print(f"wa_id: {c.wa_id}")
else:
    print("\nNo customer found with this phone number")

print("\n" + "=" * 60)
