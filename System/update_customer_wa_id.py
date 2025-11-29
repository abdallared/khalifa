import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

customer_id = 98
old_wa_id = '247201188036655@c.us'
new_wa_id = '201151218425@c.us'

print(f"Updating customer {customer_id}")
print("=" * 60)

try:
    customer = Customer.objects.get(id=customer_id)
    
    print(f"\nBefore update:")
    print(f"  Phone: {customer.phone_number}")
    print(f"  wa_id: {customer.wa_id}")
    
    customer.wa_id = new_wa_id
    customer.save(update_fields=['wa_id'])
    
    print(f"\nAfter update:")
    print(f"  Phone: {customer.phone_number}")
    print(f"  wa_id: {customer.wa_id}")
    
    print("\n" + "=" * 60)
    print("Successfully updated!")
    
except Customer.DoesNotExist:
    print(f"\nCustomer {customer_id} not found!")
except Exception as e:
    print(f"\nError: {e}")
