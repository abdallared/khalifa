import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Ticket, Message, Customer
from conversations.utils import handle_menu_selection

# Get the most recent ticket
ticket = Ticket.objects.order_by('-created_at').first()

print(f"Testing ticket: {ticket.ticket_number}")
print(f"Current category: {ticket.category}")
print(f"Category selected at: {ticket.category_selected_at}")

# Get customer
customer = ticket.customer
print(f"Customer: {customer.phone_number}")

# Get messages
messages = Message.objects.filter(ticket=ticket, sender_type='customer').order_by('created_at')
print(f"\nCustomer messages ({messages.count()}):")
for i, msg in enumerate(messages, 1):
    try:
        print(f"  {i}. {msg.message_text}")
    except:
        print(f"  {i}. (message with encoding issue)")

# Test menu selection with "2"
print("\n" + "="*50)
print("Testing handle_menu_selection with '2':")
print("="*50)

result = handle_menu_selection(customer, '2', ticket)
print(f"Result: {result}")

# Refresh ticket from DB
ticket.refresh_from_db()
print(f"\nAfter handle_menu_selection:")
print(f"  Category: {ticket.category}")
print(f"  Priority: {ticket.priority}")
print(f"  Category selected at: {ticket.category_selected_at}")
