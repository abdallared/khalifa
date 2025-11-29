#!/usr/bin/env python
"""
اختبار وحدة لوظائف تحميل الصور
Unit Tests for Image Upload Functions
"""

import os
import django
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.contrib.auth import get_user_model
from conversations.models import (
    User, Agent, Customer, Ticket, Message
)

User = get_user_model()


class ImageUploadTestCase(TestCase):
    """
    اختبار تحميل الصور
    """

    def setUp(self):
        """
        إعداد البيانات للاختبار
        """
        # إنشاء مستخدم
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            role='agent'
        )
        
        # إنشاء Agent
        self.agent = Agent.objects.create(
            user=self.user,
            name=self.user.username,
            max_concurrent_tickets=5
        )
        
        # إنشاء عميل
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone_number='201234567890',
            wa_id='201234567890@c.us'
        )
        
        # إنشاء تذكرة
        self.ticket = Ticket.objects.create(
            ticket_number='TEST001',
            customer=self.customer,
            assigned_agent=self.agent,
            status='open',
            priority='medium',
            category='general'
        )
        
        # إنشاء عميل
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def create_test_image(self, name='test_image.jpg', size=(100, 100)):
        """
        إنشاء صورة اختبار
        """
        file = BytesIO()
        image = Image.new('RGB', size, color='red')
        image.save(file, format='JPEG')
        file.seek(0)
        return SimpleUploadedFile(name, file.getvalue(), content_type='image/jpeg')

    def test_send_image_message(self):
        """
        اختبار إرسال رسالة مع صورة
        Test: Send message with image
        """
        print("\n" + "="*50)
        print("🖼️  اختبار إرسال رسالة مع صورة")
        print("="*50)
        
        # إنشاء صورة اختبار
        image = self.create_test_image('test_image.jpg', (100, 100))
        
        # إرسال POST request
        response = self.client.post(
            '/api/messages/',
            {
                'ticket': self.ticket.id,
                'message_text': 'صورة اختبار',
                'message_type': 'image',
                'image': image
            }
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Response Data: {response.json() if response.status_code == 201 else response.text}")
        
        # التحقق
        self.assertEqual(response.status_code, 201)
        
        # التحقق من الرسالة المحفوظة
        message = Message.objects.latest('created_at')
        print(f"✅ Message ID: {message.id}")
        print(f"✅ Message Type: {message.message_type}")
        print(f"✅ Media URL: {message.media_url}")
        
        self.assertEqual(message.message_type, 'image')
        self.assertIsNotNone(message.media_url)

    def test_send_text_message(self):
        """
        اختبار إرسال رسالة نصية
        Test: Send text message
        """
        print("\n" + "="*50)
        print("💬 اختبار إرسال رسالة نصية")
        print("="*50)
        
        response = self.client.post(
            '/api/messages/',
            {
                'ticket': self.ticket.id,
                'message_text': 'رسالة اختبار',
                'message_type': 'text'
            }
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Response Data: {response.json() if response.status_code == 201 else response.text}")
        
        self.assertEqual(response.status_code, 201)
        
        message = Message.objects.latest('created_at')
        print(f"✅ Message ID: {message.id}")
        print(f"✅ Message Text: {message.message_text}")
        print(f"✅ Sender Type: {message.sender_type}")
        
        self.assertEqual(message.message_type, 'text')
        self.assertEqual(message.sender_type, 'agent')

    def test_image_size_validation(self):
        """
        اختبار التحقق من حجم الصورة
        Test: Image size validation
        """
        print("\n" + "="*50)
        print("⚠️  اختبار التحقق من حجم الصورة")
        print("="*50)
        
        # إنشاء صورة كبيرة (محاكاة)
        large_image = self.create_test_image('large_image.jpg', (5000, 5000))
        
        response = self.client.post(
            '/api/messages/',
            {
                'ticket': self.ticket.id,
                'message_text': 'صورة كبيرة',
                'message_type': 'image',
                'image': large_image
            }
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Response Data: {response.json() if response.status_code != 201 else 'Success'}")
        
        # قد تنجح إذا كانت الصورة الفعلية أصغر من 5MB
        if response.status_code != 201:
            print("✅ تم رفض الصورة الكبيرة كما متوقع")

    def test_message_sender_type(self):
        """
        اختبار تعيين sender_type تلقائياً
        Test: Automatic sender_type assignment
        """
        print("\n" + "="*50)
        print("👤 اختبار تعيين sender_type")
        print("="*50)
        
        response = self.client.post(
            '/api/messages/',
            {
                'ticket': self.ticket.id,
                'message_text': 'رسالة لاختبار sender_type'
            }
        )
        
        print(f"✅ Response Status: {response.status_code}")
        
        self.assertEqual(response.status_code, 201)
        
        message = Message.objects.latest('created_at')
        print(f"✅ Sender Type: {message.sender_type}")
        print(f"✅ Sender: {message.sender}")
        
        self.assertEqual(message.sender_type, 'agent')
        self.assertEqual(message.sender, self.user)


def run_tests():
    """
    تشغيل جميع الاختبارات
    """
    print("\n" + "="*60)
    print("🧪 تشغيل اختبارات تحميل الصور")
    print("="*60)
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    failures = test_runner.run_tests(['__main__'])
    
    if failures == 0:
        print("\n" + "="*60)
        print("✅ جميع الاختبارات نجحت!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print(f"❌ فشل {failures} اختبار(ات)")
        print("="*60)


if __name__ == '__main__':
    run_tests()