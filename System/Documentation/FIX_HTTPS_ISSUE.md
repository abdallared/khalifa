# 🔧 إصلاح مشكلة HTTPS - WPPConnect

## 📋 المشكلة:
```
400 Bad Request
You're speaking plain HTTP to an SSL-enabled server port.
```

WPPConnect كان بيحاول يبعت على HTTP لكن Django شغال على HTTPS.

---

## ✅ الحل المطبق:

### 1. تغيير URL في الإعدادات:
تم تغيير `DJANGO_BACKEND_URL` من:
```
http://127.0.0.1:8000
```

إلى:
```
https://127.0.0.1:8000
```

في الملفات:
- ✅ `.env`
- ✅ `wppconnect-server/.env`

### 2. إضافة SSL Certificate Bypass:
تم إضافة الكود ده في `wppconnect-server/server.js`:

```javascript
const https = require('https');

// ✅ تجاهل أخطاء SSL للـ localhost (Development only)
const httpsAgent = new https.Agent({
    rejectUnauthorized: false
});
```

وتم إضافة `httpsAgent` في axios request:
```javascript
const response = await axios.post(webhookUrl, messageData, {
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    },
    timeout: 10000,
    httpsAgent: httpsAgent  // ✅ تجاهل أخطاء SSL
});
```

---

## 🚀 الخطوات التالية:

### 1. أعيدي تشغيل WPPConnect Server:
```bash
# أوقفي السيرفر الحالي (Ctrl+C)
# ثم شغليه تاني:
cd wppconnect-server
npm start
```

### 2. اختبري الاتصال:
أرسلي رسالة من WhatsApp وشوفي لو وصلت للنظام.

---

## ⚠️ ملاحظات مهمة:

### للتطوير (Development):
- ✅ `rejectUnauthorized: false` مناسب للتطوير على localhost
- ✅ يسمح بـ self-signed certificates

### للإنتاج (Production):
- ⚠️ **لازم تستخدمي SSL Certificate صحيح** (من Let's Encrypt مثلاً)
- ⚠️ **امسحي** `rejectUnauthorized: false` في الإنتاج
- ⚠️ أو استخدمي HTTP عادي إذا كان Django خلف Reverse Proxy

---

## 🔍 استكشاف الأخطاء:

### إذا لسه المشكلة موجودة:

#### الحل البديل 1: استخدام HTTP بدل HTTPS
إذا Django فعلاً شغال على HTTP عادي:

1. غيري الإعدادات لـ HTTP:
```bash
# في .env و wppconnect-server/.env
DJANGO_BACKEND_URL=http://127.0.0.1:8000
```

2. تأكدي إن مفيش Apache/IIS شغال قدام Django

#### الحل البديل 2: استخدام Domain Name
بدل `127.0.0.1` استخدمي `localhost`:
```bash
DJANGO_BACKEND_URL=https://localhost:8000
```

---

## 📊 التحقق من النجاح:

بعد إعادة تشغيل WPPConnect، لازم تشوفي في Terminal:
```
📤 Sending to Django: https://127.0.0.1:8000/api/whatsapp/webhook/
✅ Sent to Django successfully: 200
```

بدل:
```
❌ Failed to send to Django: 400 Bad Request
```

---

**تم الإصلاح بواسطة:** Kiro AI Assistant  
**التاريخ:** 12 نوفمبر 2025
