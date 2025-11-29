# 🔌 Driver Pattern Architecture

## 📋 نظرة عامة:

```
🎯 الفكرة الأساسية:
   نظام مرن يسمح بالتبديل بين مزودي WhatsApp بدون تغيير الكود التجاري

🔌 المبدأ:
   ├── Interface موحد (MessageDriver)
   ├── Core لا يعرف مزود WhatsApp
   ├── Drivers قابلة للتبديل
   └── بيانات موحدة (provider + id_ext)

📦 الـ Drivers:
   ├── WPPConnect Driver (المرحلة 2 - الجزء 1)
   │   ├── QR Code Scan
   │   ├── مجاني
   │   └── سريع التطبيق
   │
   └── Cloud API Driver (المرحلة 2 - الجزء 2)
       ├── WhatsApp Business Cloud API
       ├── رسمي وموثوق
       └── مدفوع

🔄 التحويل:
   تغيير WHATSAPP_DRIVER في .env فقط
   ← كل شيء آخر يعمل تلقائياً
```

---

## 🏗️ المعمارية (Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                       │
│                   (Business Logic Core)                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Tickets    │  │   Messages   │  │   Agents     │    │
│  │   Manager    │  │   Handler    │  │   Manager    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           ↓                                │
│              ┌────────────────────────┐                    │
│              │   MessageDriver        │                    │
│              │   (Abstract Interface) │                    │
│              └────────────┬───────────┘                    │
└───────────────────────────┼────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │    Driver Factory         │
              │  (based on WHATSAPP_DRIVER)│
              └─────────────┬─────────────┘
                            │
              ┌─────────────┴─────────────┐
              ↓                           ↓
    ┌─────────────────┐         ┌─────────────────┐
    │ WPPConnect      │         │ Cloud API       │
    │ Driver          │         │ Driver          │
    │                 │         │                 │
    │ - QR Scan       │         │ - Official API  │
    │ - Free          │         │ - Paid          │
    │ - Quick Setup   │         │ - Reliable      │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             ↓                           ↓
    ┌─────────────────┐         ┌─────────────────┐
    │ Redis Queue     │         │ Redis Queue     │
    │ (Incoming)      │         │ (Incoming)      │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             ↓                           ↓
       WhatsApp Web              WhatsApp Business
       (QR Code)                 Cloud API
```

---

## 🔧 MessageDriver Interface

```python
# drivers/base.py
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class IncomingMessage:
    """رسالة واردة من WhatsApp"""
    id_ext: str              # ID من WhatsApp
    phone: str               # رقم المرسل
    message_text: str        # نص الرسالة
    message_type: str        # text, image, audio, video, document
    media_url: Optional[str] # رابط الميديا (إن وجد)
    mime_type: Optional[str] # نوع الملف
    timestamp: int           # وقت الإرسال
    raw_data: Dict[str, Any] # البيانات الخام

class MessageDriver(ABC):
    """Interface موحد لجميع مزودي WhatsApp"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = "base"
    
    @abstractmethod
    async def initialize(self) -> bool:
        """تهيئة الاتصال بـ WhatsApp"""
        pass
    
    @abstractmethod
    async def on_message(self, callback: Callable):
        """تسجيل callback للرسائل الواردة"""
        pass
    
    @abstractmethod
    async def send_text(self, phone: str, message: str) -> Dict[str, Any]:
        """إرسال رسالة نصية"""
        pass
    
    @abstractmethod
    async def send_media(self, phone: str, media_url: str, 
                        media_type: str, caption: str = None) -> Dict[str, Any]:
        """إرسال ميديا"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الاتصال"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """قطع الاتصال"""
        pass
    
    def normalize_phone(self, phone: str) -> str:
        """توحيد صيغة رقم الهاتف"""
        phone = phone.strip().replace('+', '').replace(' ', '').replace('-', '')
        if phone.startswith('0'):
            phone = '20' + phone[1:]
        if not phone.startswith('20'):
            phone = '20' + phone
        return phone
```

---

## 📱 WPPConnect Driver

```python
# drivers/wppconnect_driver.py
import aiohttp
from .base import MessageDriver, IncomingMessage

