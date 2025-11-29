# 🔧 حل مشكلة WhatsApp Webhook - HTTP vs HTTPS

## ❌ **المشكلة:**

```
400 Bad Request
Reason: You're speaking plain HTTP to an SSL-enabled server port.
```

**السبب:** Django شغال على Apache/Nginx مع SSL، لكن WPPConnect بيبعت على HTTP

---

## ✅ **الحل السريع (للتطوير):**

### **الخطوة 1: إيقاف Django الحالي**

```bash
# ابحث عن Django process
netstat -ano | findstr :8000

# النتيجة:
# TCP    0.0.0.0:8000    LISTENING    5148

# أوقف الـ process
taskkill /PID 5148 /F
```

### **الخطوة 2: تشغيل Django مباشرة (بدون Apache/Nginx)**

```bash
# في terminal جديد
cd System
python manage.py runserver 127.0.0.1:8000
```

**أو استخدم الملف الجاهز:**

```bash
# في المجلد الرئيسي
run.bat
```

---

## ✅ **الحل البديل: تغيير WPPConnect ليستخدم HTTPS**

إذا كنت **لازم** تستخدم Apache/Nginx مع SSL:

### **1. تعديل `.env`:**

```env
# قبل:
DJANGO_BACKEND_URL=http://127.0.0.1:8000

# بعد:
DJANGO_BACKEND_URL=https://127.0.0.1:8000
```

### **2. إعادة تشغيل WPPConnect:**

```bash
cd wppconnect-server

# إيقاف الـ server القديم
# Ctrl+C أو:
taskkill /F /IM node.exe

# تشغيل من جديد
npm start
```

---

## 🎯 **التوصية:**

**للتطوير:** استخدم **الحل السريع** (Django مباشرة بدون SSL)

**للإنتاج:** استخدم **الحل البديل** (HTTPS مع SSL Certificate صحيح)

---

## ✅ **التحقق من الحل:**

بعد تطبيق الحل، جرب:

```bash
# اختبار الـ webhook
curl -X POST http://127.0.0.1:8000/api/whatsapp/webhook/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: khalifa-pharmacy-secret-key-2025" \
  -d '{"phone":"201234567890","message_text":"test"}'
```

**النتيجة المتوقعة:** 200 OK أو 400 (لكن مش SSL error)

---

## 📝 **ملاحظات:**

1. **Apache/Nginx** بيشتغل على البورت 8000 حالياً
2. لازم توقفه أو تغير البورت
3. Django development server أسهل للتطوير
4. للإنتاج، استخدم Gunicorn + Nginx مع SSL صحيح
