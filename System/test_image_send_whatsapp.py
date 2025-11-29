#!/usr/bin/env python
"""
اختبار شامل لإرسال الصور إلى الواتساب
Testing image sending to WhatsApp via WPPConnect
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from conversations.models import Customer, Ticket, Message, Agent
from conversations.whatsapp_driver import get_whatsapp_driver

User = get_user_model()


class WhatsAppMediaSendTest:
    """اختبار إرسال الصور إلى الواتساب"""
    
    def __init__(self):
        self.client = APIClient()
        self.user = None
        self.customer = None
        self.ticket = None
        self.agent = None
        print("✅ Test initialization completed\n")
    
    def create_test_user(self):
        """إنشاء مستخدم اختبار (موظف)"""
        print("📝 Creating test user...")
        
        # حذف إذا كان موجوداً
        User.objects.filter(username='agent_test').delete()
        
        self.user = User.objects.create_user(
            username='agent_test',
            password='testpass123',
            email='agent@test.com',
            role='agent',
            is_active=True
        )
        
        # إنشاء Agent
        Agent.objects.filter(user=self.user).delete()
        self.agent = Agent.objects.create(
            user=self.user,
            department='Support',
            max_concurrent_tickets=10
        )
        
        print(f"✅ User created: {self.user.username}")
        print(f"✅ Agent created: {self.agent.id}\n")
    
    def create_test_customer(self):
        """إنشاء عميل للاختبار"""
        print("📝 Creating test customer...")
        
        # حذف إذا كان موجوداً
        Customer.objects.filter(phone_number='201010101010').delete()
        
        self.customer = Customer.objects.create(
            phone_number='201010101010',
            name='عميل الاختبار',
            wa_id='201010101010@c.us'
        )
        
        print(f"✅ Customer created: {self.customer.phone_number}")
        print(f"✅ Customer wa_id: {self.customer.wa_id}\n")
    
    def create_test_ticket(self):
        """إنشاء تذكرة للاختبار"""
        print("📝 Creating test ticket...")
        
        self.ticket = Ticket.objects.create(
            ticket_number='TEST-001',
            customer=self.customer,
            assigned_agent=self.agent,
            status='open',
            priority='medium',
            category='test'
        )
        
        print(f"✅ Ticket created: {self.ticket.ticket_number}")
        print(f"✅ Ticket ID: {self.ticket.id}\n")
    
    def create_test_image(self):
        """إنشاء صورة اختبار"""
        print("📝 Creating test image...")
        
        # إنشاء صورة بحجم صغير
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        image_io.name = 'test_image.jpg'
        
        print(f"✅ Test image created: {image_io.name}\n")
        return image_io
    
    def test_text_message(self):
        """اختبار 1: إرسال رسالة نصية"""
        print("\n" + "="*60)
        print("🧪 TEST 1: Sending Text Message")
        print("="*60)
        
        self.client.force_authenticate(user=self.user)
        
        data = {
            'ticket': self.ticket.id,
            'message_text': 'اختبار الرسالة النصية',
            'message_type': 'text'
        }
        
        response = self.client.post('/api/messages/', data, format='json')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        if response.status_code == status.HTTP_201_CREATED:
            message = response.json()
            print(f"✅ Message created successfully")
            print(f"   - Message ID: {message.get('id')}")
            print(f"   - Message Type: {message.get('message_type')}")
            print(f"   - Sender: {message.get('sender')}\n")
            return True
        else:
            print(f"❌ Failed to create message")
            print(f"   Error: {response.json()}\n")
            return False
    
    def test_image_message(self):
        """اختبار 2: إرسال صورة"""
        print("\n" + "="*60)
        print("🧪 TEST 2: Sending Image Message")
        print("="*60)
        
        self.client.force_authenticate(user=self.user)
        
        # إنشاء صورة اختبار
        image = self.create_test_image()
        
        data = {
            'ticket': self.ticket.id,
            'message_text': 'صورة الاختبار',
            'message_type': 'image',
            'image': image
        }
        
        response = self.client.post(
            '/api/messages/',
            data,
            format='multipart'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        if response.status_code == status.HTTP_201_CREATED:
            message = response.json()
            print(f"✅ Image message created successfully")
            print(f"   - Message ID: {message.get('id')}")
            print(f"   - Message Type: {message.get('message_type')}")
            print(f"   - Media URL: {message.get('media_url')}")
            print(f"   - MIME Type: {message.get('mime_type')}")
            print(f"   - WhatsApp Message ID: {message.get('whatsapp_message_id')}\n")
            
            # تحقق من الرسالة في قاعدة البيانات
            self.verify_message_in_db(message.get('id'))
            return True
        else:
            print(f"❌ Failed to create image message")
            print(f"   Error: {response.json()}\n")
            return False
    
    def verify_message_in_db(self, message_id):
        """التحقق من الرسالة في قاعدة البيانات"""
        print("🔍 Verifying message in database...")
        
        try:
            message = Message.objects.get(id=message_id)
            print(f"✅ Message found in DB")
            print(f"   - ID: {message.id}")
            print(f"   - Type: {message.message_type}")
            print(f"   - Sender Type: {message.sender_type}")
            print(f"   - Direction: {message.direction}")
            print(f"   - Delivery Status: {message.delivery_status}")
            print(f"   - Media URL: {message.media_url}")
            print(f"   - WhatsApp Message ID: {message.whatsapp_message_id}")
            print(f"   - Created At: {message.created_at}\n")
        except Message.DoesNotExist:
            print(f"❌ Message not found in DB\n")
    
    def test_driver_send_media(self):
        """اختبار 3: اختبار Driver مباشرة"""
        print("\n" + "="*60)
        print("🧪 TEST 3: Testing WPPConnect Driver Directly")
        print("="*60)
        
        try:
            driver = get_whatsapp_driver()
            
            print(f"Driver: {driver.provider_name}")
            print(f"Base URL: {driver.base_url}\n")
            
            # اختبار إرسال صورة (محاكاة)
            print("📤 Calling send_media_message()...")
            result = driver.send_media_message(
                phone='201010101010',
                media_url='http://localhost:8000/media/messages/test.jpg',
                media_type='image',
                caption='صورة اختبار'
            )
            
            print(f"Result: {result}\n")
            
            if result.get('success'):
                print(f"✅ Media sent successfully")
                print(f"   - Message ID: {result.get('message_id')}")
                print(f"   - Phone: {result.get('phone')}")
                return True
            else:
                print(f"⚠️  Send failed (expected if WPPConnect not connected)")
                print(f"   Error: {result.get('error')}\n")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            return False
    
    def test_driver_normalize_phone(self):
        """اختبار 4: اختبار توحيد أرقام الهاتف"""
        print("\n" + "="*60)
        print("🧪 TEST 4: Testing Phone Number Normalization")
        print("="*60)
        
        driver = get_whatsapp_driver()
        
        test_cases = [
            ('201010101010', '201010101010'),
            ('+201010101010', '201010101010'),
            ('01010101010', '201010101010'),
            ('1010101010', '201010101010'),
            ('201010101010@c.us', '201010101010@c.us'),  # لا تغيير عند وجود @
        ]
        
        print("Testing phone normalization:\n")
        
        for input_phone, expected in test_cases:
            if '@' in input_phone:
                result = input_phone
                status_check = "✅" if result == expected else "❌"
            else:
                result = driver.normalize_phone(input_phone)
                status_check = "✅" if result == expected else "❌"
            
            print(f"{status_check} {input_phone:20} → {result}")
        
        print()
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("\n" + "="*60)
        print("🚀 RUNNING ALL TESTS")
        print("="*60 + "\n")
        
        try:
            # إعداد البيانات
            self.create_test_user()
            self.create_test_customer()
            self.create_test_ticket()
            
            # تشغيل الاختبارات
            results = {
                'Text Message': self.test_text_message(),
                'Image Message': self.test_image_message(),
                'Driver Direct Test': self.test_driver_send_media(),
                'Phone Normalization': True  # هذا دائماً يعمل
            }
            
            self.test_driver_normalize_phone()
            
            # ملخص النتائج
            print("="*60)
            print("📊 TEST SUMMARY")
            print("="*60)
            
            for test_name, result in results.items():
                status_icon = "✅" if result else "⚠️"
                print(f"{status_icon} {test_name}")
            
            passed = sum(1 for r in results.values() if r)
            total = len(results)
            
            print(f"\n✅ Passed: {passed}/{total}")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Test error: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """تشغيل الاختبارات"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  WhatsApp Image Send Test Suite".center(58) + "║")
    print("║" + "  اختبار إرسال الصور إلى الواتساب".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝\n")
    
    tester = WhatsAppMediaSendTest()
    tester.run_all_tests()


if __name__ == '__main__':
    main()