class WPPConnectDriver(MessageDriver):
    """
    Driver لـ WPPConnect (QR Code)
    
    المميزات: مجاني، سريع التطبيق
    العيوب: يحتاج هاتف، قد يُحظر
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "wppconnect"
        self.base_url = config.get('base_url', 'http://localhost:21465')
        self.session_name = config.get('session_name', 'khalifa_pharmacy')
        self.secret_key = config.get('secret_key')
        self.token = None
    
    async def initialize(self) -> bool:
        """تهيئة جلسة WPPConnect"""
        self.session = aiohttp.ClientSession()
        
        # بدء الجلسة
        async with self.session.post(
            f"{self.base_url}/api/{self.session_name}/start-session",
            json={'secretkey': self.secret_key}
        ) as response:
            data = await response.json()
            self.token = data.get('token')
            return data.get('status', False)
    
    async def send_text(self, phone: str, message: str) -> Dict[str, Any]:
        """إرسال رسالة نصية"""
        phone = self.normalize_phone(phone)
        
        async with self.session.post(
            f"{self.base_url}/api/{self.session_name}/send-message",
            headers={'Authorization': f'Bearer {self.token}'},
            json={'phone': phone, 'message': message}
        ) as response:
            data = await response.json()
            
            return {
                'success': data.get('status') == 'success',
                'id_ext': data.get('response', {}).get('id'),
                'provider': self.provider_name
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """حالة الاتصال"""
        async with self.session.get(
            f"{self.base_url}/api/{self.session_name}/check-connection-session",
            headers={'Authorization': f'Bearer {self.token}'}
        ) as response:
            data = await response.json()
            
            return {
                'connected': data.get('status') == 'CONNECTED',
                'phone': data.get('phone', ''),
                'provider': self.provider_name
            }
```

---

## ☁️ Cloud API Driver

```python
# drivers/cloud_api_driver.py
import aiohttp
from .base import MessageDriver, IncomingMessage

class CloudAPIDriver(MessageDriver):
    """
    Driver لـ WhatsApp Business Cloud API
    
    المميزات: رسمي، موثوق، لا يحتاج هاتف
    العيوب: مدفوع، يحتاج موافقة Meta
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "cloud_api"
        self.phone_number_id = config.get('phone_number_id')
        self.access_token = config.get('access_token')
        self.api_version = config.get('api_version', 'v18.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    async def initialize(self) -> bool:
        """تهيئة Cloud API"""
        self.session = aiohttp.ClientSession()
        status = await self.get_status()
        return status.get('connected', False)
    
    async def send_text(self, phone: str, message: str) -> Dict[str, Any]:
        """إرسال رسالة نصية"""
        phone = self.normalize_phone(phone)
        
        async with self.session.post(
            f"{self.base_url}/{self.phone_number_id}/messages",
            headers={
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            },
            json={
                'messaging_product': 'whatsapp',
                'to': phone,
                'type': 'text',
                'text': {'body': message}
            }
        ) as response:
            data = await response.json()
            
            return {
                'success': response.status == 200,
                'id_ext': data.get('messages', [{}])[0].get('id'),
                'provider': self.provider_name
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """حالة الاتصال"""
        async with self.session.get(
            f"{self.base_url}/{self.phone_number_id}",
            headers={'Authorization': f'Bearer {self.access_token}'}
        ) as response:
            data = await response.json()
            
            return {
                'connected': response.status == 200,
                'phone': data.get('display_phone_number', ''),
                'provider': self.provider_name
            }
```

---

## 🏭 Driver Factory

```python
# drivers/factory.py
from .base import MessageDriver
from .wppconnect_driver import WPPConnectDriver
from .cloud_api_driver import CloudAPIDriver

class DriverFactory:
    """Factory لإنشاء Driver المناسب"""
    
    @staticmethod
    def create_from_env() -> MessageDriver:
        """إنشاء Driver من .env"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        driver_type = os.getenv('WHATSAPP_DRIVER', 'wppconnect')
        
        if driver_type == 'wppconnect':
            config = {
                'base_url': os.getenv('WPPCONNECT_URL'),
                'session_name': os.getenv('WPPCONNECT_SESSION'),
                'secret_key': os.getenv('WPPCONNECT_SECRET_KEY')
            }
            return WPPConnectDriver(config)
        
        elif driver_type == 'cloud_api':
            config = {
                'phone_number_id': os.getenv('CLOUD_API_PHONE_NUMBER_ID'),
                'access_token': os.getenv('CLOUD_API_ACCESS_TOKEN'),
                'api_version': os.getenv('CLOUD_API_VERSION', 'v18.0')
            }
            return CloudAPIDriver(config)
        
        else:
            raise ValueError(f"WHATSAPP_DRIVER غير صحيح: {driver_type}")
```

---

## 🗄️ تحديث قاعدة البيانات (Database Schema Updates)

### **إضافة حقول provider و id_ext:**

```sql
-- تحديث جدول customers
ALTER TABLE customers ADD COLUMN provider VARCHAR(50) DEFAULT 'wppconnect';
ALTER TABLE customers ADD COLUMN id_ext VARCHAR(255);  -- WhatsApp ID
ALTER TABLE customers ADD INDEX idx_provider_id_ext (provider, id_ext);

-- تحديث جدول tickets
ALTER TABLE tickets ADD COLUMN provider VARCHAR(50) DEFAULT 'wppconnect';
ALTER TABLE tickets ADD COLUMN id_ext VARCHAR(255);  -- Conversation ID من WhatsApp
ALTER TABLE tickets ADD INDEX idx_provider_id_ext (provider, id_ext);

-- تحديث جدول messages
ALTER TABLE messages ADD COLUMN provider VARCHAR(50) DEFAULT 'wppconnect';
-- id_ext موجود بالفعل في whatsapp_message_id
-- لكن نضيف provider للتوضيح
ALTER TABLE messages ADD INDEX idx_provider (provider);
```

---

## 🔄 استراتيجية التحويل (Migration Strategy)

### **من WPPConnect → Cloud API:**

```python
# management/commands/migrate_to_cloud_api.py
from django.core.management.base import BaseCommand
from conversations.models import Customer, Ticket, Message

class Command(BaseCommand):
    help = 'تحويل البيانات من WPPConnect إلى Cloud API'

    def handle(self, *args, **options):
        # 1. تحديث جميع السجلات الموجودة
        Customer.objects.filter(provider='wppconnect').update(provider='cloud_api')
        Ticket.objects.filter(provider='wppconnect').update(provider='cloud_api')
        Message.objects.filter(provider='wppconnect').update(provider='cloud_api')

        self.stdout.write(self.style.SUCCESS('✅ تم التحويل بنجاح'))

        # 2. التحقق
        wpp_count = Customer.objects.filter(provider='wppconnect').count()
        cloud_count = Customer.objects.filter(provider='cloud_api').count()

        self.stdout.write(f"WPPConnect: {wpp_count}")
        self.stdout.write(f"Cloud API: {cloud_count}")
```

### **خطوات التحويل:**

```
1. ✅ اختبار Cloud API في بيئة التطوير
2. ✅ نسخ احتياطي من قاعدة البيانات
3. ✅ تشغيل Migration Script
4. ✅ تغيير WHATSAPP_DRIVER=cloud_api في .env
5. ✅ إعادة تشغيل التطبيق
6. ✅ اختبار شامل
7. ✅ مراقبة لمدة 24 ساعة
8. ✅ إيقاف WPPConnect (اختياري)
```

---

## ⚙️ Environment Variables

### **.env للمرحلة 2 - الجزء 1 (WPPConnect):**

```bash
# WhatsApp Driver
WHATSAPP_DRIVER=wppconnect

# WPPConnect Settings
WPPCONNECT_URL=http://localhost:21465
WPPCONNECT_SESSION=khalifa_pharmacy
WPPCONNECT_SECRET_KEY=your_secret_key_here
WPPCONNECT_WEBHOOK_URL=https://yourdomain.com/api/webhook/wppconnect

# Redis (للـ Queue)
REDIS_URL=redis://localhost:6379/0
```

### **.env للمرحلة 2 - الجزء 2 (Cloud API):**

```bash
# WhatsApp Driver
WHATSAPP_DRIVER=cloud_api

# Cloud API Settings
CLOUD_API_PHONE_NUMBER_ID=123456789012345
CLOUD_API_ACCESS_TOKEN=your_access_token_here
CLOUD_API_VERSION=v18.0
CLOUD_API_WEBHOOK_VERIFY_TOKEN=your_verify_token_here

# Redis (للـ Queue)
REDIS_URL=redis://localhost:6379/0
```

---

## 🔄 Redis Queue Architecture

### **Message Flow:**

```
WhatsApp → Driver → Redis Queue → Worker → Core → Database
                                    ↓
                              Agent Notification
```

### **Redis Queues:**

```python
# queues.py
import redis
from rq import Queue

redis_conn = redis.from_url(os.getenv('REDIS_URL'))

# Queues
incoming_queue = Queue('incoming_messages', connection=redis_conn)
outgoing_queue = Queue('outgoing_messages', connection=redis_conn)
```

### **Worker للرسائل الواردة:**

```python
# workers/incoming_worker.py
from drivers.factory import DriverFactory
from conversations.models import Customer, Ticket, Message

async def process_incoming_message(message_data):
    """معالجة رسالة واردة"""

    # 1. البحث عن العميل أو إنشاؤه
    customer, created = Customer.objects.get_or_create(
        phone_number=message_data['phone'],
        defaults={
            'provider': message_data['provider'],
            'id_ext': message_data['id_ext']
        }
    )

    # 2. البحث عن تذكرة مفتوحة أو إنشاء جديدة
    ticket = Ticket.objects.filter(
        customer=customer,
        status='open'
    ).first()

    if not ticket:
        # توزيع على موظف
        agent = get_available_agent()
        ticket = Ticket.objects.create(
            customer=customer,
            assigned_agent=agent,
            status='open',
            provider=message_data['provider']
        )

    # 3. حفظ الرسالة
    message = Message.objects.create(
        ticket=ticket,
        sender_type='customer',
        message_text=message_data['message_text'],
        message_type=message_data['message_type'],
        whatsapp_message_id=message_data['id_ext'],
        provider=message_data['provider']
    )

    # 4. إشعار الموظف (WebSocket)
    notify_agent(ticket.assigned_agent, message)
```

---

## 🧪 Testing Strategy

### **اختبار WPPConnect Driver:**

```python
# tests/test_wppconnect_driver.py
import pytest
from drivers.wppconnect_driver import WPPConnectDriver

@pytest.mark.asyncio
async def test_wppconnect_initialize():
    config = {
        'base_url': 'http://localhost:21465',
        'session_name': 'test_session',
        'secret_key': 'test_key'
    }

    driver = WPPConnectDriver(config)
    result = await driver.initialize()

    assert result == True
    assert driver.token is not None

@pytest.mark.asyncio
async def test_wppconnect_send_text():
    driver = WPPConnectDriver(config)
    await driver.initialize()

    result = await driver.send_text('201012345678', 'مرحباً')

    assert result['success'] == True
    assert result['provider'] == 'wppconnect'
    assert 'id_ext' in result
```

### **اختبار Cloud API Driver:**

```python
# tests/test_cloud_api_driver.py
import pytest
from drivers.cloud_api_driver import CloudAPIDriver

@pytest.mark.asyncio
async def test_cloud_api_initialize():
    config = {
        'phone_number_id': '123456789',
        'access_token': 'test_token',
        'api_version': 'v18.0'
    }

    driver = CloudAPIDriver(config)
    result = await driver.initialize()

    assert result == True

@pytest.mark.asyncio
async def test_cloud_api_send_text():
    driver = CloudAPIDriver(config)
    await driver.initialize()

    result = await driver.send_text('201012345678', 'مرحباً')

    assert result['success'] == True
    assert result['provider'] == 'cloud_api'
```

---

## 🔙 Rollback Plan

### **إذا فشل Cloud API:**

```bash
# 1. إيقاف التطبيق
sudo systemctl stop khalifa_app

# 2. استعادة النسخة الاحتياطية
mysql -u root -p khalifa_db < backup_before_migration.sql

# 3. تغيير .env
WHATSAPP_DRIVER=wppconnect

# 4. إعادة تشغيل
sudo systemctl start khalifa_app

# 5. التحقق
curl http://localhost:8000/api/whatsapp/status
```

---

## 📊 خطة التنفيذ المحدثة

### **المرحلة 2 - الجزء 1: WPPConnect (8 أيام)**

```
اليوم 1-2: تصميم Driver Pattern
├── MessageDriver Interface
├── DriverFactory
└── تحديث Database Schema

اليوم 3-4: تطبيق WPPConnect Driver
├── WPPConnectDriver Class
├── Redis Queue Setup
└── Webhook Handler

اليوم 5-6: دمج مع Core
├── Incoming Message Handler
├── Outgoing Message Handler
└── WebSocket Notifications

اليوم 7-8: اختبار ونشر
├── Unit Tests
├── Integration Tests
└── Production Deployment
```

### **المرحلة 2 - الجزء 2: Cloud API (9 أيام)**

```
اليوم 1-2: إعداد Cloud API
├── تسجيل في Meta Developer
├── إنشاء WhatsApp Business Account
└── الحصول على Access Token

اليوم 3-4: تطبيق Cloud API Driver
├── CloudAPIDriver Class
├── Webhook Verification
└── Message Parsing

اليوم 5-6: Migration Script
├── Data Migration
├── Testing في بيئة التطوير
└── Rollback Plan

اليوم 7-9: النشر والمراقبة
├── Production Migration
├── Monitoring (24 ساعة)
└── Performance Tuning
```

---

## ✅ الخلاصة

```
🎯 Driver Pattern يوفر:
   ✅ مرونة في التبديل بين المزودين
   ✅ كود تجاري نظيف (لا يعتمد على مزود معين)
   ✅ سهولة الاختبار
   ✅ قابلية التوسع

🔄 التحويل:
   ✅ تغيير متغير واحد في .env
   ✅ بدون فقد بيانات
   ✅ مع Rollback Plan

📦 الملفات:
   ├── drivers/base.py (Interface)
   ├── drivers/wppconnect_driver.py
   ├── drivers/cloud_api_driver.py
   ├── drivers/factory.py
   └── .env (Configuration)
```

