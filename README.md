# 🏥 Khalifa Pharmacy - Conversation Management System
## نظام إدارة محادثات صيدليات خليفة

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2.7-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Integration-25D366?style=for-the-badge&logo=whatsapp)
![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)

**نظام متكامل لإدارة محادثات العملاء عبر WhatsApp مع تتبع الأداء والتحليلات**

</div>

---

## 👨‍💻 المطور

**محمد فارس** - AI Software Engineer  
مهندس برمجيات متخصص في تطوير تطبيقات الذكاء الاصطناعي ومتكاملات منصات التواصل الاجتماعي

---

## 📋 نظرة عامة

نظام إدارة محادثات صيدليات خليفة هو منصة شاملة لإدارة تفاعلات العملاء عبر WhatsApp، مع ميزات متقدمة لتتبع الأداء، إدارة التذاكر، والتحليلات في الوقت الفعلي.

### ✨ المميزات الرئيسية

#### 🎯 إدارة المحادثات
- ✅ ربط مباشر مع WhatsApp عبر WPPConnect
- ✅ إدارة التذاكر (Tickets) بنظام ذكي
- ✅ توزيع تلقائي للتذاكر على الموظفين
- ✅ دعم الرسائل النصية والصور والملفات
- ✅ قوالب رسائل جاهزة (Templates)
- ✅ ردود تلقائية (Auto-Reply)

#### 👥 إدارة الموظفين
- ✅ نظام صلاحيات متعدد المستويات (Admin, Agent, QA, Supervisor, Manager)
- ✅ تتبع حالة الموظفين (Online/Offline/Break)
- ✅ إدارة السعة القصوى لكل موظف
- ✅ نقل التذاكر بين الموظفين
- ✅ تتبع وقت الاستراحة

#### 📊 التحليلات والتقارير
- ✅ مؤشرات الأداء (KPIs) في الوقت الفعلي
- ✅ تقارير يومية وشهرية
- ✅ تتبع وقت الاستجابة
- ✅ معدل حل المشكلات
- ✅ رضا العملاء
- ✅ تحليل التأخيرات

#### 🔔 الإشعارات والتنبيهات
- ✅ تنبيهات التأخير في الرد
- ✅ إشعارات التذاكر الجديدة
- ✅ تنبيهات السعة القصوى
- ✅ إشعارات نقل التذاكر

#### 🛡️ الأمان والحماية
- ✅ نظام مصادقة آمن
- ✅ حماية من هجمات Brute Force
- ✅ تشفير كلمات المرور
- ✅ سجل النشاطات (Activity Log)
- ✅ جلسات دائمة آمنة

---

## 🏗️ البنية التقنية

### Backend
- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Authentication:** Session-based + Custom Backend

### WhatsApp Integration
- **Driver:** WPPConnect
- **Features:** Send/Receive Messages, Media Support, QR Code Authentication

### Frontend
- **Technology:** HTML5, CSS3, JavaScript (Vanilla)
- **Design:** Modern, Responsive, RTL Support
- **Icons:** Custom SVG Icons
- **Theme:** Dark Mode (Sophos XG Inspired)

---

## 📦 التثبيت

### المتطلبات
- Python 3.10+
- Node.js 16+
- npm

### التثبيت السريع

```bash
# 1. Clone المشروع
git clone [repository-url]
cd khalifa

# 2. إنشاء وتفعيل البيئة الافتراضية
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. تثبيت المكتبات
pip install -r requirements.txt

# 4. إعداد قاعدة البيانات
cd System
python manage.py migrate

# 5. تشغيل WPPConnect
cd ..\wppconnect-server
npm install
npm start

# 6. تشغيل Django
cd ..\System
python manage.py runserver 0.0.0.0:8888
```

📖 **للمزيد من التفاصيل:** راجع [INSTALLATION.md](INSTALLATION.md)

---

## 🚀 الاستخدام

### تشغيل المشروع

#### Windows:
```bash
# تشغيل كل شيء
START_SERVERS.bat

# أو للتطوير
dev.bat
```

