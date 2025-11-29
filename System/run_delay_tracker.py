import os
import django
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Ticket
from conversations.utils import update_ticket_delay_status

def check_and_update_delays():
    open_tickets = Ticket.objects.filter(status='open')
    
    updated_count = 0
    delayed_count = 0
    
    for ticket in open_tickets:
        old_delayed_status = ticket.is_delayed
        update_ticket_delay_status(ticket)
        ticket.refresh_from_db()
        
        if ticket.is_delayed != old_delayed_status:
            updated_count += 1
        
        if ticket.is_delayed:
            delayed_count += 1
    
    return updated_count, delayed_count

if __name__ == '__main__':
    print("✅ Delay Tracker Started - Monitoring ticket delays every 1 minute")
    print("=" * 60)
    
    while True:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated, delayed = check_and_update_delays()
            
            if updated > 0:
                print(f"[{now}] ✅ Updated {updated} tickets | Total delayed: {delayed}")
            else:
                print(f"[{now}] ⏸️  No changes | Total delayed: {delayed}")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {str(e)}")
        
        time.sleep(60)
