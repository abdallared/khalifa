import os
import django
import codecs

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Ticket, Message

output_file = codecs.open('debug_output.txt', 'w', encoding='utf-8')

def log(msg):
    try:
        print(msg)
    except:
        pass
    output_file.write(msg + '\n')

log("=" * 50)
log("RECENT TICKETS DEBUG")
log("=" * 50)

tickets = Ticket.objects.order_by('-created_at')[:5]

for ticket in tickets:
    customer_messages = Message.objects.filter(
        ticket=ticket,
        sender_type='customer'
    ).count()
    
    all_messages = Message.objects.filter(ticket=ticket).count()
    
    log(f"\nTicket: {ticket.ticket_number}")
    log(f"  Customer: {ticket.customer.phone_number}")
    log(f"  Category: {ticket.category}")
    log(f"  Category Selected At: {ticket.category_selected_at}")
    log(f"  Status: {ticket.status}")
    log(f"  Customer Messages: {customer_messages}")
    log(f"  Total Messages: {all_messages}")
    
    if customer_messages > 0:
        msgs = Message.objects.filter(
            ticket=ticket,
            sender_type='customer'
        ).order_by('created_at')[:3]
        log(f"  First customer messages:")
        for i, msg in enumerate(msgs, 1):
            text = msg.message_text[:50] if msg.message_text else '(empty)'
            log(f"    {i}. {text}")

log("\n" + "=" * 50)
log("CATEGORY COUNTS")
log("=" * 50)
log(f"Complaints: {Ticket.objects.filter(category='complaint').count()}")
log(f"Medicine Orders: {Ticket.objects.filter(category='medicine_order').count()}")
log(f"Follow-ups: {Ticket.objects.filter(category='follow_up').count()}")
log(f"General: {Ticket.objects.filter(category='general').count()}")
log(f"Total: {Ticket.objects.count()}")

output_file.close()
log("Debug output saved to debug_output.txt")
