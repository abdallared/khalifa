import os
import sys
import django
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer, Message, Ticket

# Customers with invalid phone numbers
invalid_customers = [
    {'name': 'عميل 1998', 'bad_phone': '128355097681998'},
    {'name': 'Zeka', 'bad_phone': '2744568045622'},
    {'name': 'Mohmmed Mohsen', 'bad_phone': '59000284524547'},
    {'name': 'عميل 7323', 'bad_phone': '92908883587323'},
    {'name': 'عميل 2689', 'bad_phone': '25516987932689'}
]

print("Searching for real phone numbers in message data...")
print("-" * 80)

for invalid in invalid_customers:
    print(f"\n🔍 Checking: {invalid['name']} (stored as: {invalid['bad_phone']})")
    
    # Get the customer
    try:
        customer = Customer.objects.get(phone_number=invalid['bad_phone'])
        
        # Get their tickets
        tickets = Ticket.objects.filter(customer=customer).order_by('-created_at')
        print(f"  Found {tickets.count()} tickets")
        
        # Check messages for real phone numbers
        for ticket in tickets[:3]:  # Check last 3 tickets
            messages = Message.objects.filter(ticket=ticket).order_by('-created_at')[:5]
            
            for msg in messages:
                # Check if message has raw_data stored
                if msg.whatsapp_message_id:
                    print(f"  Message ID: {msg.whatsapp_message_id}")
                    print(f"  Sender: {msg.sender}")
                    print(f"  Direction: {msg.direction}")
                    
                    # Try to extract phone from sender_id if it's incoming
                    if msg.direction == 'incoming' and msg.sender_id:
                        print(f"  Sender ID: {msg.sender_id}")
                        # Check if sender_id contains a valid phone
                        if '@' in str(msg.sender_id):
                            potential_phone = str(msg.sender_id).split('@')[0]
                            if potential_phone.startswith('20') and len(potential_phone) == 12:
                                print(f"  ✅ FOUND REAL PHONE: {potential_phone}")
                                break
                
                # Check message_text for phone patterns
                if msg.message_text:
                    import re
                    phone_pattern = r'20\d{10}'
                    phones = re.findall(phone_pattern, msg.message_text)
                    if phones:
                        print(f"  📱 Phone in message text: {phones}")
            
    except Customer.DoesNotExist:
        print(f"  ❌ Customer not found with phone: {invalid['bad_phone']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("Checking webhook logs for real phone numbers...")

# Check webhook log for these IDs
try:
    with open('wppconnect-server/webhook.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()[-2000:]  # Last 2000 lines
        
    for invalid in invalid_customers:
        print(f"\n🔍 Searching logs for: {invalid['bad_phone']}")
        found = False
        
        for line in lines:
            if invalid['bad_phone'] in line:
                # Try to find real phone in the same line
                import re
                # Look for Egyptian phone patterns
                phone_pattern = r'"(20\d{10})"'
                phones = re.findall(phone_pattern, line)
                if phones:
                    print(f"  ✅ Found in logs with real phone: {phones[0]}")
                    found = True
                    break
                    
                # Also check for phone in different format
                phone_pattern2 = r'"phone":"(20\d{10})"'
                phones2 = re.findall(phone_pattern2, line)
                if phones2:
                    print(f"  ✅ Found in logs with real phone: {phones2[0]}")
                    found = True
                    break
        
        if not found:
            print(f"  ❌ Not found in recent logs")
            
except FileNotFoundError:
    print("Webhook log file not found")
except Exception as e:
    print(f"Error reading logs: {e}")