"""
Django Signals لتحديث KPIs تلقائياً
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from .models import Ticket, Message, Agent, Customer
from .utils import calculate_agent_kpi

User = get_user_model()


@receiver(post_save, sender=Ticket)
def update_kpi_on_ticket_save(sender, instance, created, **kwargs):
    """
    تحديث KPI عند إنشاء أو تحديث تذكرة
    """
    # تحديث current_active_tickets للموظف
    if instance.current_agent:
        try:
            # حساب عدد التذاكر المفتوحة للموظف
            active_count = Ticket.objects.filter(
                current_agent=instance.current_agent,
                status__in=['open', 'pending', 'in_progress']
            ).count()

            # تحديث current_active_tickets
            Agent.objects.filter(id=instance.current_agent.id).update(
                current_active_tickets=active_count
            )
        except Exception as e:
            pass

    # تحديث total_tickets_count للعميل
    if instance.customer:
        try:
            # حساب إجمالي التذاكر للعميل
            total_count = Ticket.objects.filter(customer=instance.customer).count()

            # تحديث total_tickets_count
            Customer.objects.filter(id=instance.customer.id).update(
                total_tickets_count=total_count
            )
        except Exception as e:
            pass

    # تحديث KPI للموظف المعين
    if instance.assigned_agent:
        try:
            calculate_agent_kpi(instance.assigned_agent)
        except Exception as e:
            # تجاهل الأخطاء لعدم التأثير على العملية الأساسية
            pass


@receiver(post_delete, sender=Ticket)
def update_customer_on_ticket_delete(sender, instance, **kwargs):
    """
    تحديث total_tickets_count عند حذف تذكرة
    """
    if instance.customer:
        try:
            # حساب إجمالي التذاكر للعميل
            total_count = Ticket.objects.filter(customer=instance.customer).count()

            # تحديث total_tickets_count
            Customer.objects.filter(id=instance.customer.id).update(
                total_tickets_count=total_count
            )
        except Exception as e:
            pass


@receiver(post_save, sender=Message)
def update_kpi_on_message_save(sender, instance, created, **kwargs):
    """
    تحديث KPI عند إرسال رسالة من الموظف
    """
    # تحديث last_contact_date للعميل عند أي رسالة جديدة
    if created and instance.ticket and instance.ticket.customer:
        try:
            from django.utils import timezone
            Customer.objects.filter(id=instance.ticket.customer.id).update(
                last_contact_date=timezone.now()
            )
        except Exception as e:
            pass

    # فقط عند إرسال رسالة جديدة من الموظف
    if created and instance.sender_type == 'agent' and instance.ticket.assigned_agent:
        try:
            calculate_agent_kpi(instance.ticket.assigned_agent)
        except Exception as e:
            # تجاهل الأخطاء لعدم التأثير على العملية الأساسية
            pass


@receiver(post_save, sender=User)
def create_agent_profile(sender, instance, created, **kwargs):
    """
    إنشاء سجل Agent تلقائياً عند إنشاء User من نوع agent
    """
    if created and hasattr(instance, 'role') and instance.role == 'agent':
        try:
            Agent.objects.get(user=instance)
        except Agent.DoesNotExist:
            Agent.objects.create(
                user=instance,
                max_capacity=15,
                is_online=False,
                status='offline',
                current_active_tickets=0
            )
