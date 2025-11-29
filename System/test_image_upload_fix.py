#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار شامل لإصلاح مشكلة رفع الصور
Comprehensive test for image upload fix
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from conversations.models import User, Agent, Admin, Customer, Ticket, Message
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

def create_test_user():
    """إنشاء مستخدم اختبار"""
    print("\n[1] إنشاء مستخدم اختبار...")
    
    # Delete existing test user
    User.objects.filter(username='test_agent').delete()
    
    # Create new test user
    user = User.objects.create(
        username='test_agent',
        full_name='Test Agent',
        role='agent',
        is_active=True
    )
    user.set_password('test123')
    user.save()
    
    # Create agent profile
    try:
        Agent.objects.create(user=user, max_capacity=15)
    except:
        pass
    
    print(f"✓ تم إنشاء المستخدم: {user.username}")
    return user


def create_test_customer():
    """إنشاء عميل اختبار"""
    print("\n[2] إنشاء عميل اختبار...")
    
    # Delete existing
    Customer.objects.filter(phone_number='201012345678').delete()
    
    customer = Customer.objects.create(
        phone_number='201012345678',
        name='Test Customer',
        wa_id='201012345678'
    )
    
    print(f"✓ تم إنشاء العميل: {customer.name}")
    return customer


def create_test_ticket(user, customer):
    """إنشاء تذكرة اختبار"""
    print("\n[3] إنشاء تذكرة اختبار...")
    
    try:
        agent = Agent.objects.get(user=user)
    except:
        agent = Agent.objects.create(user=user, max_capacity=15)
    
    ticket = Ticket.objects.create(
        customer=customer,
        assigned_agent=agent,
        current_agent=agent,
        status='open'
    )
    
    print(f"✓ تم إنشاء التذكرة: {ticket.ticket_number}")
    return ticket


def create_test_image():
    """إنشاء صورة اختبار"""
    print("\n[4] إنشاء صورة اختبار...")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_io.name = 'test_image.png'
    
    print(f"✓ تم إنشاء صورة الاختبار: {img_io.name}")
    return img_io


def test_image_upload(user, ticket):
    """اختبار رفع الصورة عبر API"""
    print("\n[5] اختبار رفع الصورة...")
    
    client = APIClient()
    client.defaults['HTTP_HOST'] = 'localhost:8000'
    
    # Authenticate
    client.force_authenticate(user=user)
    print(f"✓ تم المصادقة كـ: {user.username}")
    
    # Create test image
    img = create_test_image()
    
    # Prepare request data
    data = {
        'ticket': ticket.id,
        'message_text': 'صورة اختبار',
        'image': img
    }
    
    # Send request
    print("\nإرسال الطلب...")
    response = client.post('/api/messages/', data, format='multipart', HTTP_HOST='localhost:8000')
    
    print(f"حالة الاستجابة: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("\n✓ تم رفع الصورة بنجاح!")
        
        # Get the last message
        message = Message.objects.all().order_by('-created_at').first()
        print(f"\nتفاصيل الرسالة:")
        print(f"  - ID: {message.id}")
        print(f"  - نوع الرسالة: {message.message_type}")
        print(f"  - رابط الوسيط: {message.media_url}")
        print(f"  - نوع MIME: {message.mime_type}")
        print(f"  - المرسل: {message.sender.full_name}")
        print(f"  - نوع المرسل: {message.sender_type}")
        print(f"  - الاستجابة: {response.data}")
        
        return True
    else:
        print(f"\n✗ فشل رفع الصورة!")
        try:
            print(f"  الاستجابة: {response.data}")
        except:
            print(f"  الاستجابة: {response.content}")
        return False


def test_text_message(user, ticket):
    """اختبار إرسال رسالة نصية"""
    print("\n[6] اختبار إرسال رسالة نصية...")
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    data = {
        'ticket': ticket.id,
        'message_text': 'رسالة اختبار نصية'
    }
    
    response = client.post('/api/messages/', data, HTTP_HOST='localhost:8000')
    
    print(f"حالة الاستجابة: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✓ تم إرسال الرسالة النصية بنجاح!")
        message = Message.objects.all().order_by('-created_at').first()
        print(f"  - نوع الرسالة: {message.message_type}")
        return True
    else:
        print(f"✗ فشل إرسال الرسالة النصية!")
        try:
            print(f"  الاستجابة: {response.data}")
        except:
            print(f"  الاستجابة: {response.content}")
        return False


def run_tests():
    """تشغيل جميع الاختبارات"""
    print("\n" + "="*60)
    print("اختبار شامل لإصلاح مشكلة رفع الصور")
    print("="*60)
    
    try:
        # Create test data
        user = create_test_user()
        customer = create_test_customer()
        ticket = create_test_ticket(user, customer)
        
        # Run tests
        success = True
        
        # Test 1: Text message
        if not test_text_message(user, ticket):
            success = False
        
        # Test 2: Image upload
        if not test_image_upload(user, ticket):
            success = False
        
        # Print summary
        print("\n" + "="*60)
        if success:
            print("✓ جميع الاختبارات نجحت!")
        else:
            print("✗ فشلت بعض الاختبارات")
        print("="*60 + "\n")
        
        return success
        
    except Exception as e:
        print(f"\n✗ خطأ أثناء الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)