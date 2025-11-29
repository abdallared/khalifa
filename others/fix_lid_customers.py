import os
import sys
import django
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer

# These are WhatsApp LIDs, not phone numbers
lid_customers = [
    {'lid': '128355097681998', 'name': 'عميل 1998'},
    {'lid': '2744568045622', 'name': 'Zeka'},
    {'lid': '59000284524547', 'name': 'Mohmmed Mohsen'},
    {'lid': '92908883587323', 'name': 'عميل 7323'},
    {'lid': '25516987932689', 'name': 'عميل 2689'}
]

print("Fixing WhatsApp LID customers...")
print("-" * 80)

for item in lid_customers:
    try:
        customer = Customer.objects.get(phone_number=item['lid'])
        
        # Update the name to indicate it's a LID user
        old_name = customer.name
        if old_name.startswith('[INVALID PHONE]'):
            # Remove the invalid phone prefix and add LID prefix
            new_name = old_name.replace('[INVALID PHONE] ', '')
            new_name = f'[WhatsApp LID] {new_name}'
        else:
            new_name = f'[WhatsApp LID] {customer.name}'
        
        # Update wa_id to use @lid format
        customer.wa_id = f"{item['lid']}@lid"
        customer.name = new_name
        customer.save()
        
        print(f"✅ Updated: {old_name} -> {new_name}")
        print(f"   LID: {item['lid']}")
        print(f"   wa_id: {customer.wa_id}")
        
    except Customer.DoesNotExist:
        print(f"❌ Customer not found with LID: {item['lid']}")

print("-" * 80)
print("Done! These customers are now properly marked as WhatsApp LID users.")
print("\nNote: WhatsApp LID users don't share their phone numbers.")
print("We can still send and receive messages using their LID.")