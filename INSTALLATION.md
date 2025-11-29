# 📦 دليل التثبيت - Khalifa Pharmacy System

## نظام إدارة محادثات صيدليات خليفة
**Created by: محمد فارس - AI Software Engineer**

---

## 📋 المتطلبات الأساسية

### 1. Python
- **الإصدار المطلوب:** Python 3.10 أو أحدث
- تحقق من الإصدار:
```bash
python --version
```

### 2. Node.js (لـ WPPConnect)
- **الإصدار المطلوب:** Node.js 16+ و npm
- تحقق من الإصدار:
```bash
node --version
npm --version
```

---

## 🚀 خطوات التثبيت

### الخطوة 1️⃣: إنشاء بيئة افتراضية (Virtual Environment)

#### على Windows:
```bash
# الانتقال إلى مجلد المشروع
cd d:\khalifa_latest033\khalifa_latest02\khalifa_latest\khalifa\khalifa

# إنشاء البيئة الافتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
venv\Scripts\activate
```

#### على Linux/Mac:
```bash
# إنشاء البيئة الافتراضية
python3 -m venv venv

# تفعيل البيئة الافتراضية
source venv/bin/activate
```

---

### الخطوة 2️⃣: تثبيت المكتبات المطلوبة

```bash
# تثبيت جميع المكتبات من requirements.txt
pip install -r requirements.txt

# أو تثبيت المكتبات يدوياً:
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install python-dotenv==1.0.0
pip install python-dateutil==2.8.2
pip install pytz==2024.1
pip install requests==2.31.0
pip install Pillow==10.4.0
pip install django-cors-headers==4.3.1
```

---

### الخطوة 3️⃣: إعداد قاعدة البيانات

```bash
# الانتقال إلى مجلد System
cd System

# إنشاء جداول قاعدة البيانات
python manage.py makemigrations
python manage.py migrate

# إنشاء مستخدم Admin (اختياري)
python manage.py createsuperuser
```

---

### الخطوة 4️⃣: إعداد WPPConnect Server

```bash
# الانتقال إلى مجلد wppconnect-server
cd wppconnect-server

# تثبيت المكتبات
npm install

# تشغيل السيرفر
npm start
```

**ملاحظة:** WPPConnect سيعمل على المنفذ `3000` افتراضياً.

---

### الخطوة 5️⃣: تشغيل Django Server

```bash
# العودة إلى مجلد System
cd ..\System

# تشغيل السيرفر
python manage.py runserver 0.0.0.0:8888
```

**السيرفر سيعمل على:** `http://localhost:8888`

---

## 🔧 إعدادات متقدمة

### 1. ملف `.env`
قم بإنشاء ملف `.env` في المجلد الرئيسي:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# WhatsApp Settings
WPPCONNECT_HOST=localhost
WPPCONNECT_PORT=3000
WHATSAPP_API_KEY=khalifa-pharmacy-secret-key-2025
WPPCONNECT_SESSION_NAME=khalifa-pharmacy

# Media Domain (للوصول للصور من الخارج)
WHATSAPP_MEDIA_DOMAIN=http://localhost:8888
```

### 2. إعدادات قاعدة البيانات (Production)

#### PostgreSQL:
```python
# في settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'khalifa_pharmacy_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

ثم قم بتثبيت:
```bash
pip install psycopg2-binary==2.9.9
```

#### MySQL:
```python
# في settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'khalifa_pharmacy_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

ثم قم بتثبيت:
```bash
pip install mysqlclient==2.2.0
```

---

## 🎯 تشغيل المشروع بالكامل

### استخدام ملفات Batch (Windows):

#### 1. تشغيل كل شيء:
```bash
START_SERVERS.bat
```

#### 2. تشغيل للتطوير:
```bash
dev.bat
```

#### 3. إيقاف السيرفرات:
```bash
stop.bat
```

---

## 📊 التحقق من التثبيت

### 1. اختبار Django:
```bash
python manage.py check
```

### 2. اختبار الاتصال بـ WhatsApp:
افتح المتصفح وانتقل إلى:
```
http://localhost:3000/api/khalifa-pharmacy/qrcode-session
```

### 3. الوصول إلى Django Admin:
```
http://localhost:8888/admin/
```

### 4. الوصول إلى API:
```
http://localhost:8888/api/
```

---

## 🛠️ حل المشاكل الشائعة

### مشكلة: `ModuleNotFoundError`
**الحل:**
```bash
# تأكد من تفعيل البيئة الافتراضية
venv\Scripts\activate

# أعد تثبيت المكتبات
pip install -r requirements.txt
```

### مشكلة: `database is locked`
**الحل:**
```bash
# أغلق جميع الاتصالات بقاعدة البيانات
# أعد تشغيل السيرفر
```

### مشكلة: WPPConnect لا يعمل
**الحل:**
```bash
# تأكد من تثبيت Node.js
node --version

# أعد تثبيت المكتبات
cd wppconnect-server
npm install
npm start
```

### مشكلة: Pillow لا يعمل على Windows
**الحل:**
```bash
# قم بتثبيت Visual C++ Build Tools
# ثم أعد تثبيت Pillow
pip uninstall Pillow
pip install Pillow==10.4.0
```

---

## 📚 الأوامر المفيدة

### Django Management Commands:

```bash
# إنشاء مستخدم جديد
python manage.py createsuperuser

# جمع الملفات الثابتة
python manage.py collectstatic

# تحديث KPIs
python manage.py update_kpis

# معالجة قائمة الرسائل
python manage.py process_message_queue

# تحديث حالة التذاكر المتأخرة
python manage.py update_delayed_tickets

# إعادة تعيين حالة الموظفين
python manage.py reset_online_status
```

---

## 🔐 الأمان (Production)

### 1. تغيير SECRET_KEY:
```python
# في settings.py
SECRET_KEY = 'your-new-secret-key-here'
```

### 2. تعطيل DEBUG:
```python
DEBUG = False
```

### 3. تحديد ALLOWED_HOSTS:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### 4. استخدام HTTPS:
```python
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

---

## 📞 الدعم والمساعدة

إذا واجهت أي مشاكل:
1. تحقق من ملف `logs/django.log`
2. راجع الوثائق في `Instructions.txt`
3. تواصل مع المطور: محمد فارس

---

## ✅ قائمة التحقق النهائية

- [ ] Python 3.10+ مثبت
- [ ] Node.js 16+ مثبت
- [ ] البيئة الافتراضية مفعلة
- [ ] جميع المكتبات مثبتة من `requirements.txt`
- [ ] قاعدة البيانات تم إنشاؤها (`migrate`)
- [ ] ملف `.env` تم إعداده
- [ ] WPPConnect يعمل على المنفذ 3000
- [ ] Django يعمل على المنفذ 8888
- [ ] WhatsApp تم ربطه بنجاح (QR Code)

---

**🎉 تم التثبيت بنجاح! استمتع باستخدام نظام إدارة محادثات صيدليات خليفة**
