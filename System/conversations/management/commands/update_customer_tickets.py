"""
Management Command لتحديث total_tickets_count لجميع العملاء
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from conversations.models import Customer, Ticket


class Command(BaseCommand):
    help = 'تحديث total_tickets_count لجميع العملاء'

    def handle(self, *args, **options):
        """
        تحديث total_tickets_count لجميع العملاء
        """
        self.stdout.write('بدء تحديث total_tickets_count للعملاء...')
        
        customers = Customer.objects.all()
        updated_count = 0
        
        for customer in customers:
            # حساب عدد التذاكر
            total_count = Ticket.objects.filter(customer=customer).count()
            
            # تحديث total_tickets_count
            customer.total_tickets_count = total_count
            customer.save(update_fields=['total_tickets_count'])
            
            updated_count += 1
            self.stdout.write(
                f'  ✓ {customer.name or customer.phone_number}: {total_count} تذكرة'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ تم تحديث {updated_count} عميل بنجاح!'
            )
        )

