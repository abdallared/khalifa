# 🚀 تشغيل نظام صيدليات خليفة

## ✅ الإعدادات الحالية:

### Django Backend:
- **Port:** 8888
- **URL:** http://127.0.0.1:8888
- **Protocol:** HTTP

### WPPConnect Server:
- **Port:** 3000
- **URL:** http://127.0.0.1:3000
- **Protocol:** HTTP

### الاتصال:
- WPPConnect يبعت Webhook على: `http://127.0.0.1:8888/api/whatsapp/webhook/`

---

## 🚀 خطوات التشغيل:

### 1️⃣ تشغيل Django (إذا مش شغال):
```bash
cd System
python manage.py runserver 0.0.0.0:8888
```

**النتيجة المتوقعة:**
```
Starting development server at http://0.0.0.0:8888/
```

---

### 2️⃣ تشغيل WPPConnect Server:
```bash
cd wppconnect-server
npm start
```

**النتيجة المتوقعة:**
```
🚀 Starting WhatsApp Client...
📱 QR Code Generated
✅ WhatsApp Client Started Successfully!
🚀 WPPConnect Server started on port 3000
```

---

### 3️⃣ ربط WhatsApp:
1. انتظري ظهور QR Code في Terminal
2. افتحي WhatsApp على موبايلك
3. اذهبي إلى: **الإعدادات** → **الأجهزة المرتبطة** → **ربط جهاز**
4. امسحي الـ QR Code

**النتيجة المتوقعة:**
```
✅ QR Code Scanned Successfully!
✅ WhatsApp Connected!
```

---

### 4️⃣ اختبار النظام:
1. أرسلي رسالة من WhatsApp للرقم المربوط
2. شوفي Terminal WPPConnect، لازم تشوفي:

```
📩 New Message Received: 201234567890
📤 Sending to Django: http://127.0.0.1:8888/api/whatsapp/webhook/
✅ Sent to Django successfully: 200
```

3. افتحي المتصفح: http://127.0.0.1:8888/admin/
4. سجلي دخول كـ Admin
5. شوفي التذاكر - لازم تلاقي التذكرة الجديدة

---

## 🔍 استكشاف الأخطاء:

### المشكلة: Port 8888 مستخدم
**الحل:**
```bash
# شوفي مين اللي شغال على Port 8888
netstat -ano | findstr :8888

# أوقفي العملية (غيري XXXX برقم العملية)
taskkill /PID XXXX /F
```

### المشكلة: Port 3000 مستخدم
**الحل:**
```bash
# شوفي مين اللي شغال على Port 3000
netstat -ano | findstr :3000

# أوقفي العملية
taskkill /PID XXXX /F
```

### المشكلة: QR Code مش ظاهر
**الحل:**
```bash
# امسحي السيشن القديمة
Remove-Item -Path "wppconnect-server\tokens\khalifa-pharmacy" -Recurse -Force

# شغلي WPPConnect تاني
npm start
```

### المشكلة: Webhook بيرجع 400/500
**الحل:**
1. تأكدي إن Django شغال
2. تأكدي إن الـ URL صح: `http://127.0.0.1:8888`
3. تأكدي إن API Key متطابق في الملفين

---

## 📊 التحقق من النجاح:

### ✅ Django شغال:
افتحي المتصفح: http://127.0.0.1:8888
لازم تشوفي صفحة Django

### ✅ WPPConnect شغال:
افتحي المتصفح: http://127.0.0.1:3000/health
لازم تشوفي:
```json
{
  "status": "ok",
  "whatsapp_connected": true,
  "timestamp": "..."
}
```

### ✅ WhatsApp متصل:
في Terminal WPPConnect لازم تشوفي:
```
✅ WhatsApp Connected - Session Active
```

---

## 🎯 الخطوات السريعة (للمرات القادمة):

```bash
# Terminal 1: Django
cd System
python manage.py runserver 0.0.0.0:8888

# Terminal 2: WPPConnect
cd wppconnect-server
npm start
```

---

## 📝 ملاحظات مهمة:

1. ✅ Django على Port **8888** (HTTP)
2. ✅ WPPConnect على Port **3000** (HTTP)
3. ✅ لا تعارض في Ports
4. ✅ الاتصال بينهم HTTP عادي (مناسب للتطوير)
5. ⚠️ في الإنتاج: استخدمي HTTPS مع SSL Certificate صحيح

---

**تم إعداد الدليل بواسطة:** Kiro AI Assistant  
**التاريخ:** 12 نوفمبر 2025
