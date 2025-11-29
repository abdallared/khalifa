# 🛑 نظام الاستراحة للموظفين - Agent Break System

## 📋 نظرة عامة

تم إضافة نظام استراحة كامل للموظفين يسمح لهم بأخذ استراحة وعدم استقبال تذاكر جديدة حتى يعودوا للعمل.

---

## ✨ المميزات

### 1. **أزرار التحكم في الاستراحة**
- ✅ زر "أخذ استراحة" - يظهر عندما الموظف يعمل
- ✅ زر "العودة للعمل" - يظهر عندما الموظف في استراحة
- ✅ تنبيه مرئي عند الاستراحة

### 2. **منع استقبال التذاكر**
- ✅ الموظفين في استراحة لا يستقبلون تذاكر جديدة
- ✅ خوارزمية التوزيع تستبعد الموظفين في استراحة
- ✅ التذاكر الحالية تبقى مع الموظف

### 3. **تتبع وقت الاستراحة**
- ✅ تسجيل وقت بدء الاستراحة
- ✅ حساب مدة الاستراحة عند العودة
- ✅ تتبع إجمالي دقائق الاستراحة اليومية

---

## 🗄️ التغييرات في قاعدة البيانات

### حقول جديدة في جدول `agents`:

```python
# Break Tracking
is_on_break = models.BooleanField(default=False)  # هل الموظف في استراحة؟
break_started_at = models.DateTimeField(null=True, blank=True)  # متى بدأت الاستراحة
total_break_minutes_today = models.IntegerField(default=0)  # إجمالي دقائق الاستراحة اليوم
```

### Migration:
```bash
python manage.py makemigrations conversations
# Output: 0010_agent_break_started_at_agent_is_on_break_and_more.py

python manage.py migrate conversations
# Output: OK
```

---

## 🔌 API Endpoints

### 1. **الحصول على بيانات الموظف الحالي**
```http
GET /api/agents/me/
```

**Response:**
```json
{
  "id": 1,
  "user": {...},
  "is_on_break": false,
  "break_started_at": null,
  "total_break_minutes_today": 0,
  "status": "available",
  ...
}
```

---

### 2. **بدء الاستراحة**
```http
POST /api/agents/{id}/take_break/
```

**Response:**
```json
{
  "success": true,
  "message": "تم بدء الاستراحة بنجاح. لن تستقبل تذاكر جديدة حتى تنهي الاستراحة.",
  "data": {
    "is_on_break": true,
    "break_started_at": "2025-11-10T12:00:00Z",
    "status": "on_break",
    ...
  }
}
```

**ما يحدث:**
1. ✅ تحديث `is_on_break = True`
2. ✅ تسجيل `break_started_at = الآن`
3. ✅ تحديث `status = 'on_break'`
4. ✅ تسجيل النشاط في Activity Log

---

### 3. **إنهاء الاستراحة**
```http
POST /api/agents/{id}/end_break/
```

**Response:**
```json
{
  "success": true,
  "message": "تم إنهاء الاستراحة بنجاح. مدة الاستراحة: 15 دقيقة. يمكنك الآن استقبال التذاكر.",
  "data": {
    "is_on_break": false,
    "break_started_at": null,
    "total_break_minutes_today": 15,
    "status": "available",
    ...
  }
}
```

**ما يحدث:**
1. ✅ حساب مدة الاستراحة
2. ✅ إضافة المدة إلى `total_break_minutes_today`
3. ✅ تحديث `is_on_break = False`
4. ✅ مسح `break_started_at = None`
5. ✅ تحديث `status` بناءً على عدد التذاكر
6. ✅ تسجيل النشاط في Activity Log

---

## 🎨 واجهة المستخدم

### موقع الأزرار:
في صفحة المحادثات (`/agent/conversations/`)، في رأس قائمة المحادثات:

```
┌─────────────────────────────────┐
│ المحادثات              [+]     │
├─────────────────────────────────┤
│ [أخذ استراحة] [العودة للعمل]  │ ← الأزرار
├─────────────────────────────────┤
│ ⚠️ أنت في استراحة - لن تستقبل │ ← التنبيه
│    تذاكر جديدة                 │
├─────────────────────────────────┤
│ 🔍 ابحث عن محادثة...          │
└─────────────────────────────────┘
```

### حالات الأزرار:

| الحالة | زر "أخذ استراحة" | زر "العودة للعمل" | التنبيه |
|--------|------------------|-------------------|---------|
| يعمل | ✅ ظاهر | ❌ مخفي | ❌ مخفي |
| في استراحة | ❌ مخفي | ✅ ظاهر | ✅ ظاهر |

---

## ⚙️ التحديثات في الكود

### 1. **تحديث `get_available_agent()`**

**الملف:** `System/conversations/utils.py`

```python
def get_available_agent():
    """
    الحصول على موظف متاح باستخدام خوارزمية Least Loaded
    
    ✅ التحديث: استبعاد الموظفين في استراحة (is_on_break=True)
    """
    from .models import Agent
    from django.db.models import F

    # البحث عن موظف متاح (ليس في استراحة)
    available_agents = Agent.objects.filter(
        is_online=True,
        status='available',
        is_on_break=False,  # ✅ استبعاد الموظفين في استراحة
        current_active_tickets__lt=F('max_capacity')
    ).order_by('current_active_tickets')

    if available_agents.exists():
        return available_agents.first()

    return None
```