#### Linux/Mac:
```bash
# تشغيل Django
python System/manage.py runserver 0.0.0.0:8888

# تشغيل WPPConnect (في terminal آخر)
cd wppconnect-server && npm start
```

### الوصول إلى النظام

- **Frontend:** http://localhost:8888
- **API:** http://localhost:8888/api/
- **Admin Panel:** http://localhost:8888/admin/
- **WPPConnect:** http://localhost:3000

### المستخدم الافتراضي

```
Username: admin
Password: admin123
```

---

## 📚 البنية الهيكلية

```
khalifa/
├── System/                          # Django Project
│   ├── conversations/               # Main App
│   │   ├── models.py               # 22 Database Models
│   │   ├── views.py                # API Endpoints
│   │   ├── serializers.py          # DRF Serializers
│   │   ├── utils.py                # Utility Functions
│   │   ├── whatsapp_driver.py      # WhatsApp Integration
│   │   ├── message_queue.py        # Message Queue Manager
│   │   ├── middleware.py           # Custom Middleware
│   │   ├── permissions.py          # Custom Permissions
│   │   └── management/             # Django Commands
│   ├── khalifa_pharmacy/           # Project Settings
│   │   ├── settings.py             # Configuration
│   │   ├── urls.py                 # URL Routing
│   │   └── wsgi.py                 # WSGI Config
│   ├── static/                     # Static Files
│   ├── media/                      # Uploaded Media
│   ├── templates/                  # HTML Templates
│   ├── logs/                       # Log Files
│   └── db.sqlite3                  # Database
├── wppconnect-server/              # WhatsApp Server
├── requirements.txt                # Python Dependencies
├── requirements-dev.txt            # Development Dependencies
├── requirements-prod.txt           # Production Dependencies
├── README.md                       # This File
├── INSTALLATION.md                 # Installation Guide
└── .env                            # Environment Variables
```

---

## 🗄️ نماذج قاعدة البيانات (22 Model)

### 1. User Management (3 Models)
- `User` - المستخدمون
- `Agent` - الموظفون
- `Admin` - المديرون

### 2. Customer Management (3 Models)
- `Customer` - العملاء
- `CustomerTag` - تصنيفات العملاء
- `CustomerNote` - ملاحظات العملاء

### 3. Ticket Management (3 Models)
- `Ticket` - التذاكر
- `TicketTransferLog` - سجل نقل التذاكر
- `TicketStateLog` - سجل تغييرات الحالة

### 4. Messages (3 Models)
- `Message` - الرسائل
- `MessageDeliveryLog` - سجل التوصيل
- `MessageSearchIndex` - فهرس البحث

### 5. Templates (3 Models)
- `GlobalTemplate` - القوالب العامة
- `AgentTemplate` - قوالب الموظفين
- `AutoReplyTrigger` - محفزات الرد التلقائي

### 6. Delay Tracking (3 Models)
- `ResponseTimeTracking` - تتبع وقت الاستجابة
- `AgentDelayEvent` - أحداث التأخير
- `AgentBreakSession` - جلسات الاستراحة

### 7. KPI & Performance (3 Models)
- `AgentKPI` - مؤشرات الأداء اليومية
- `AgentKPIMonthly` - مؤشرات الأداء الشهرية
- `CustomerSatisfaction` - رضا العملاء

