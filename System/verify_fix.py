import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Ticket

t = Ticket.objects.get(ticket_number='TKT-20251111-0017')
print(f"Ticket: {t.ticket_number}")
print(f"Category: {t.category}")
print(f"Priority: {t.priority}")
print(f"Selected at: {t.category_selected_at}")

print("\n" + "="*50)
print("CATEGORY COUNTS")
print("="*50)
print(f"Complaints: {Ticket.objects.filter(category='complaint').count()}")
print(f"Medicine Orders: {Ticket.objects.filter(category='medicine_order').count()}")
print(f"Follow-ups: {Ticket.objects.filter(category='follow_up').count()}")
