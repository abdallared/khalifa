#!/usr/bin/env python
"""
فحص البيانات في قاعدة البيانات
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import *
from django.utils import timezone

def check_data():
    """فحص البيانات الموجودة"""
    
    print("=== فحص البيانات في قاعدة البيانات ===")
    
    today = timezone.now().date()
    print(f"تاريخ اليوم: {today}")
    
    # فحص إجمالي البيانات
    print(f"\n📊 إجمالي البيانات:")
    print(f"- التذاكر: {Ticket.objects.count()}")
    print(f"- العملاء: {Customer.objects.count()}")
    print(f"- الموظفين: {Agent.objects.count()}")
    print(f"- مؤشرات الأداء: {AgentKPI.objects.count()}")
    
    # فحص التذاكر لليوم
    today_tickets = Ticket.objects.filter(created_at__date=today)
    print(f"\n📅 تذاكر اليوم ({today}):")
    print(f"- العدد: {today_tickets.count()}")

    # فحص بطريقة أخرى
    from datetime import datetime
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    today_tickets_alt = Ticket.objects.filter(created_at__gte=today_start, created_at__lte=today_end)
    print(f"- العدد (طريقة بديلة): {today_tickets_alt.count()}")

    if today_tickets_alt.exists():
        print("- التفاصيل:")
        for ticket in today_tickets_alt[:5]:  # أول 5 تذاكر
            print(f"  • {ticket.ticket_number} - {ticket.status} - {ticket.assigned_agent.user.username if ticket.assigned_agent else 'غير محدد'}")
            print(f"    تاريخ الإنشاء: {ticket.created_at}")
    
    # فحص آخر التذاكر
    latest_tickets = Ticket.objects.order_by('-created_at')[:5]
    print(f"\n🕒 آخر 5 تذاكر:")
    for ticket in latest_tickets:
        print(f"- {ticket.ticket_number} - {ticket.created_at.date()} - {ticket.status}")
    
    # فحص مؤشرات الأداء لليوم
    today_kpis = AgentKPI.objects.filter(kpi_date=today)
    print(f"\n📈 مؤشرات الأداء لليوم:")
    print(f"- العدد: {today_kpis.count()}")
    
    if today_kpis.exists():
        print("- التفاصيل:")
        for kpi in today_kpis:
            print(f"  • {kpi.agent.user.username}: {kpi.total_tickets} تذاكر, Score: {kpi.overall_kpi_score:.1f}%")
    
    # فحص آخر مؤشرات
    latest_kpis = AgentKPI.objects.order_by('-kpi_date')[:5]
    print(f"\n🕒 آخر 5 مؤشرات أداء:")
    for kpi in latest_kpis:
        print(f"- {kpi.agent.user.username}: {kpi.kpi_date} - {kpi.total_tickets} تذاكر")

if __name__ == "__main__":
    check_data()
