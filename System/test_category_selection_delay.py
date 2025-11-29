"""
اختبار حساب التأخير من وقت اختيار الفئة
Test delay calculation from category selection time
"""

import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from conversations.models import Ticket, Customer, Agent, User
from conversations.utils import check_ticket_delay, handle_menu_selection

def test_category_selection_delay():
    """
    اختبار أن التأخير يُحسب من وقت اختيار الفئة وليس من أول رسالة
    """
    print("\n" + "="*60)
    print("🧪 اختبار حساب التأخير من وقت اختيار الفئة")
    print("="*60 + "\n")
    
    # 1. الحصول على عميل وموظف للاختبار
    try:
        customer = Customer.objects.first()
        agent = Agent.objects.first()
        
        if not customer or not agent:
            print("❌ لا يوجد عملاء أو موظفين في قاعدة البيانات")
            return
        
        print(f"✅ العميل: {customer.name} ({customer.phone_number})")
        print(f"✅ الموظف: {agent.user.username}\n")
        
    except Exception as e:
        print(f"❌ خطأ في جلب البيانات: {str(e)}")
        return
    
    # 2. إنشاء تذكرة جديدة
    try:
        from conversations.utils import generate_ticket_number
        
        ticket_number = generate_ticket_number()
        ticket = Ticket.objects.create(
            ticket_number=ticket_number,
            customer=customer,
            assigned_agent=agent,
            status='open',
            priority='medium',
            category='general',
            created_at=timezone.now() - timedelta(minutes=5),  # منذ 5 دقائق
            last_customer_message_at=timezone.now() - timedelta(minutes=5)
        )
        
        print(f"✅ تم إنشاء تذكرة: {ticket.ticket_number}")
        print(f"   - تم إنشاؤها منذ: 5 دقائق")
        print(f"   - آخر رسالة من العميل: منذ 5 دقائق")
        print(f"   - category_selected_at: {ticket.category_selected_at}\n")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء التذكرة: {str(e)}")
        return
    
    # 3. اختبار التأخير قبل اختيار الفئة
    print("📊 اختبار 1: فحص التأخير قبل اختيار الفئة")
    print("-" * 60)
    
    is_delayed_before = check_ticket_delay(ticket)
    print(f"   - هل التذكرة متأخرة؟ {is_delayed_before}")
    print(f"   - السبب: يستخدم last_customer_message_at (منذ 5 دقائق)")
    print(f"   - النتيجة المتوقعة: True (لأن مر أكثر من 3 دقائق)\n")
    
    # 4. محاكاة اختيار الفئة (الآن)
    print("📊 اختبار 2: محاكاة اختيار العميل للفئة")
    print("-" * 60)
    
    # تحديث category_selected_at إلى الآن
    ticket.category = 'complaint'
    ticket.priority = 'high'
    ticket.category_selected_at = timezone.now()  # الآن
    ticket.save()
    
    print(f"   - العميل اختار: شكوى (complaint)")
    print(f"   - category_selected_at: {ticket.category_selected_at}")
    print(f"   - الوقت الحالي: {timezone.now()}\n")
    
    # 5. اختبار التأخير بعد اختيار الفئة
    print("📊 اختبار 3: فحص التأخير بعد اختيار الفئة")
    print("-" * 60)
    
    is_delayed_after = check_ticket_delay(ticket)
    print(f"   - هل التذكرة متأخرة؟ {is_delayed_after}")
    print(f"   - السبب: يستخدم category_selected_at (الآن)")
    print(f"   - النتيجة المتوقعة: False (لأن لم يمر 3 دقائق بعد)\n")
    
    # 6. محاكاة مرور 4 دقائق
    print("📊 اختبار 4: محاكاة مرور 4 دقائق بعد اختيار الفئة")
    print("-" * 60)
    
    # تحديث category_selected_at إلى منذ 4 دقائق
    ticket.category_selected_at = timezone.now() - timedelta(minutes=4)
    ticket.save()
    
    is_delayed_final = check_ticket_delay(ticket)
    print(f"   - category_selected_at: منذ 4 دقائق")
    print(f"   - هل التذكرة متأخرة؟ {is_delayed_final}")
    print(f"   - النتيجة المتوقعة: True (لأن مر أكثر من 3 دقائق)\n")
    
    # 7. النتيجة النهائية
    print("="*60)
    print("📋 ملخص النتائج:")
    print("="*60)
    
    success = True
    
    if is_delayed_before:
        print("✅ الاختبار 1: نجح - التذكرة متأخرة قبل اختيار الفئة")
    else:
        print("❌ الاختبار 1: فشل - التذكرة يجب أن تكون متأخرة")
        success = False
    
    if not is_delayed_after:
        print("✅ الاختبار 2: نجح - التذكرة ليست متأخرة بعد اختيار الفئة مباشرة")
    else:
        print("❌ الاختبار 2: فشل - التذكرة لا يجب أن تكون متأخرة")
        success = False
    
    if is_delayed_final:
        print("✅ الاختبار 3: نجح - التذكرة متأخرة بعد مرور 4 دقائق")
    else:
        print("❌ الاختبار 3: فشل - التذكرة يجب أن تكون متأخرة")
        success = False
    
    print("\n" + "="*60)
    if success:
        print("🎉 جميع الاختبارات نجحت!")
    else:
        print("⚠️  بعض الاختبارات فشلت")
    print("="*60 + "\n")
    
    # 8. تنظيف - حذف التذكرة التجريبية
    try:
        ticket.delete()
        print("🧹 تم حذف التذكرة التجريبية\n")
    except:
        pass


if __name__ == '__main__':
    # تشغيل الاختبار
    test_category_selection_delay()

