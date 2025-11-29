# 📋 تحديث: حساب التأخير من وقت اختيار الفئة

## 🎯 الهدف من التحديث

تم تعديل النظام بحيث يبدأ حساب تأخير التذكرة من **وقت اختيار العميل للفئة** (شكوى/أدوية/متابعة) بدلاً من وقت أول رسالة.

---

## 🔄 التغييرات المُنفذة

### 1. إضافة حقل جديد في جدول `tickets`

**الحقل الجديد:**
```python
category_selected_at = models.DateTimeField(null=True, blank=True)
```

**الوصف:** يحفظ التوقيت الدقيق لاختيار العميل نوع الخدمة (1، 2، أو 3)

**Migration:** `0009_ticket_category_selected_at.py`

---

### 2. تحديث `handle_menu_selection()` في `utils.py`

**الموقع:** `System/conversations/utils.py` - السطور 482-518

**التعديل:**
```python
# عند اختيار "شكوى"
ticket.category = 'complaint'
ticket.priority = 'high'
ticket.category_selected_at = timezone.now()  # ✅ تسجيل وقت الاختيار
ticket.save(update_fields=['category', 'priority', 'category_selected_at'])

# عند اختيار "أدوية"
ticket.category = 'medicine_order'
ticket.priority = 'medium'
ticket.category_selected_at = timezone.now()  # ✅ تسجيل وقت الاختيار
ticket.save(update_fields=['category', 'priority', 'category_selected_at'])

# عند اختيار "متابعة"
ticket.category = 'follow_up'
ticket.priority = 'low'
ticket.category_selected_at = timezone.now()  # ✅ تسجيل وقت الاختيار
ticket.save(update_fields=['category', 'priority', 'category_selected_at'])
```

---

### 3. تحديث `check_ticket_delay()` في `utils.py`

**الموقع:** `System/conversations/utils.py` - السطور 252-283

**المنطق الجديد:**
```python
def check_ticket_delay(ticket):
    """
    فحص ما إذا كانت التذكرة متأخرة (حسب الإجابة س11: 3 دقائق)
    
    ✅ التحديث: يبدأ حساب التأخير من وقت اختيار العميل للفئة (شكوى/أدوية/متابعة)
    """
    if ticket.status != 'open':
        return False
    
    # ✅ استخدام category_selected_at إذا كان متاحاً، وإلا استخدام last_customer_message_at
    reference_time = ticket.category_selected_at or ticket.last_customer_message_at
    
    if not reference_time:
        return False
    
    # الحصول على عتبة التأخير من الإعدادات (3 دقائق)
    delay_threshold = getattr(settings, 'DELAY_THRESHOLD_MINUTES', 3)
    
    # حساب الوقت منذ اختيار الفئة أو آخر رسالة من العميل
    time_since_reference = timezone.now() - reference_time
    
    # إذا مر أكثر من 3 دقائق بدون رد من الموظف
    if time_since_reference.total_seconds() > (delay_threshold * 60):
        return True
    
    return False
```

**الفائدة:**
- إذا كان `category_selected_at` موجوداً → يستخدمه كنقطة بداية
- إذا لم يكن موجوداً (تذاكر قديمة) → يستخدم `last_customer_message_at`

---

### 4. تحديث `update_delayed_tickets` Command

**الموقع:** `System/conversations/management/commands/update_delayed_tickets.py` - السطور 27-90

**التعديل:**
```python
# ✅ استخدام category_selected_at إذا كان متاحاً، وإلا استخدام آخر رسالة من العميل
reference_time = ticket.category_selected_at

if not reference_time:
    # إذا لم يتم اختيار الفئة بعد، استخدام آخر رسالة من العميل
    last_customer_msg = Message.objects.filter(
        ticket=ticket,
        sender_type='customer'
    ).order_by('-created_at').first()
    
    if last_customer_msg:
        reference_time = last_customer_msg.created_at
```

---

### 5. تحديث `TicketSerializer`

**الموقع:** `System/conversations/serializers.py` - السطور 305-322

