"""
Management Command لتحديث جميع الإحصائيات (العملاء، الموظفين، KPIs)
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Max
from django.utils import timezone
from conversations.models import Customer, Agent, Ticket, Message
from conversations.utils import calculate_agent_kpi


class Command(BaseCommand):
    help = 'تحديث جميع الإحصائيات (العملاء، الموظفين، KPIs)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customers',
            action='store_true',
            help='تحديث إحصائيات العملاء فقط',
        )
        parser.add_argument(
            '--agents',
            action='store_true',
            help='تحديث إحصائيات الموظفين فقط',
        )
        parser.add_argument(
            '--kpis',
            action='store_true',
            help='تحديث KPIs فقط',
        )

    def handle(self, *args, **options):
        """
        تحديث جميع الإحصائيات
        """
        # إذا لم يتم تحديد أي خيار، نفذ الكل
        update_all = not (options['customers'] or options['agents'] or options['kpis'])
        
        if options['customers'] or update_all:
            self.update_customers()
        
        if options['agents'] or update_all:
            self.update_agents()
        
        if options['kpis'] or update_all:
            self.update_kpis()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ تم تحديث جميع الإحصائيات بنجاح!')
        )

    def update_customers(self):
        """
        تحديث إحصائيات العملاء
        """
        self.stdout.write('\n📊 تحديث إحصائيات العملاء...')
        
        customers = Customer.objects.all()
        updated_count = 0
        
        for customer in customers:
            # حساب عدد التذاكر
            total_count = Ticket.objects.filter(customer=customer).count()
            
            # آخر تاريخ اتصال (من آخر رسالة)
            last_message = Message.objects.filter(
                ticket__customer=customer
            ).order_by('-created_at').first()
            
            last_contact = last_message.created_at if last_message else customer.last_contact_date
            
            # تحديث البيانات
            customer.total_tickets_count = total_count
            if last_contact:
                customer.last_contact_date = last_contact
            customer.save(update_fields=['total_tickets_count', 'last_contact_date'])
            
            updated_count += 1
            self.stdout.write(
                f'  ✓ {customer.name or customer.phone_number}: {total_count} تذكرة'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✅ تم تحديث {updated_count} عميل')
        )

    def update_agents(self):
        """
        تحديث إحصائيات الموظفين
        """
        self.stdout.write('\n👥 تحديث إحصائيات الموظفين...')
        
        agents = Agent.objects.all()
        updated_count = 0
        
        for agent in agents:
            # حساب عدد التذاكر النشطة
            active_count = Ticket.objects.filter(
                current_agent=agent,
                status__in=['open', 'pending', 'in_progress']
            ).count()
            
            # حساب إجمالي الرسائل المرسلة
            messages_sent = Message.objects.filter(
                ticket__assigned_agent=agent,
                sender_type='agent'
            ).count()
            
            # حساب إجمالي الرسائل المستلمة
            messages_received = Message.objects.filter(
                ticket__assigned_agent=agent,
                sender_type='customer'
            ).count()
            
            # تحديث البيانات
            agent.current_active_tickets = active_count
            agent.total_messages_sent = messages_sent
            agent.total_messages_received = messages_received
            agent.save(update_fields=[
                'current_active_tickets',
                'total_messages_sent',
                'total_messages_received'
            ])
            
            updated_count += 1
            self.stdout.write(
                f'  ✓ {agent.user.full_name}: {active_count} تذكرة نشطة، '
                f'{messages_sent} رسالة مرسلة، {messages_received} رسالة مستلمة'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✅ تم تحديث {updated_count} موظف')
        )

    def update_kpis(self):
        """
        تحديث KPIs لجميع الموظفين
        """
        self.stdout.write('\n📈 تحديث KPIs...')
        
        agents = Agent.objects.all()
        updated_count = 0
        
        for agent in agents:
            try:
                calculate_agent_kpi(agent)
                updated_count += 1
                self.stdout.write(
                    f'  ✓ {agent.user.full_name}: تم تحديث KPI'
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ {agent.user.full_name}: خطأ في تحديث KPI - {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✅ تم تحديث KPI لـ {updated_count} موظف')
        )

