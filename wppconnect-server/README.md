# 🔌 WPPConnect Server - صيدليات خليفة

خادم WPPConnect للربط مع WhatsApp

---

## 📋 المتطلبات

### 1. Node.js
```bash
# تحميل Node.js من:
https://nodejs.org/

# التحقق من التثبيت:
node --version  # يجب أن يكون >= 16.x
npm --version
```

### 2. Redis (اختياري لكن موصى به)
```bash
# Windows:
# تحميل من: https://github.com/microsoftarchive/redis/releases
# أو استخدام Docker:
docker run -d -p 6379:6379 redis

# Linux/Mac:
sudo apt-get install redis-server
# أو
brew install redis
```

---

## 🚀 التثبيت

### 1. تثبيت Dependencies
```bash
cd wppconnect-server
npm install
```

### 2. إعداد Environment Variables
```bash
# نسخ ملف .env.example إلى .env
copy .env.example .env

# تعديل القيم في .env:
# - PORT: منفذ الخادم (افتراضي: 3000)
# - DJANGO_BACKEND_URL: عنوان Django (افتراضي: http://localhost:8000)
# - API_KEY: مفتاح API للأمان (غيّره!)
```

### 3. تشغيل الخادم
```bash
# Production
npm start

# Development (مع auto-reload)
npm run dev
```

---

## 📱 ربط WhatsApp

### 1. تشغيل الخادم
```bash
npm start
```

### 2. مسح QR Code
- سيظهر QR Code في الـ Terminal
- افتح WhatsApp على هاتفك
- اذهب إلى: الإعدادات > الأجهزة المرتبطة > ربط جهاز
- امسح الـ QR Code

### 3. التأكد من الاتصال
```bash
# في متصفح آخر أو Postman:
GET http://localhost:3000/api/status
Headers: X-API-Key: your-secret-api-key
```

---

## 🔌 API Endpoints

### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "ok",
  "whatsapp_connected": true,
  "timestamp": "2025-10-30T12:00:00.000Z"
}
```

### 2. Get QR Code
```http
GET /api/qr-code
Headers: X-API-Key: your-secret-api-key
```
**Response:**
```json
{
  "success": true,
  "qr_code": "data:image/png;base64,...",
  "qr_url": "https://..."
}
```

### 3. Get Connection Status
```http
GET /api/status
Headers: X-API-Key: your-secret-api-key
```
**Response:**
```json
{
  "connected": true,
  "session": "khalifa-pharmacy",
  "phone": "201234567890",
  "device": "Samsung",
  "timestamp": "2025-10-30T12:00:00.000Z"
}
```

### 4. Send Text Message
```http
POST /api/send-message
Headers: 
  Content-Type: application/json
  X-API-Key: your-secret-api-key

Body:
{
  "phone": "201234567890",
  "message": "مرحباً! كيف يمكنني مساعدتك؟"
}
```
**Response:**
```json
{
  "success": true,
  "message_id": "...",
  "phone": "201234567890"
}
```

### 5. Logout
```http
POST /api/logout
Headers: X-API-Key: your-secret-api-key
```
**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 🔄 كيف يعمل النظام؟

### الرسائل الواردة (من العميل):
```
1. عميل يرسل رسالة WhatsApp
   ↓
2. WPPConnect يستقبل الرسالة
   ↓
3. WPPConnect يرسل POST request إلى Django:
   POST http://localhost:8000/api/whatsapp/webhook/
   ↓
4. Django يعالج الرسالة ويحفظها في قاعدة البيانات
   ↓
5. الموظف يرى الرسالة في صفحة "محادثاتي"
```

### الرسائل الصادرة (من الموظف):
```
1. الموظف يكتب رد في صفحة "محادثاتي"
   ↓
2. Frontend يرسل AJAX إلى Django
   ↓
3. Django يحفظ الرسالة في قاعدة البيانات
   ↓
4. Django يرسل POST request إلى WPPConnect:
   POST http://localhost:3000/api/send-message
   ↓
5. WPPConnect يرسل الرسالة عبر WhatsApp
   ↓
6. العميل يستقبل الرسالة ✅
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: QR Code لا يظهر
**الحل:**
```bash
# تأكد من تثبيت Chrome/Chromium
# أو استخدم useChrome: true في server.js
```

### المشكلة: WhatsApp يفصل باستمرار
**الحل:**
```bash
# تأكد من استقرار الإنترنت
# تأكد من عدم استخدام الرقم على أجهزة أخرى
# أعد تشغيل الخادم
```

### المشكلة: الرسائل لا تصل إلى Django
**الحل:**
```bash
# تحقق من DJANGO_BACKEND_URL في .env
# تحقق من أن Django يعمل على المنفذ الصحيح
# تحقق من API_KEY
```

---

## 📝 ملاحظات مهمة

⚠️ **الأمان:**
- غيّر `API_KEY` في `.env` قبل الإنتاج
- لا تشارك `.env` في Git
- استخدم HTTPS في الإنتاج

⚠️ **الاستقرار:**
- استخدم `pm2` أو `forever` لتشغيل الخادم في الإنتاج
- راقب الـ logs باستمرار
- احتفظ بنسخة احتياطية من session data

⚠️ **WhatsApp Policy:**
- لا ترسل رسائل spam
- احترم سياسات WhatsApp
- استخدم الرقم بشكل مسؤول

---

## 🔧 Production Deployment

### استخدام PM2 (موصى به):
```bash
# تثبيت PM2
npm install -g pm2

# تشغيل الخادم
pm2 start server.js --name khalifa-wppconnect

# عرض الحالة
pm2 status

# عرض الـ logs
pm2 logs khalifa-wppconnect

# إعادة التشغيل
pm2 restart khalifa-wppconnect

# إيقاف
pm2 stop khalifa-wppconnect
```

---

## 📞 الدعم

للمزيد من المعلومات:
- WPPConnect Docs: https://wppconnect.io/
- GitHub: https://github.com/wppconnect-team/wppconnect

---

**تم إعداده بواسطة:** Augment AI Agent  
**التاريخ:** 2025-10-30