### 8. System (3 Models)
- `ActivityLog` - سجل النشاطات
- `LoginAttempt` - محاولات تسجيل الدخول
- `SystemSettings` - إعدادات النظام

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/login/              # تسجيل الدخول
POST   /api/auth/logout/             # تسجيل الخروج
GET    /api/auth/profile/            # الملف الشخصي
```

### Tickets
```
GET    /api/tickets/                 # قائمة التذاكر
POST   /api/tickets/                 # إنشاء تذكرة
GET    /api/tickets/{id}/            # تفاصيل تذكرة
PATCH  /api/tickets/{id}/            # تحديث تذكرة
POST   /api/tickets/{id}/close/      # إغلاق تذكرة
POST   /api/tickets/{id}/transfer/   # نقل تذكرة
```

### Messages
```
GET    /api/messages/                # قائمة الرسائل
POST   /api/messages/                # إرسال رسالة
GET    /api/tickets/{id}/messages/   # رسائل تذكرة معينة
```

### Agents
```
GET    /api/agents/                  # قائمة الموظفين
POST   /api/agents/create_with_user/ # إنشاء موظف
GET    /api/agents/available/        # الموظفين المتاحين
GET    /api/agents/me/               # بيانات الموظف الحالي
POST   /api/agents/{id}/take_break/  # بدء استراحة
POST   /api/agents/{id}/end_break/   # إنهاء استراحة
```

### Analytics
```
GET    /api/analytics/dashboard/     # لوحة التحكم
GET    /api/analytics/agent-kpi/     # KPI الموظفين
GET    /api/analytics/tickets-stats/ # إحصائيات التذاكر
```

---

## 🛠️ Django Management Commands

```bash
# تحديث مؤشرات الأداء
python manage.py update_kpis

# معالجة قائمة الرسائل
python manage.py process_message_queue

# تحديث التذاكر المتأخرة
python manage.py update_delayed_tickets

# تحديث عدد التذاكر النشطة
python manage.py update_active_tickets

# إعادة تعيين حالة الموظفين
python manage.py reset_online_status

# تحديث جميع الإحصائيات
python manage.py update_all_stats
```

---

## 🧪 الاختبار

```bash
# تشغيل جميع الاختبارات
pytest

# اختبار مع تغطية الكود
pytest --cov=conversations

# اختبار ملف معين
pytest System/test_agent_break.py
```

---

## 📈 الأداء والتحسين

### Database Optimization
- ✅ Database Indexes على الحقول الأكثر استخداماً
- ✅ `select_related()` و `prefetch_related()` للاستعلامات
- ✅ Connection Pooling

### Caching
- ✅ Django Cache Framework
- ✅ Redis للـ Session Storage (Production)

### Queue Management
- ✅ Message Queue مع Deduplication
- ✅ Rate Limiting
- ✅ Retry Mechanism مع Exponential Backoff

---

## 🔒 الأمان

### Best Practices
- ✅ CSRF Protection
- ✅ SQL Injection Prevention (Django ORM)
- ✅ XSS Protection
- ✅ Password Hashing (Django's make_password)
- ✅ Brute Force Protection (5 attempts → 15 min lockout)
- ✅ Session Security (HttpOnly, SameSite)

### Production Security
```python
# في settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

---

## 📝 المساهمة

هذا مشروع خاص لصيدليات خليفة. للمساهمة:
1. Fork المشروع
2. إنشاء Branch جديد (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى Branch (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

---

## 📄 الترخيص

هذا المشروع خاص ومملوك لصيدليات خليفة. جميع الحقوق محفوظة © 2025

---

## 📞 الدعم والتواصل

**المطور:** محمد فارس  
**التخصص:** AI Software Engineer  
**البريد الإلكتروني:** [your-email@example.com]

---

## 🙏 شكر وتقدير

- Django Framework
- Django REST Framework
- WPPConnect Team
- جميع المكتبات مفتوحة المصدر المستخدمة

---

## 🗺️ خارطة الطريق

### المرحلة الحالية ✅
- [x] نظام إدارة المحادثات الأساسي
- [x] ربط WhatsApp
- [x] إدارة التذاكر
- [x] مؤشرات الأداء
- [x] نظام الصلاحيات

### المرحلة القادمة 🚀
- [ ] WebSocket للتحديثات الفورية
- [ ] تطبيق Mobile (React Native)
- [ ] AI Chatbot للردود التلقائية
- [ ] تحليلات متقدمة بالذكاء الاصطناعي
- [ ] تكامل مع أنظمة ERP

---

<div align="center">

**صُنع بـ ❤️ في مصر**

**محمد فارس - AI Software Engineer**

</div>
#   k h a l i f a  
 "# khalifa" 
