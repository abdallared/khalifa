import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.utils import timezone
from conversations.models import Ticket
from conversations.utils import check_ticket_delay, update_ticket_delay_status

print("=" * 70)
print("Testing Delay Detection Logic")
print("=" * 70)

open_tickets = Ticket.objects.filter(status='open')

print(f"\nFound {open_tickets.count()} open tickets\n")

for ticket in open_tickets:
    print(f"\nTicket #{ticket.ticket_number}")
    print(f"  Customer: {ticket.customer.name or ticket.customer.phone_number}")
    print(f"  Status: {ticket.status}")
    print(f"  Last Customer Message: {ticket.last_customer_message_at}")
    print(f"  Last Agent Message: {ticket.last_agent_message_at}")
    
    if ticket.last_customer_message_at:
        time_diff = timezone.now() - ticket.last_customer_message_at
        minutes = int(time_diff.total_seconds() / 60)
        print(f"  Time since customer message: {minutes} minutes")
    
    if ticket.last_agent_message_at and ticket.last_customer_message_at:
        if ticket.last_agent_message_at > ticket.last_customer_message_at:
            print(f"  ✅ Agent responded AFTER customer")
        else:
            print(f"  ⚠️  Agent did NOT respond yet")
    
    is_delayed = check_ticket_delay(ticket)
    print(f"  Current is_delayed in DB: {ticket.is_delayed}")
    print(f"  Should be delayed (check_ticket_delay): {is_delayed}")
    
    update_ticket_delay_status(ticket)
    ticket.refresh_from_db()
    
    print(f"  ✅ Updated is_delayed to: {ticket.is_delayed}")
    
    if ticket.is_delayed:
        print(f"  🔴 DELAYED TICKET!")

print("\n" + "=" * 70)
print(f"Total delayed tickets: {Ticket.objects.filter(is_delayed=True, status='open').count()}")
print("=" * 70)
