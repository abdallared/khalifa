"""
اختبار تأثير وقت الاستراحة على KPI

هذا السكريبت يختبر:
1. إنشاء جلسة استراحة
2. حساب KPI مع وقت الاستراحة
3. عرض التقرير
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.utils import timezone
from conversations.models import Agent, AgentBreakSession, AgentKPI
from conversations.utils import calculate_agent_kpi


def test_break_kpi():
    """
    اختبار حساب KPI مع وقت الاستراحة
    """
    print("=" * 80)
    print("🧪 اختبار تأثير وقت الاستراحة على KPI")
    print("=" * 80)
    print()
    
    # 1. الحصول على أول موظف
    try:
        agent = Agent.objects.first()
        if not agent:
            print("❌ لا يوجد موظفين في النظام")
            return
        
        print(f"✅ الموظف: {agent.user.full_name}")
        print(f"   ID: {agent.id}")
        print()
        
    except Exception as e:
        print(f"❌ خطأ في الحصول على الموظف: {e}")
        return
    
    # 2. إنشاء جلسات استراحة تجريبية
    print("📝 إنشاء جلسات استراحة تجريبية...")
    print()
    
    today = timezone.now().date()
    
    # جلسة استراحة 1: 15 دقيقة
    break1_start = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
    break1_end = break1_start + timedelta(minutes=15)
    
    session1, created1 = AgentBreakSession.objects.get_or_create(
        agent=agent,
        break_start_time=break1_start,
        defaults={
            'break_end_time': break1_end,
            'break_duration_seconds': 15 * 60
        }
    )
    
    if created1:
        print(f"✅ جلسة استراحة 1:")
        print(f"   البداية: {break1_start.strftime('%H:%M')}")
        print(f"   النهاية: {break1_end.strftime('%H:%M')}")
        print(f"   المدة: 15 دقيقة")
        print()
    else:
        print(f"ℹ️  جلسة استراحة 1 موجودة بالفعل")
        print()
    
    # جلسة استراحة 2: 20 دقيقة
    break2_start = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0)
    break2_end = break2_start + timedelta(minutes=20)
    
    session2, created2 = AgentBreakSession.objects.get_or_create(
        agent=agent,
        break_start_time=break2_start,
        defaults={
            'break_end_time': break2_end,
            'break_duration_seconds': 20 * 60
        }
    )
    
    if created2:
        print(f"✅ جلسة استراحة 2:")
        print(f"   البداية: {break2_start.strftime('%H:%M')}")
        print(f"   النهاية: {break2_end.strftime('%H:%M')}")
        print(f"   المدة: 20 دقيقة")
        print()
    else:
        print(f"ℹ️  جلسة استراحة 2 موجودة بالفعل")
        print()
    
    # 3. حساب KPI
    print("📊 حساب KPI...")
    print()
    
    try:
        kpi_data = calculate_agent_kpi(agent, today)
        
        print("=" * 80)
        print("📈 نتائج KPI")
        print("=" * 80)
        print()
        
        print(f"📅 التاريخ: {today}")
        print()
        
        print("📊 المؤشرات الأساسية:")
        print(f"   • إجمالي التذاكر: {kpi_data['total_tickets']}")
        print(f"   • التذاكر المغلقة: {kpi_data['closed_tickets']}")
        print(f"   • متوسط وقت الاستجابة: {kpi_data['avg_response_time_seconds']} ثانية ({kpi_data['avg_response_time_seconds'] // 60} دقيقة)")
        print(f"   • الرسائل المرسلة: {kpi_data['messages_sent']}")
        print(f"   • الرسائل المستلمة: {kpi_data['messages_received']}")
        print(f"   • عدد التأخيرات: {kpi_data['delay_count']}")
        print()
        
        print("⏸️  مؤشرات الاستراحة:")
        total_break_minutes = kpi_data['total_break_time_seconds'] // 60
        print(f"   • إجمالي وقت الاستراحة: {kpi_data['total_break_time_seconds']} ثانية ({total_break_minutes} دقيقة)")
        print(f"   • عدد مرات الاستراحة: {kpi_data['break_count']}")
        print()
        
        print("🎯 معدلات الأداء:")
        print(f"   • معدل الرد الأول: {kpi_data['first_response_rate']:.2f}%")
        print(f"   • معدل الحل: {kpi_data['resolution_rate']:.2f}%")
        print(f"   • رضا العملاء: {kpi_data['customer_satisfaction_score']:.2f}/5")
        print(f"   • KPI Score الإجمالي: {kpi_data['overall_kpi_score']:.2f}")
        print()
        
        # 4. عرض جلسات الاستراحة
        print("=" * 80)
        print("📋 جلسات الاستراحة اليوم")
        print("=" * 80)
        print()
        
        break_sessions = AgentBreakSession.objects.filter(
            agent=agent,
            break_start_time__date=today
        ).order_by('break_start_time')
        
        if break_sessions.exists():
            for i, session in enumerate(break_sessions, 1):
                duration_minutes = session.break_duration_seconds // 60 if session.break_duration_seconds else 0
                print(f"جلسة {i}:")
                print(f"   البداية: {session.break_start_time.strftime('%H:%M:%S')}")
                if session.break_end_time:
                    print(f"   النهاية: {session.break_end_time.strftime('%H:%M:%S')}")
                    print(f"   المدة: {duration_minutes} دقيقة")
                else:
                    print(f"   النهاية: جارية...")
                print()
        else:
            print("ℹ️  لا توجد جلسات استراحة اليوم")
            print()
        
        # 5. التحليل
        print("=" * 80)
        print("🔍 التحليل")
        print("=" * 80)
        print()
        
        if kpi_data['total_break_time_seconds'] > 0:
            print("✅ وقت الاستراحة يتم تتبعه بنجاح!")
            print()
            print("📌 ملاحظات:")
            print(f"   • الموظف أخذ {kpi_data['break_count']} استراحة اليوم")
            print(f"   • إجمالي وقت الاستراحة: {total_break_minutes} دقيقة")
            print()
            
            if kpi_data['avg_response_time_seconds'] > 0:
                break_percentage = (kpi_data['total_break_time_seconds'] / kpi_data['avg_response_time_seconds']) * 100
                print(f"   • نسبة وقت الاستراحة من متوسط وقت الاستجابة: {break_percentage:.1f}%")
                print()
            
            print("⚠️  التأثير على الأداء:")
            print("   • وقت الاستراحة محسوب ضمن Response Time للتذاكر")
            print("   • كلما زاد وقت الاستراحة، زاد متوسط وقت الاستجابة")
            print("   • هذا يؤثر سلباً على First Response Rate و Overall KPI Score")
            print()
        else:
            print("ℹ️  لا يوجد وقت استراحة مسجل اليوم")
            print()
        
        print("=" * 80)
        print("✅ الاختبار اكتمل بنجاح!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ خطأ في حساب KPI: {e}")
        import traceback
        traceback.print_exc()


def view_all_agents_kpi():
    """
    عرض KPI لجميع الموظفين
    """
    print()
    print("=" * 80)
    print("📊 KPI جميع الموظفين")
    print("=" * 80)
    print()
    
    today = timezone.now().date()
    
    kpis = AgentKPI.objects.filter(kpi_date=today).select_related('agent__user')
    
    if not kpis.exists():
        print("ℹ️  لا توجد بيانات KPI اليوم")
        return
    
    for kpi in kpis:
        print(f"👤 {kpi.agent.user.full_name}")
        print(f"   التذاكر: {kpi.total_tickets} | المغلقة: {kpi.closed_tickets}")
        print(f"   متوسط الاستجابة: {kpi.avg_response_time_seconds // 60} دقيقة")
        print(f"   وقت الاستراحة: {kpi.total_break_time_seconds // 60} دقيقة ({kpi.break_count} مرة)")
        print(f"   KPI Score: {kpi.overall_kpi_score:.2f}")
        print()


if __name__ == '__main__':
    test_break_kpi()
    view_all_agents_kpi()

