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

# Get the invalid customers
invalid_customers = Customer.objects.filter(
    phone_number__in=['128355097681998', '2744568045622', '59000284524547', '92908883587323', '25516987932689']
)

print("Analyzing message patterns for invalid customers...")
print("=" * 80)

for customer in invalid_customers:
    print(f"\n🔍 Customer: {customer.name}")
    print(f"   Stored Phone: {customer.phone_number}")
    print(f"   Customer ID: {customer.id}")
    
    # Get all tickets
    tickets = Ticket.objects.filter(customer=customer).order_by('-created_at')
    
    for ticket in tickets:
        print(f"\n   📋 Ticket #{ticket.ticket_number} (ID: {ticket.id})")
        
        # Get all messages
        messages = Message.objects.filter(ticket=ticket).order_by('created_at')
        
        print(f"   Messages: {messages.count()}")
        
        for msg in messages[:10]:  # Show first 10 messages
            print(f"\n   Message ID: {msg.id}")
            print(f"   WhatsApp ID: {msg.whatsapp_message_id}")
            print(f"   Direction: {msg.direction}")
            print(f"   Sender: {msg.sender}")
            print(f"   Sender ID: {msg.sender_id}")
            print(f"   Text: {msg.message_text[:100] if msg.message_text else 'None'}")
            
            # The key insight: Check the whatsapp_message_id format
            if msg.whatsapp_message_id and '@lid' in str(msg.whatsapp_message_id):
                # Extract the number before @lid
                lid_part = str(msg.whatsapp_message_id).split('@')[0]
                if '_' in lid_part:
                    parts = lid_part.split('_')
                    if len(parts) > 1:
                        potential_phone = parts[1]
                        print(f"   📱 Extracted from WhatsApp ID: {potential_phone}")
                        
                        # Check if this matches the stored invalid phone
                        if potential_phone == customer.phone_number:
                            print(f"   ⚠️ This IS the stored phone - it's a WhatsApp LID!")
                            print(f"   💡 This means WhatsApp is using Local ID instead of phone number")
                            print(f"   🔴 We need to get the real phone from WhatsApp contact info")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("\nThese customers are using WhatsApp Business API Local IDs (LID) instead of phone numbers.")
print("This happens when:")
print("1. The customer is using WhatsApp Business")
print("2. The customer hasn't shared their phone number")
print("3. The webhook receives a Local ID instead of a phone number")
print("\nSOLUTION: We need to request the real phone number from WhatsApp API using the LID.")