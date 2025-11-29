import os
import sys
import django
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Customer, Message, Ticket

customers_to_check = ['عميل 1998', 'Zeka', 'Mohmmed Mohsen']

print("Checking recent messages for these customers:")
print("-" * 50)

for name in customers_to_check:
    customers = Customer.objects.filter(name=name)
    for customer in customers:
        print(f"\nCustomer: {customer.name}")
        print(f"Stored Phone: {customer.phone_number}")
        print(f"Customer ID: {customer.id}")
        
        # Get tickets for this customer
        tickets = Ticket.objects.filter(customer=customer).order_by('-created_at')[:1]
        for ticket in tickets:
            print(f"Ticket ID: {ticket.id}")
            
            # Get recent messages for this ticket
            messages = Message.objects.filter(ticket=ticket).order_by('-created_at')[:5]
            print(f"Recent messages: {messages.count()}")
            for msg in messages:
                print(f"  - {msg.sender}: {msg.message_text[:50] if msg.message_text else 'No content'}...")
                
        print("-" * 50)