#!/usr/bin/env python
"""
سكريبت لحذف محادثات عميل معين
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Ticket, Message, Customer

def delete_customer_conversations(customer_name):
    """حذف جميع محادثات عميل معين"""
    
    print("=" * 80)
    print(f"🗑️ حذف محادثات العميل: {customer_name}")
    print("=" * 80)
    print()
    
    # البحث عن العميل
    customers = Customer.objects.filter(name__icontains=customer_name)
    
    if not customers.exists():
        print(f"❌ لم يتم العثور على عميل باسم: {customer_name}")
        return
    
    print(f"✅ تم العثور على {customers.count()} عميل:")
    print()
    
    total_tickets_deleted = 0
    total_messages_deleted = 0
    
    for customer in customers:
        print(f"👤 العميل: {customer.name}")
        print(f"📞 الهاتف: {customer.phone_number}")
        print(f"🆔 WhatsApp ID: {customer.wa_id}")
        print()
        
        # جلب جميع التذاكر الخاصة بهذا العميل
        tickets = Ticket.objects.filter(customer=customer)
        tickets_count = tickets.count()
        
        print(f"📊 عدد المحادثات: {tickets_count}")
        
        if tickets_count == 0:
            print("⚠️ لا توجد محادثات لهذا العميل")
            continue
        
        # عرض تفاصيل المحادثات قبل الحذف
        print("\n📋 المحادثات التي سيتم حذفها:")
        print("-" * 80)
        
        for ticket in tickets:
            messages_count = Message.objects.filter(ticket=ticket).count()
            print(f"  🎫 ID: {ticket.id} | رقم: {ticket.ticket_number} | الحالة: {ticket.status} | الرسائل: {messages_count}")
            total_messages_deleted += messages_count
        
        print()
        print(f"⚠️ سيتم حذف {tickets_count} محادثة و {total_messages_deleted} رسالة")
        print()

        # حذف مباشرة بدون تأكيد
        print("🗑️ جاري الحذف...")

        # حذف جميع الرسائل أولاً (سيتم حذفها تلقائياً بسبب CASCADE)
        # ثم حذف التذاكر
        deleted_count = tickets.delete()

        print(f"✅ تم حذف {deleted_count[0]} عنصر بنجاح")
        print(f"   - {tickets_count} محادثة")
        print(f"   - {total_messages_deleted} رسالة")

        total_tickets_deleted += tickets_count

        # تحديث عدد التذاكر للعميل
        customer.total_tickets_count = 0
        customer.save()

        print(f"✅ تم تحديث بيانات العميل")
        
        print()
    
    print("=" * 80)
    print(f"✅ انتهت العملية")
    print(f"📊 إجمالي المحادثات المحذوفة: {total_tickets_deleted}")
    print("=" * 80)


if __name__ == '__main__':
    # حذف محادثات Abdallah Reda Elsayed
    delete_customer_conversations("Abdallah Reda Elsayed")

