"""
Test script for WhatsApp audio message handling
تجربة استقبال وعرض الرسائل الصوتية من WhatsApp
"""

import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Message, Ticket, Customer
from django.utils import timezone

def test_audio_message():
    """
    إنشاء رسالة صوتية تجريبية للاختبار
    """
    print("🎤 Testing Audio Message Support...")
    
    # الحصول على أول عميل وتذكرة
    customer = Customer.objects.first()
    if not customer:
        print("❌ No customers found. Please create a customer first.")
        return
    
    ticket = Ticket.objects.filter(customer=customer).first()
    if not ticket:
        print("❌ No tickets found for customer. Please create a ticket first.")
        return
    
    # إنشاء رسالة صوتية تجريبية
    audio_message = Message.objects.create(
        ticket=ticket,
        sender=None,  # من العميل
        sender_type='customer',
        direction='incoming',
        message_text='رسالة صوتية',  # وصف اختياري
        message_type='audio',
        media_url='/uploads/test_audio.ogg',  # مسار ملف صوتي تجريبي
        mime_type='audio/ogg',
        whatsapp_message_id=f'test_audio_{timezone.now().timestamp()}',
        delivery_status='delivered'
    )
    
    print(f"✅ Audio message created: ID={audio_message.id}")
    print(f"   Type: {audio_message.message_type}")
    print(f"   Media URL: {audio_message.media_url}")
    print(f"   MIME Type: {audio_message.mime_type}")
    
    # إنشاء رسائل أخرى للاختبار
    test_messages = [
        {
            'message_type': 'document',
            'media_url': '/uploads/test_document.pdf',
            'mime_type': 'application/pdf',
            'message_text': 'وثيقة مهمة.pdf'
        },
        {
            'message_type': 'video',
            'media_url': '/uploads/test_video.mp4',
            'mime_type': 'video/mp4',
            'message_text': 'فيديو توضيحي'
        }
    ]
    
    for msg_data in test_messages:
        msg = Message.objects.create(
            ticket=ticket,
            sender=None,
            sender_type='customer',
            direction='incoming',
            whatsapp_message_id=f"test_{msg_data['message_type']}_{timezone.now().timestamp()}",
            delivery_status='delivered',
            **msg_data
        )
        print(f"✅ {msg_data['message_type'].title()} message created: ID={msg.id}")
    
    print("\n📊 Summary:")
    print(f"   Customer: {customer.name} ({customer.phone_number})")
    print(f"   Ticket: {ticket.ticket_number}")
    print(f"   Total messages in ticket: {ticket.messages.count()}")
    
    # عرض آخر 5 رسائل
    print("\n📨 Last 5 messages:")
    for msg in ticket.messages.order_by('-created_at')[:5]:
        print(f"   - {msg.message_type}: {msg.message_text or 'No text'} ({msg.created_at.strftime('%H:%M')})")
        if msg.media_url:
            print(f"     Media: {msg.media_url}")

def check_audio_support():
    """
    التحقق من دعم الملفات الصوتية في النظام
    """
    print("\n🔍 Checking Audio Support in Database...")
    
    # التحقق من الرسائل الصوتية الموجودة
    audio_messages = Message.objects.filter(message_type='audio')
    print(f"   Found {audio_messages.count()} audio messages")
    
    if audio_messages.exists():
        print("\n   Sample audio messages:")
        for msg in audio_messages[:3]:
            print(f"   - Ticket: {msg.ticket.ticket_number}")
            print(f"     URL: {msg.media_url}")
            print(f"     MIME: {msg.mime_type}")
            print(f"     Status: {msg.delivery_status}")
            print()
    
    # التحقق من أنواع الرسائل المدعومة
    print("\n📋 Supported message types:")
    for choice in Message.MESSAGE_TYPE_CHOICES:
        count = Message.objects.filter(message_type=choice[0]).count()
        print(f"   - {choice[1]}: {count} messages")

if __name__ == '__main__':
    print("=" * 50)
    print("WhatsApp Audio Message Test")
    print("=" * 50)
    
    # التحقق من الدعم الحالي
    check_audio_support()
    
    # إنشاء رسالة صوتية تجريبية
    print("\n" + "=" * 50)
    response = input("\n❓ Do you want to create test audio messages? (y/n): ")
    if response.lower() == 'y':
        test_audio_message()
    
    print("\n✅ Test completed!")
    print("\n📌 Next steps:")
    print("1. Open the conversation interface in your browser")
    print("2. Select a customer with audio messages")
    print("3. Verify that audio players appear for audio messages")
    print("4. Test playback functionality")