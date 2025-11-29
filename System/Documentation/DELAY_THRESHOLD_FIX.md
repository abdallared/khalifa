# إصلاح Delay Threshold - استخدام الإعدادات

## المشكلة
- غيرت الـ delay threshold في صفحة Settings لدقيقة واحدة
- لكن التذاكر مش بتتعلم إنها delayed
- السبب: الكود كان بيستخدم قيمة ثابتة من Django settings، مش من SystemSettings

## الحل

### الملف المُعدل: `System/conversations/utils.py`

#### قبل التعديل ❌
```python
def check_ticket_delay(ticket):
    """فحص ما إذا كانت التذكرة متأخرة"""
    ...
    
    # ❌ يستخدم قيمة ثابتة من Django settings
    delay_threshold = getattr(settings, 'DELAY_THRESHOLD_MINUTES', 3)
    
    time_since_customer_message = timezone.now() - ticket.last_customer_message_at
    
    if time_since_customer_message.total_seconds() > (delay_threshold * 60):
        return True
    
    return False
```

#### بعد التعديل ✅
```python
def check_ticket_delay(ticket):
    """فحص ما إذا كانت التذكرة متأخرة"""
    ...
    
    # ✅ يستخدم delay_threshold من SystemSettings
    from .models import SystemSettings
    system_settings = SystemSettings.get_settings()
    delay_threshold = system_settings.delay_threshold_minutes
    
    time_since_customer_message = timezone.now() - ticket.last_customer_message_at
    
    if time_since_customer_message.total_seconds() > (delay_threshold * 60):
        return True
    
    return False
```

---

## الاختبار

### Test 1: Delay Threshold = 1 Minute ✅
```bash
python test_delay_threshold.py
```

**النتيجة:**
```
Test 1: Set delay threshold to 1 minute
  ✅ Delay threshold set to: 1 minute(s)

Test 2: Create test ticket
  ✅ Ticket created
  ✅ Last customer message: 2 minutes ago

Test 3: Check if ticket is delayed (threshold = 1 minute)
  ✅ Is delayed: True  ← التذكرة متأخرة لأن مر 2 دقيقة والحد 1 دقيقة
```

### Test 2: Delay Threshold = 3 Minutes ✅
```
Test 4: Change threshold to 3 minutes
  ✅ Delay threshold set to: 3 minute(s)
  ✅ Is delayed: False  ← التذكرة مش متأخرة لأن مر 2 دقيقة والحد 3 دقائق
```

---

## كيفية الاستخدام

### 1. تغيير Delay Threshold من صفحة Settings
1. افتح `/admin/settings/`
2. غيّر "عتبة التأخير (بالدقائق)" من 3 إلى 1
3. احفظ الإعدادات

### 2. اختبار التأخير
1. افتح محادثة مع عميل
2. العميل يرسل رسالة
3. انتظر دقيقة واحدة بدون رد من الموظف
4. **✅ التذكرة تتحول لـ "delayed" تلقائياً**

### 3. التحقق من Dashboard
1. افتح `/admin/dashboard/`
2. في قسم "Delayed Tickets" هتلاقي التذاكر المتأخرة
3. التذاكر اللي مر عليها أكثر من الـ threshold هتظهر هنا

---

## متى يتم فحص التأخير؟

الـ `check_ticket_delay()` function يتم استدعاؤها في:

1. **عند استقبال رسالة من العميل** - `views_whatsapp.py`
2. **عند إرسال رسالة من الموظف** - `views_messages.py`
3. **في الـ Dashboard** - `views.py`
4. **في صفحة المحادثات** - `views.py`

---

## الفرق بين القيم

| Delay Threshold | معنى التأخير |
|----------------|--------------|
| 1 دقيقة | إذا لم يرد الموظف خلال دقيقة واحدة، التذكرة تصبح delayed |
| 3 دقائق (افتراضي) | إذا لم يرد الموظف خلال 3 دقائق، التذكرة تصبح delayed |
| 5 دقائق | إذا لم يرد الموظف خلال 5 دقائق، التذكرة تصبح delayed |

---

## الملفات المُعدلة

1. ✅ `System/conversations/utils.py`
   - تعديل `check_ticket_delay()` function
   - استخدام `SystemSettings.get_settings().delay_threshold_minutes`

---

## الخلاصة

### قبل الإصلاح ❌
- الـ delay threshold كان ثابت (3 دقائق)
- تغيير الإعدادات من صفحة Settings مكانش بيأثر
- التذاكر كانت بتتأخر بعد 3 دقائق دائماً

### بعد الإصلاح ✅
- الـ delay threshold يُقرأ من SystemSettings
- تغيير الإعدادات من صفحة Settings بيأثر فوراً
- التذاكر بتتأخر حسب القيمة المحددة في الإعدادات

**🎉 دلوقتي لما تغير الـ delay threshold في Settings، التذاكر هتتأخر حسب القيمة الجديدة!**
