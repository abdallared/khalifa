"""
Management command to update delayed tickets status
تحديث حالة التذاكر المتأخرة عندما لا يرد العميل خلال 3 دقائق
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from conversations.models import Ticket, Message, AgentDelayEvent, AgentKPI
from conversations.utils import calculate_agent_kpi


class Command(BaseCommand):
    help = 'Update delayed status for tickets when client does not respond for 3+ minutes'

    def handle(self, *args, **options):
        """
        تحديث حالة التأخير عندما لا يرد العميل خلال 3 دقائق من رد الموظف
        """
        open_tickets = Ticket.objects.filter(status__in=['open'])
        
        updated_count = 0
        newly_delayed = 0
        no_longer_delayed = 0
        
        for ticket in open_tickets:
            old_delayed_status = ticket.is_delayed

            last_agent_msg = Message.objects.filter(
                ticket=ticket,
                sender_type='agent'
            ).order_by('-created_at').first()

            if last_agent_msg:
                last_customer_msg_after_agent = Message.objects.filter(
                    ticket=ticket,
                    sender_type='customer',
                    created_at__gt=last_agent_msg.created_at
                ).order_by('-created_at').first()

                time_since_agent_msg = timezone.now() - last_agent_msg.created_at
                delay_threshold = timedelta(minutes=3)

                if not last_customer_msg_after_agent and time_since_agent_msg > delay_threshold:
                    ticket.is_delayed = True
                    if not old_delayed_status:
                        newly_delayed += 1
                        ticket.delay_started_at = last_agent_msg.created_at
                        ticket.delay_count = (ticket.delay_count or 0) + 1

                        if ticket.assigned_agent:
                            AgentDelayEvent.objects.create(
                                ticket=ticket,
                                agent=ticket.assigned_agent,
                                delay_start_time=last_agent_msg.created_at,
                                reason='العميل لم يرد خلال 3 دقائق من رد الموظف'
                            )
                            
                            today = timezone.now().date()
                            kpi, created = AgentKPI.objects.get_or_create(
                                agent=ticket.assigned_agent,
                                kpi_date=today
                            )
                            kpi.delay_count = (kpi.delay_count or 0) + 1
                            kpi.save()
                else:
                    if last_customer_msg_after_agent:
                        ticket.is_delayed = False
                        if old_delayed_status:
                            no_longer_delayed += 1
                            
                            if ticket.assigned_agent:
                                open_delay_event = AgentDelayEvent.objects.filter(
                                    ticket=ticket,
                                    agent=ticket.assigned_agent,
                                    delay_end_time__isnull=True
                                ).first()
                                if open_delay_event:
                                    open_delay_event.delay_end_time = last_customer_msg_after_agent.created_at
                                    delay_duration = last_customer_msg_after_agent.created_at - open_delay_event.delay_start_time
                                    open_delay_event.delay_duration_seconds = int(delay_duration.total_seconds())
                                    open_delay_event.reason = 'العميل رد على التذكرة'
                                    open_delay_event.save()

            if ticket.is_delayed != old_delayed_status:
                ticket.save()
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ تم تحديث {updated_count} تذكرة\n'
                f'   - {newly_delayed} تذكرة أصبحت متأخرة (العميل لم يرد)\n'
                f'   - {no_longer_delayed} تذكرة لم تعد متأخرة (العميل رد)\n'
                f'   - إجمالي التذاكر المتأخرة: {Ticket.objects.filter(is_delayed=True, status="open").count()}'
            )
        )