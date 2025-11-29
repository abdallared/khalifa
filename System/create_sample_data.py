#!/usr/bin/env python
"""
إنشاء بيانات تجريبية لصفحة التقارير
"""

import os
import sys
import django
import uuid
from datetime import datetime, timedelta

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import *
from conversations.utils import calculate_agent_kpi
from django.utils import timezone

def create_sample_data():
    """إنشاء بيانات تجريبية لليوم"""
    
    print("=== إنشاء بيانات تجريبية لصفحة التقارير ===")
    
    today = timezone.now().date()
    print(f"تاريخ اليوم: {today}")
    
    # الحصول على عميل وموظف
    customer = Customer.objects.first()
    agents = Agent.objects.all()[:3]  # أول 3 موظفين
    
    if not customer:
        print("❌ لا يوجد عملاء في النظام!")
        return
    
    if not agents:
        print("❌ لا يوجد موظفين في النظام!")
        return
    
    print(f"✅ تم العثور على {len(agents)} موظفين")
    
    # إنشاء تذاكر لليوم
    tickets_created = 0
    
    for i, agent in enumerate(agents):
        # إنشاء 3-5 تذاكر لكل موظف
        num_tickets = 3 + i  # agent1: 3, agent2: 4, agent3: 5
        
        for j in range(num_tickets):
            ticket_number = f"TK{today.strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            # تنويع حالات التذاكر
            if j < num_tickets - 1:
                status = 'open'
            else:
                status = 'closed'
                
            # تنويع الأولوية
            priorities = ['low', 'medium', 'high']
            priority = priorities[j % 3]
            
            # تنويع الفئة
            categories = ['general', 'medicine_order', 'complaint', 'consultation']
            category = categories[j % 4]
            
            try:
                ticket = Ticket.objects.create(
                    ticket_number=ticket_number,
                    customer=customer,
                    assigned_agent=agent,
                    current_agent=agent,
                    category=category,
                    priority=priority,
                    status=status,
                    created_at=timezone.now(),
                    last_message_at=timezone.now(),
                )

                tickets_created += 1
                print(f"✅ تم إنشاء التذكرة: {ticket.ticket_number} - {agent.user.username}")

            except Exception as e:
                print(f"❌ خطأ في إنشاء التذكرة: {e}")
    
    print(f"\n📊 تم إنشاء {tickets_created} تذكرة لليوم")
    
    # التحقق من التذاكر المُنشأة
    today_tickets = Ticket.objects.filter(created_at__date=today)
    print(f"📊 إجمالي تذاكر اليوم في قاعدة البيانات: {today_tickets.count()}")
    
    # إعادة حساب مؤشرات الأداء
    print("\n=== إعادة حساب مؤشرات الأداء ===")
    
    # حذف مؤشرات اليوم القديمة
    deleted_count = AgentKPI.objects.filter(kpi_date=today).delete()[0]
    print(f"🗑️ تم حذف {deleted_count} مؤشر قديم")
    
    # حساب مؤشرات جديدة
    for agent in agents:
        try:
            kpi_data = calculate_agent_kpi(agent, today)
            print(f"✅ تم حساب KPI للموظف: {agent.user.username}")
        except Exception as e:
            print(f"❌ خطأ في حساب KPI للموظف {agent.user.username}: {e}")
    
    # عرض النتائج النهائية
    print("\n=== النتائج النهائية ===")
    today_kpis = AgentKPI.objects.filter(kpi_date=today)
    print(f"📊 مؤشرات الأداء لليوم: {today_kpis.count()}")
    
    for kpi in today_kpis:
        print(f"👤 {kpi.agent.user.username}: {kpi.total_tickets} تذاكر, Score: {kpi.overall_kpi_score:.1f}%")
    
    print("\n🎉 تم إنشاء البيانات التجريبية بنجاح!")
    print("🔗 يمكنك الآن فتح صفحة التقارير: http://localhost:8000/admin/reports/")

if __name__ == "__main__":
    create_sample_data()
