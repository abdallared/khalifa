"""
Management Command لتحديث current_active_tickets لجميع الموظفين
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from conversations.models import Agent, Ticket


class Command(BaseCommand):
    help = 'تحديث current_active_tickets لجميع الموظفين'

    def handle(self, *args, **options):
        """
        تحديث current_active_tickets لجميع الموظفين
        """
        self.stdout.write('بدء تحديث current_active_tickets...')
        
        agents = Agent.objects.all()
        updated_count = 0
        
        for agent in agents:
            # حساب عدد التذاكر المفتوحة
            active_count = Ticket.objects.filter(
                current_agent=agent,
                status__in=['open', 'pending', 'in_progress']
            ).count()
            
            # تحديث current_active_tickets
            agent.current_active_tickets = active_count
            agent.save(update_fields=['current_active_tickets'])
            
            updated_count += 1
            self.stdout.write(
                f'  ✓ {agent.user.full_name}: {active_count} تذكرة نشطة'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ تم تحديث {updated_count} موظف بنجاح!'
            )
        )