---

### 2. **تحديث AgentSerializer**

**الملف:** `System/conversations/serializers.py`

```python
class Meta:
    model = Agent
    fields = [
        'id', 'user', 'user_id', 'max_capacity', 'current_active_tickets',
        'is_online', 'status', 'total_messages_sent', 'total_messages_received',
        'is_on_break', 'break_started_at', 'total_break_minutes_today',  # ✅ حقول الاستراحة
        'available_capacity', 'is_available', 'created_at', 'updated_at'
    ]
    read_only_fields = [
        'id', 'current_active_tickets', 'total_messages_sent', 
        'total_messages_received', 'break_started_at', 'total_break_minutes_today',  # ✅ للقراءة فقط
        'created_at', 'updated_at'
    ]
```

---

### 3. **JavaScript Functions**

**الملف:** `System/templates/agent/conversations.html`

```javascript
// Check break status
function checkBreakStatus() {
    fetch('/api/agents/me/')
        .then(response => response.json())
        .then(data => {
            updateBreakUI(data.is_on_break);
        });
}

// Update UI
function updateBreakUI(isOnBreak) {
    if (isOnBreak) {
        // Show "Get Back" button and alert
        document.getElementById('takeBreakBtn').style.display = 'none';
        document.getElementById('endBreakBtn').style.display = 'block';
        document.getElementById('breakStatusAlert').style.display = 'block';
    } else {
        // Show "Take Break" button
        document.getElementById('takeBreakBtn').style.display = 'block';
        document.getElementById('endBreakBtn').style.display = 'none';
        document.getElementById('breakStatusAlert').style.display = 'none';
    }
}

// Take break
function takeBreak() {
    if (!confirm('هل تريد أخذ استراحة؟ لن تستقبل تذاكر جديدة حتى تعود.')) {
        return;
    }
    
    fetch('/api/agents/{{ request.user.agent.id }}/take_break/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBreakUI(true);
            showNotification('success', data.message);
        }
    });
}

// End break
function endBreak() {
    fetch('/api/agents/{{ request.user.agent.id }}/end_break/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBreakUI(false);
            showNotification('success', data.message);
            loadConversations(); // Reload to get new tickets
        }
    });
}
```

---

## 🧪 الاختبار

### تشغيل الاختبار:
```bash
cd System
python test_agent_break.py
```

### نتائج الاختبار:
```
✅ الاختبار 1: الموظفان متاحان
✅ الاختبار 2: تم العثور على موظف متاح
✅ الاختبار 3: تم وضع الموظف 1 في استراحة
✅ الاختبار 4: تم استبعاد الموظف 1 من التوزيع
✅ الاختبار 5: تم وضع جميع الموظفين في استراحة
✅ الاختبار 6: لا يوجد موظف متاح عندما الجميع في استراحة
✅ الاختبار 7: تم إنهاء استراحة الموظف 1 وحساب المدة
✅ الاختبار 8: تم العثور على موظف متاح بعد العودة

🎉 جميع الاختبارات نجحت!
```

---

## 📊 سير العمل

```
1. الموظف يضغط "أخذ استراحة"
   ↓
2. تأكيد من الموظف
   ↓
3. API Call: POST /api/agents/{id}/take_break/
   ↓
4. تحديث قاعدة البيانات:
   - is_on_break = True
   - break_started_at = الآن
   - status = 'on_break'
   ↓
5. تحديث الواجهة:
   - إخفاء زر "أخذ استراحة"
   - إظهار زر "العودة للعمل"
   - إظهار تنبيه الاستراحة
   ↓
6. ⏸️ الموظف في استراحة - لا يستقبل تذاكر جديدة
   ↓
7. الموظف يضغط "العودة للعمل"
   ↓
8. API Call: POST /api/agents/{id}/end_break/
   ↓
9. حساب مدة الاستراحة وتحديث قاعدة البيانات:
   - is_on_break = False
   - break_started_at = None
   - total_break_minutes_today += المدة
   - status = 'available' أو 'busy'
   ↓
10. تحديث الواجهة وإعادة تحميل المحادثات
    ↓
11. ▶️ الموظف يعمل - يستقبل تذاكر جديدة
```

---

## 🔒 الصلاحيات

### Endpoint `/api/agents/me/`
- ✅ يمكن للموظف الوصول إليه
- ✅ يعيد بيانات الموظف الحالي فقط

### Endpoints `/take_break/` و `/end_break/`
- ✅ يمكن للموظف التحكم في استراحته الخاصة
- ✅ يمكن للأدمن التحكم في استراحة أي موظف
- ❌ لا يمكن للموظف التحكم في استراحة موظف آخر

---

## 📁 الملفات المُعدلة

1. ✅ `System/conversations/models.py` - إضافة حقول الاستراحة
2. ✅ `System/conversations/utils.py` - تحديث `get_available_agent()`
3. ✅ `System/conversations/views.py` - إضافة endpoints
4. ✅ `System/conversations/serializers.py` - تحديث AgentSerializer
5. ✅ `System/templates/agent/conversations.html` - إضافة الأزرار والـ JavaScript
6. ✅ `System/conversations/migrations/0010_*.py` - Migration جديد

---

## 🚀 الحالة: **جاهز للإنتاج**

جميع التغييرات تم تطبيقها واختبارها بنجاح! ✅

