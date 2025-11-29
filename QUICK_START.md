# ⚡ دليل البدء السريع - Khalifa Pharmacy System

## 🚀 تثبيت وتشغيل المشروع في 5 دقائق

---

## ✅ المتطلبات

- ✔️ Python 3.10+
- ✔️ Node.js 16+
- ✔️ 10 دقائق من وقتك

---

## 📦 التثبيت السريع

### 1️⃣ إنشاء البيئة الافتراضية (30 ثانية)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

---

### 2️⃣ تثبيت المكتبات (2 دقيقة)

```bash
pip install -r requirements.txt
```

**المكتبات المثبتة:**
- Django 4.2.7
- Django REST Framework
- Pillow (للصور)
- Requests (للـ API)
- وغيرها...

---

### 3️⃣ إعداد قاعدة البيانات (30 ثانية)

```bash
cd System
python manage.py migrate
```

---

### 4️⃣ تشغيل WPPConnect (1 دقيقة)

```bash
# في terminal جديد
cd wppconnect-server
npm install
npm start
```

**✅ WPPConnect يعمل على:** http://localhost:3000

---

### 5️⃣ تشغيل Django (30 ثانية)

```bash
# في terminal آخر
cd System
python manage.py runserver 0.0.0.0:8888
```

**✅ Django يعمل على:** http://localhost:8888

---

## 🎯 الوصول إلى النظام

### 1. الواجهة الأمامية
```
http://localhost:8888
```

### 2. لوحة التحكم Admin
```
http://localhost:8888/admin/
```

### 3. API Documentation
```
http://localhost:8888/api/
```

### 4. WPPConnect QR Code
```
http://localhost:3000/api/khalifa-pharmacy/qrcode-session
```

---

## 👤 المستخدم الافتراضي

```
Username: admin
Password: admin123
```

**⚠️ تحذير:** قم بتغيير كلمة المرور بعد أول تسجيل دخول!

---

## 🔧 إنشاء مستخدم جديد

```bash
python manage.py createsuperuser
```

---

## 📱 ربط WhatsApp

1. افتح: http://localhost:3000/api/khalifa-pharmacy/qrcode-session
2. امسح QR Code من تطبيق WhatsApp
3. انتظر رسالة "Connected"
4. ابدأ باستقبال الرسائل!

---

## 🛠️ أوامر مفيدة

### تشغيل كل شيء (Windows)
```bash
START_SERVERS.bat
```

### إيقاف السيرفرات (Windows)
```bash
stop.bat
```

### تحديث قاعدة البيانات
```bash
python manage.py migrate
```

### إنشاء بيانات تجريبية
```bash
python manage.py create_sample_data
```

---

## ❓ حل المشاكل السريع

### مشكلة: `ModuleNotFoundError`
```bash
# تأكد من تفعيل البيئة الافتراضية
venv\Scripts\activate
pip install -r requirements.txt
```

### مشكلة: `Port already in use`
```bash
# أوقف العملية على المنفذ 8888
# Windows:
netstat -ano | findstr :8888
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8888 | xargs kill -9
```

### مشكلة: WPPConnect لا يعمل
```bash
cd wppconnect-server
rm -rf node_modules
npm install
npm start
```

---

## 📚 الخطوات التالية

بعد التثبيت الناجح:

1. ✅ اقرأ [README.md](README.md) للتعرف على المشروع
2. ✅ راجع [INSTALLATION.md](INSTALLATION.md) للتفاصيل الكاملة
3. ✅ اطلع على [DEPENDENCIES.md](DEPENDENCIES.md) لفهم المكتبات
4. ✅ ابدأ باستخدام النظام!

---

## 🎉 تهانينا!

أنت الآن جاهز لاستخدام نظام إدارة محادثات صيدليات خليفة!

---

**صُنع بـ ❤️ بواسطة محمد فارس - AI Software Engineer**
