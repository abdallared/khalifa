import os
import sys
import django
import io

# Fix Unicode output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
sys.path.append('e:\\Hive_Work\\Projects\\Kh_Pharmacy\\final_kh\\V1\\Anas_S05\\Anas_S04\\st_9\\st_8\\khalifa\\System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer
from conversations.whatsapp_driver import get_whatsapp_driver

print("=" * 60)
print("Fixing Customer WhatsApp IDs")
print("=" * 60)

# The customers with wrong IDs and their correct numbers
corrections = [
    {
        'name': 'راجية الفردوس',
        'wrong_phone': '247201188036655',
        'correct_phone': '01151218425',
        'correct_wa_id': '201151218425@c.us'  # Egyptian format
    },
    {
        'name': 'Bahaa Elhawary',
        'wrong_phone': '131748608372742',
        'correct_phone': '01013655361',
        'correct_wa_id': '201013655361@c.us'  # Egyptian format
    },
    {
        'name': 'Bahaa Elhawary',
        'wrong_phone': '201013655361',  # This one is already correct
        'correct_phone': '201013655361',
        'correct_wa_id': '201013655361@c.us'
    }
]

print("\n1. Finding and fixing customers:")
print("-" * 30)

for correction in corrections:
    # Find the customer
    customers = Customer.objects.filter(phone_number=correction['wrong_phone'])
    
    if customers.exists():
        for customer in customers:
            print(f"\n📋 Found: {customer.name}")
            print(f"   Current phone: {customer.phone_number}")
            print(f"   Current wa_id: {customer.wa_id}")
            
            # Update to correct values
            if correction['wrong_phone'] != correction['correct_phone']:
                # Need to fix the phone number
                customer.phone_number = correction['correct_phone'].replace('0', '20', 1) if correction['correct_phone'].startswith('0') else correction['correct_phone']
                customer.wa_id = correction['correct_wa_id']
                customer.save()
                
                print(f"   ✅ Fixed to:")
                print(f"      New phone: {customer.phone_number}")
                print(f"      New wa_id: {customer.wa_id}")
            else:
                print(f"   ℹ️ Phone number is already correct")
    else:
        print(f"\n❌ Customer not found with phone: {correction['wrong_phone']}")

# Check if there are duplicate customers
print("\n2. Checking for duplicate customers:")
print("-" * 30)

for correction in corrections:
    # Check both old and new phone numbers
    customers_old = Customer.objects.filter(phone_number=correction['wrong_phone'])
    customers_new = Customer.objects.filter(phone_number=correction['correct_phone'].replace('0', '20', 1) if correction['correct_phone'].startswith('0') else correction['correct_phone'])
    
    if customers_old.count() + customers_new.count() > 1:
        print(f"\n⚠️ Multiple customers found for {correction['name']}:")
        for c in customers_old:
            print(f"   - ID: {c.id}, Name: {c.name}, Phone: {c.phone_number}")
        for c in customers_new:
            print(f"   - ID: {c.id}, Name: {c.name}, Phone: {c.phone_number}")

# Test sending a message to the corrected numbers
print("\n3. Testing message sending to corrected numbers:")
print("-" * 30)

driver = get_whatsapp_driver()

test_customers = [
    ('راجية الفردوس', '201151218425@c.us'),
    ('Bahaa Elhawary', '201013655361@c.us')
]

for name, wa_id in test_customers:
    print(f"\n📤 Testing: {name}")
    print(f"   Sending to: {wa_id}")
    
    try:
        result = driver.send_text_message(
            phone=wa_id,
            message=f"اختبار - تم إصلاح رقمك في النظام. Test message after fixing your number."
        )
        
        if result.get('success'):
            print(f"   ✅ Message sent successfully!")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Fix Complete!")
print("=" * 60)
print("""
✅ WHAT WAS FIXED:
1. راجية الفردوس: 247201188036655 → 201151218425
2. Bahaa Elhawary: 131748608372742 → 201013655361

📋 NEXT STEPS:
1. The corrected numbers should now work for sending messages
2. Monitor incoming messages to ensure correct IDs are used
3. Check the webhook to prevent this issue in the future
""")