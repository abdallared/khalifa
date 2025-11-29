#!/usr/bin/env python
"""
سكريبت لجلب جميع المحادثات من قاعدة البيانات
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Ticket, Message, Customer

def get_all_conversations():
    """جلب جميع المحادثات مع التفاصيل"""
    
    print("=" * 80)
    print("📊 جميع المحادثات (Tickets) في النظام")
    print("=" * 80)
    print()
    
    # جلب جميع التذاكر
    tickets = Ticket.objects.all().select_related('customer', 'assigned_agent', 'current_agent')
    
    print(f"📌 إجمالي عدد المحادثات: {tickets.count()}")
    print()
    
    if tickets.count() == 0:
        print("⚠️ لا توجد محادثات في قاعدة البيانات")
        return
    
    # عرض كل محادثة
    conversations_data = []
    
    for ticket in tickets:
        print(f"{'=' * 80}")
        print(f"🎫 ID: {ticket.id}")
        print(f"📋 رقم التذكرة: {ticket.ticket_number}")
        print(f"👤 العميل: {ticket.customer.name or 'غير محدد'} ({ticket.customer.phone_number})")
        print(f"📞 WhatsApp ID: {ticket.customer.wa_id}")
        print(f"👨‍💼 الموظف المسؤول: {ticket.assigned_agent.full_name if ticket.assigned_agent else 'غير مخصص'}")
        print(f"📊 الحالة: {ticket.status}")
        print(f"🏷️ التصنيف: {ticket.category}")
        print(f"⚡ الأولوية: {ticket.priority}")
        print(f"💬 عدد الرسائل: {ticket.messages_count}")
        print(f"📅 تاريخ الإنشاء: {ticket.created_at}")
        print(f"🕐 آخر رسالة: {ticket.last_message_at or 'لا توجد'}")
        
        if ticket.is_delayed:
            print(f"⏰ متأخرة: نعم ({ticket.total_delay_minutes} دقيقة)")
        
        # جلب الرسائل
        messages = Message.objects.filter(ticket=ticket).order_by('created_at')
        
        print(f"\n💬 الرسائل ({messages.count()}):")
        print("-" * 80)
        
        for i, msg in enumerate(messages, 1):
            sender_name = "العميل" if msg.sender_type == "customer" else (msg.sender.full_name if msg.sender else "النظام")
            direction_icon = "📥" if msg.direction == "incoming" else "📤"
            
            print(f"  {i}. {direction_icon} [{msg.sender_type}] {sender_name}")
            print(f"     📝 النص: {msg.message_text[:100] if msg.message_text else '[ملف مرفق]'}...")
            print(f"     🕐 الوقت: {msg.created_at}")
            print(f"     ✅ الحالة: {msg.delivery_status}")
            
            if msg.media_url:
                print(f"     📎 ملف مرفق: {msg.media_url}")
            print()
        
        # حفظ البيانات للتصدير
        ticket_data = {
            'id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'customer': {
                'id': ticket.customer.id,
                'name': ticket.customer.name,
                'phone': ticket.customer.phone_number,
                'wa_id': ticket.customer.wa_id
            },
            'assigned_agent': ticket.assigned_agent.full_name if ticket.assigned_agent else None,
            'status': ticket.status,
            'category': ticket.category,
            'priority': ticket.priority,
            'messages_count': ticket.messages_count,
            'created_at': str(ticket.created_at),
            'last_message_at': str(ticket.last_message_at) if ticket.last_message_at else None,
            'is_delayed': ticket.is_delayed,
            'messages': [
                {
                    'id': msg.id,
                    'sender_type': msg.sender_type,
                    'sender_name': msg.sender.full_name if msg.sender else None,
                    'direction': msg.direction,
                    'message_text': msg.message_text,
                    'message_type': msg.message_type,
                    'media_url': msg.media_url,
                    'delivery_status': msg.delivery_status,
                    'created_at': str(msg.created_at)
                }
                for msg in messages
            ]
        }
        
        conversations_data.append(ticket_data)
        print()
    
    # حفظ في ملف JSON
    output_file = 'all_conversations_export.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations_data, f, ensure_ascii=False, indent=2)
    
    print("=" * 80)
    print(f"✅ تم حفظ البيانات في: {output_file}")
    print("=" * 80)
    
    return conversations_data


if __name__ == '__main__':
    get_all_conversations()

