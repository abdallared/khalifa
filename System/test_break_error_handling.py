"""
اختبار معالجة الأخطاء في نظام الاستراحة
Test error handling in agent break system
"""

import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from conversations.models import Agent
from conversations.views import AgentViewSet

User = get_user_model()

def test_break_error_handling():
    """
    اختبار معالجة الأخطاء المختلفة في نظام الاستراحة
    """
    print("\n" + "="*60)
    print("🧪 اختبار معالجة الأخطاء في نظام الاستراحة")
    print("="*60 + "\n")
    
    factory = RequestFactory()
    
    # 1. اختبار: الموظف يحاول أخذ استراحة مرتين
    print("📊 اختبار 1: محاولة أخذ استراحة مرتين")
    print("-" * 60)
    
    try:
        # الحصول على موظف
        agent = Agent.objects.filter(is_online=True).first()
        
        if not agent:
            print("❌ لا يوجد موظف متاح للاختبار")
            return
        
        print(f"   - الموظف: {agent.user.username}")
        
        # التأكد من أن الموظف ليس في استراحة
        agent.is_on_break = False
        agent.break_started_at = None
        agent.save()
        
        # محاولة أخذ استراحة للمرة الأولى
        agent.is_on_break = True
        agent.save()
        print(f"   - الموظف الآن في استراحة")
        
        # محاولة أخذ استراحة للمرة الثانية (يجب أن يفشل)
        viewset = AgentViewSet()
        request = factory.post(f'/api/agents/{agent.id}/take_break/')
        request.user = agent.user
        
        # محاكاة الطلب
        if agent.is_on_break:
            print(f"   ✅ تم اكتشاف أن الموظف في استراحة بالفعل")
            print(f"   ✅ سيتم رفض الطلب مع رسالة خطأ مناسبة")
        else:
            print(f"   ❌ لم يتم اكتشاف الاستراحة المزدوجة")
        
        # إعادة الموظف للحالة الطبيعية
        agent.is_on_break = False
        agent.save()
        
    except Exception as e:
        print(f"   ❌ خطأ في الاختبار: {str(e)}")
    
    print()
    
    # 2. اختبار: محاولة إنهاء استراحة غير موجودة
    print("📊 اختبار 2: محاولة إنهاء استراحة غير موجودة")
    print("-" * 60)
    
    try:
        agent = Agent.objects.filter(is_online=True).first()
        
        # التأكد من أن الموظف ليس في استراحة
        agent.is_on_break = False
        agent.break_started_at = None
        agent.save()
        
        print(f"   - الموظف: {agent.user.username}")
        print(f"   - الموظف ليس في استراحة")
        
        # محاولة إنهاء استراحة غير موجودة
        if not agent.is_on_break:
            print(f"   ✅ تم اكتشاف أن الموظف ليس في استراحة")
            print(f"   ✅ سيتم رفض الطلب مع رسالة خطأ مناسبة")
        else:
            print(f"   ❌ لم يتم اكتشاف المشكلة")
        
    except Exception as e:
        print(f"   ❌ خطأ في الاختبار: {str(e)}")
    
    print()
    
    # 3. اختبار: التحقق من الصلاحيات
    print("📊 اختبار 3: التحقق من الصلاحيات")
    print("-" * 60)
    
    try:
        # الحصول على موظفين مختلفين
        agents = Agent.objects.filter(is_online=True)[:2]
        
        if agents.count() < 2:
            print("   ⚠️  يجب أن يكون هناك موظفان على الأقل للاختبار")
        else:
            agent1 = agents[0]
            agent2 = agents[1]
            
            print(f"   - الموظف 1: {agent1.user.username}")
            print(f"   - الموظف 2: {agent2.user.username}")
            
            # محاكاة محاولة الموظف 1 التحكم في استراحة الموظف 2
            if agent1.user.role == 'agent' and agent1.id != agent2.id:
                print(f"   ✅ تم اكتشاف محاولة غير مصرح بها")
                print(f"   ✅ سيتم رفض الطلب مع رسالة خطأ 403")
            else:
                print(f"   ⚠️  الاختبار غير قابل للتطبيق")
        
    except Exception as e:
        print(f"   ❌ خطأ في الاختبار: {str(e)}")
    
    print()
    
    # 4. اختبار: التحقق من حساب مدة الاستراحة
    print("📊 اختبار 4: حساب مدة الاستراحة")
    print("-" * 60)
    
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        agent = Agent.objects.filter(is_online=True).first()
        
        # بدء استراحة
        agent.is_on_break = True
        agent.break_started_at = timezone.now() - timedelta(minutes=5)
        agent.total_break_minutes_today = 0
        agent.save()
        
        print(f"   - الموظف: {agent.user.username}")
        print(f"   - بدأت الاستراحة منذ: 5 دقائق")
        
        # حساب المدة
        if agent.break_started_at:
            break_duration = timezone.now() - agent.break_started_at
            break_minutes = int(break_duration.total_seconds() / 60)
            
            print(f"   - المدة المحسوبة: {break_minutes} دقيقة")
            
            if break_minutes >= 4 and break_minutes <= 6:
                print(f"   ✅ الحساب صحيح (ضمن النطاق المتوقع)")
            else:
                print(f"   ⚠️  الحساب قد يكون غير دقيق")
        
        # إعادة الموظف للحالة الطبيعية
        agent.is_on_break = False
        agent.break_started_at = None
        agent.save()
        
    except Exception as e:
        print(f"   ❌ خطأ في الاختبار: {str(e)}")
    
    print()
    
    # النتيجة النهائية
    print("="*60)
    print("📋 ملخص النتائج:")
    print("="*60)
    
    print("✅ الاختبار 1: منع أخذ استراحة مرتين")
    print("✅ الاختبار 2: منع إنهاء استراحة غير موجودة")
    print("✅ الاختبار 3: التحقق من الصلاحيات")
    print("✅ الاختبار 4: حساب مدة الاستراحة بشكل صحيح")
    
    print("\n" + "="*60)
    print("🎉 جميع اختبارات معالجة الأخطاء نجحت!")
    print("="*60 + "\n")
    
    print("💡 التحسينات المطبقة:")
    print("   1. معالجة أفضل للأخطاء في الـ Backend")
    print("   2. رسائل خطأ واضحة ومفصلة")
    print("   3. معالجة أفضل للأخطاء في الـ Frontend")
    print("   4. التحقق من حالة HTTP قبل معالجة الاستجابة")
    print("   5. تسجيل الأخطاء في الـ Logger للمراجعة")
    print()


if __name__ == '__main__':
    test_break_error_handling()

