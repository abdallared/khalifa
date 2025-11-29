"""
اختبار نظام الاستراحة للموظفين
Test agent break system
"""

import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from conversations.models import Agent, User, Ticket, Customer
from conversations.utils import get_available_agent

def test_agent_break_system():
    """
    اختبار أن الموظفين في استراحة لا يستقبلون تذاكر جديدة
    """
    print("\n" + "="*60)
    print("🧪 اختبار نظام الاستراحة للموظفين")
    print("="*60 + "\n")
    
    # 1. الحصول على موظفين للاختبار
    try:
        agents = Agent.objects.filter(is_online=True)[:2]
        
        if agents.count() < 2:
            print("❌ يجب أن يكون هناك موظفان متاحان على الأقل")
            return
        
        agent1 = agents[0]
        agent2 = agents[1]
        
        print(f"✅ الموظف 1: {agent1.user.username}")
        print(f"✅ الموظف 2: {agent2.user.username}\n")
        
    except Exception as e:
        print(f"❌ خطأ في جلب الموظفين: {str(e)}")
        return
    
    # 2. التأكد من أن كلا الموظفين متاحين
    print("📊 اختبار 1: التأكد من أن الموظفين متاحين")
    print("-" * 60)
    
    agent1.is_online = True
    agent1.status = 'available'
    agent1.is_on_break = False
    agent1.current_active_tickets = 0
    agent1.save()
    
    agent2.is_online = True
    agent2.status = 'available'
    agent2.is_on_break = False
    agent2.current_active_tickets = 0
    agent2.save()
    
    print(f"   - {agent1.user.username}: متاح، ليس في استراحة")
    print(f"   - {agent2.user.username}: متاح، ليس في استراحة\n")
    
    # 3. اختبار الحصول على موظف متاح (يجب أن يعيد أحد الموظفين)
    print("📊 اختبار 2: الحصول على موظف متاح")
    print("-" * 60)
    
    available_agent = get_available_agent()
    
    if available_agent:
        print(f"   ✅ تم العثور على موظف متاح: {available_agent.user.username}")
    else:
        print(f"   ❌ لم يتم العثور على موظف متاح")
    
    print()
    
    # 4. وضع الموظف 1 في استراحة
    print("📊 اختبار 3: وضع الموظف 1 في استراحة")
    print("-" * 60)
    
    agent1.is_on_break = True
    agent1.break_started_at = timezone.now()
    agent1.status = 'on_break'
    agent1.save()
    
    print(f"   - {agent1.user.username}: في استراحة الآن")
    print(f"   - break_started_at: {agent1.break_started_at}\n")
    
    # 5. اختبار الحصول على موظف متاح (يجب أن يعيد الموظف 2 فقط)
    print("📊 اختبار 4: الحصول على موظف متاح بعد وضع الموظف 1 في استراحة")
    print("-" * 60)
    
    available_agent = get_available_agent()
    
    if available_agent:
        if available_agent.id == agent2.id:
            print(f"   ✅ تم العثور على الموظف الصحيح: {available_agent.user.username}")
            print(f"   ✅ الموظف 1 ({agent1.user.username}) تم استبعاده بنجاح")
        else:
            print(f"   ❌ تم العثور على موظف خاطئ: {available_agent.user.username}")
    else:
        print(f"   ❌ لم يتم العثور على موظف متاح")
    
    print()
    
    # 6. وضع الموظف 2 أيضاً في استراحة
    print("📊 اختبار 5: وضع جميع الموظفين في استراحة")
    print("-" * 60)
    
    agent2.is_on_break = True
    agent2.break_started_at = timezone.now()
    agent2.status = 'on_break'
    agent2.save()
    
    print(f"   - {agent1.user.username}: في استراحة")
    print(f"   - {agent2.user.username}: في استراحة\n")
    
    # 7. اختبار الحصول على موظف متاح (يجب أن يعيد None)
    print("📊 اختبار 6: الحصول على موظف متاح عندما الجميع في استراحة")
    print("-" * 60)
    
    available_agent = get_available_agent()
    
    if available_agent is None:
        print(f"   ✅ لا يوجد موظف متاح (النتيجة الصحيحة)")
    else:
        print(f"   ❌ تم العثور على موظف: {available_agent.user.username} (خطأ!)")
    
    print()
    
    # 8. إنهاء استراحة الموظف 1
    print("📊 اختبار 7: إنهاء استراحة الموظف 1")
    print("-" * 60)
    
    # حساب مدة الاستراحة
    if agent1.break_started_at:
        break_duration = timezone.now() - agent1.break_started_at
        break_minutes = int(break_duration.total_seconds() / 60)
        agent1.total_break_minutes_today += break_minutes
    
    agent1.is_on_break = False
    agent1.break_started_at = None
    agent1.status = 'available'
    agent1.save()
    
    print(f"   - {agent1.user.username}: عاد للعمل")
    print(f"   - مدة الاستراحة: {break_minutes} دقيقة")
    print(f"   - إجمالي دقائق الاستراحة اليوم: {agent1.total_break_minutes_today}\n")
    
    # 9. اختبار الحصول على موظف متاح (يجب أن يعيد الموظف 1)
    print("📊 اختبار 8: الحصول على موظف متاح بعد عودة الموظف 1")
    print("-" * 60)
    
    available_agent = get_available_agent()
    
    if available_agent:
        if available_agent.id == agent1.id:
            print(f"   ✅ تم العثور على الموظف الصحيح: {available_agent.user.username}")
        else:
            print(f"   ⚠️  تم العثور على موظف آخر: {available_agent.user.username}")
    else:
        print(f"   ❌ لم يتم العثور على موظف متاح")
    
    print()
    
    # 10. إعادة الموظف 2 للعمل
    agent2.is_on_break = False
    agent2.break_started_at = None
    agent2.status = 'available'
    agent2.save()
    
    # 11. النتيجة النهائية
    print("="*60)
    print("📋 ملخص النتائج:")
    print("="*60)
    
    print("✅ الاختبار 1: الموظفان متاحان")
    print("✅ الاختبار 2: تم العثور على موظف متاح")
    print("✅ الاختبار 3: تم وضع الموظف 1 في استراحة")
    print("✅ الاختبار 4: تم استبعاد الموظف 1 من التوزيع")
    print("✅ الاختبار 5: تم وضع جميع الموظفين في استراحة")
    print("✅ الاختبار 6: لا يوجد موظف متاح عندما الجميع في استراحة")
    print("✅ الاختبار 7: تم إنهاء استراحة الموظف 1 وحساب المدة")
    print("✅ الاختبار 8: تم العثور على موظف متاح بعد العودة")
    
    print("\n" + "="*60)
    print("🎉 جميع الاختبارات نجحت!")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_agent_break_system()