**التعديل:**
```python
fields = [
    # ... الحقول الأخرى
    'category_selected_at',  # ✅ إضافة الحقل الجديد
    # ...
]

read_only_fields = [
    # ... الحقول الأخرى
    'category_selected_at',  # ✅ إضافة للحقول للقراءة فقط
    # ...
]
```

---

## 📊 سير العمل الجديد

### السيناريو الكامل:

```
1. العميل يرسل رسالة أولى
   ↓
2. النظام يرسل رسالة الترحيب مع الخيارات (1، 2، 3)
   ↓
3. العميل يختار (مثلاً: 1 - شكوى)
   ↓
4. ✅ النظام يسجل category_selected_at = الآن
   ↓
5. النظام يرسل رسالة تأكيد
   ↓
6. العميل يكتب تفاصيل شكواه (يمكنه الكتابة بحرية)
   ↓
7. ⏱️ يبدأ حساب التأخير من category_selected_at
   ↓
8. إذا مر 3 دقائق بدون رد من الموظف → التذكرة تصبح متأخرة
```

---

## ✅ الفوائد

1. **دقة أكبر في حساب التأخير:**
   - التأخير يُحسب من وقت اختيار الفئة (عندما يكون العميل جاهزاً للتواصل)
   - وليس من أول رسالة (قد تكون مجرد "مرحباً")

2. **عدالة أكثر للموظفين:**
   - لا يُحسب الوقت الذي يستغرقه العميل في اختيار الفئة ضمن التأخير

3. **توافق مع التذاكر القديمة:**
   - التذاكر القديمة (قبل التحديث) تستخدم `last_customer_message_at`
   - التذاكر الجديدة تستخدم `category_selected_at`

4. **مرونة للعميل:**
   - العميل يمكنه الكتابة بحرية بعد اختيار الفئة
   - لا يوجد حظر على الكتابة

---

## 🧪 الاختبار

### اختبار يدوي:

```bash
# 1. تشغيل الخادم
cd System
python manage.py runserver

# 2. إرسال رسالة من WhatsApp
# 3. اختيار فئة (1، 2، أو 3)
# 4. التحقق من قاعدة البيانات

python manage.py shell
>>> from conversations.models import Ticket
>>> ticket = Ticket.objects.last()
>>> ticket.category_selected_at
datetime.datetime(2025, 11, 10, 14, 30, 0, tzinfo=<UTC>)
```

### اختبار التأخير:

```bash
# تشغيل أمر فحص التأخير
python manage.py update_delayed_tickets
```

---

## 📝 الملفات المُعدلة

1. ✅ `System/conversations/models.py` - إضافة حقل `category_selected_at`
2. ✅ `System/conversations/utils.py` - تحديث `handle_menu_selection()` و `check_ticket_delay()`
3. ✅ `System/conversations/serializers.py` - إضافة الحقل للـ API
4. ✅ `System/conversations/management/commands/update_delayed_tickets.py` - تحديث المنطق
5. ✅ `System/conversations/migrations/0009_ticket_category_selected_at.py` - Migration جديد

---

## 🚀 التطبيق

```bash
# 1. تطبيق Migration
cd System
python manage.py migrate conversations

# 2. إعادة تشغيل الخادم
python manage.py runserver
```

---

## 📌 ملاحظات مهمة

- ✅ التحديث متوافق مع التذاكر القديمة (Backward Compatible)
- ✅ لا يؤثر على التذاكر المغلقة
- ✅ يعمل تلقائياً مع الرسائل الجديدة
- ✅ لا يتطلب تغييرات في الـ Frontend

---

## 🔍 التحقق من النجاح

بعد التطبيق، تحقق من:

1. ✅ Migration تم تطبيقه بنجاح
2. ✅ الحقل `category_selected_at` موجود في جدول `tickets`
3. ✅ عند اختيار فئة، يتم تسجيل الوقت
4. ✅ حساب التأخير يستخدم الوقت الصحيح

---

**تاريخ التحديث:** 2025-11-10  
**الإصدار:** 1.1  
**الحالة:** ✅ مُطبق ومُختبر

