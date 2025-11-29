# 📊 تأثير وقت الاستراحة على KPI الموظفين

## 🎯 الهدف

**وقت الاستراحة يُحسب ضمن مؤشرات الأداء (KPI) للموظف**

عندما يأخذ الموظف استراحة، فإن الوقت الذي يقضيه في الاستراحة **يؤثر سلباً** على مؤشرات الأداء الخاصة به، خاصة:
- ⏱️ **وقت الاستجابة (Response Time)**
- 📈 **معدل الإنتاجية**
- 🎯 **KPI Score الإجمالي**

---

## 🔍 كيف يعمل النظام؟

### 1. **حساب وقت الاستجابة (Response Time)**

#### ✅ الطريقة الحالية (تشمل وقت الاستراحة):

```python
# في views_messages.py - عند أول رد من الموظف
if not ticket.first_response_at:
    ticket.first_response_at = timezone.now()
    
    if ticket.created_at:
        response_time = timezone.now() - ticket.created_at
        ticket.response_time_seconds = int(response_time.total_seconds())
```

**مثال:**
- 🕐 **10:00 AM** - العميل يرسل رسالة (تُنشأ التذكرة)
- 🕑 **10:05 AM** - الموظف يأخذ استراحة
- 🕒 **10:20 AM** - الموظف يعود من الاستراحة
- 🕓 **10:22 AM** - الموظف يرد على العميل

**النتيجة:**
```
Response Time = 10:22 AM - 10:00 AM = 22 دقيقة
```

✅ **وقت الاستراحة (15 دقيقة) محسوب ضمن الـ Response Time**

---

### 2. **تتبع وقت الاستراحة في KPI**

#### الحقول الجديدة في `AgentKPI`:

```python
class AgentKPI(models.Model):
    # ... الحقول الموجودة
    
    # ✅ حقول جديدة لتتبع الاستراحة
    total_break_time_seconds = models.IntegerField(default=0)  # إجمالي وقت الاستراحة (بالثواني)
    break_count = models.IntegerField(default=0)  # عدد مرات الاستراحة
```

#### جدول جديد: `AgentBreakSession`

```python
class AgentBreakSession(models.Model):
    """
    تتبع كل جلسة استراحة للموظف
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    break_start_time = models.DateTimeField()
    break_end_time = models.DateTimeField(null=True, blank=True)
    break_duration_seconds = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 3. **حساب KPI اليومي**

```python
def calculate_agent_kpi(agent, date=None):
    # ... حسابات أخرى
    
    # ✅ حساب إجمالي وقت الاستراحة في هذا اليوم
    break_sessions = AgentBreakSession.objects.filter(
        agent=agent,
        break_start_time__date=date,
        break_duration_seconds__isnull=False
    )
    
    total_break_time_seconds = break_sessions.aggregate(
        total=Sum('break_duration_seconds')
    )['total'] or 0
    
    break_count = break_sessions.count()
    
    # حفظ في KPI
    AgentKPI.objects.update_or_create(
        agent=agent,
        kpi_date=date,
        defaults={
            # ... حقول أخرى
            'total_break_time_seconds': total_break_time_seconds,
            'break_count': break_count,
        }
    )
```

---

## 📊 تأثير الاستراحة على المؤشرات

### 1. **Response Time (وقت الاستجابة)**

| السيناريو | Response Time | التأثير |
|-----------|---------------|---------|
| **بدون استراحة** | 5 دقائق | ✅ ممتاز |
| **مع استراحة 15 دقيقة** | 20 دقيقة | ⚠️ متوسط |
| **مع استراحة 30 دقيقة** | 35 دقيقة | ❌ ضعيف |

---

### 2. **First Response Rate (معدل الرد الأول)**

- إذا تأخر الموظف بسبب الاستراحة، قد تُعتبر التذكرة **متأخرة (Delayed)**
- التأخير يؤثر على `first_response_rate`

---

### 3. **Overall KPI Score**

```python
overall_kpi_score = (first_response_rate + resolution_rate + (satisfaction * 20)) / 3
```

- ⬇️ **Response Time أعلى** → First Response Rate أقل
- ⬇️ **First Response Rate أقل** → Overall KPI Score أقل

---

## 📈 مثال عملي

### موظف A (بدون استراحة):

```
التذاكر: 10
متوسط Response Time: 3 دقائق
First Response Rate: 100%
Resolution Rate: 90%
Satisfaction: 4.5/5

Overall KPI Score = (100 + 90 + (4.5 * 20)) / 3 = 93.33
```

### موظف B (مع استراحة 30 دقيقة):

```
التذاكر: 10
متوسط Response Time: 15 دقيقة (بسبب الاستراحة)
First Response Rate: 70% (بعض التذاكر تأخرت)
Resolution Rate: 90%
Satisfaction: 4.5/5

Overall KPI Score = (70 + 90 + (4.5 * 20)) / 3 = 83.33
```

**الفرق:** `-10 نقاط` بسبب الاستراحة!

---

## 🔧 التطبيق التقني

### 1. **عند بدء الاستراحة:**

```python
# في views.py - take_break()
agent.is_on_break = True
agent.break_started_at = timezone.now()
agent.status = 'on_break'
agent.save()
```

✅ **الموظف لا يستقبل تذاكر جديدة**

---

### 2. **عند العودة من الاستراحة:**

```python
# في views.py - end_break()
break_duration = timezone.now() - agent.break_started_at
break_seconds = int(break_duration.total_seconds())

# ✅ إنشاء سجل جلسة الاستراحة
AgentBreakSession.objects.create(
    agent=agent,
    break_start_time=agent.break_started_at,
    break_end_time=timezone.now(),
    break_duration_seconds=break_seconds
)

agent.is_on_break = False
agent.break_started_at = None
agent.status = 'available'
agent.save()
```

✅ **يتم تسجيل مدة الاستراحة**

---

### 3. **عند حساب KPI:**

```python
# في utils.py - calculate_agent_kpi()
total_break_time_seconds = AgentBreakSession.objects.filter(
    agent=agent,
    break_start_time__date=date
).aggregate(total=Sum('break_duration_seconds'))['total'] or 0

# يتم حفظه في AgentKPI
kpi.total_break_time_seconds = total_break_time_seconds
kpi.break_count = break_sessions.count()
```

✅ **يمكن عرض وقت الاستراحة في التقارير**

---

## 📋 API Response

### GET `/api/agents/kpi/?date=2025-11-10`

```json
{
  "id": 1,
  "agent": 5,
  "agent_name": "أحمد محمد",
  "kpi_date": "2025-11-10",
  "total_tickets": 15,
  "closed_tickets": 12,
  "avg_response_time_seconds": 900,
  "messages_sent": 45,
  "messages_received": 60,
  "delay_count": 2,
  "total_break_time_seconds": 1800,
  "break_count": 2,
  "customer_satisfaction_score": 4.5,
  "first_response_rate": 80.0,
  "resolution_rate": 80.0,
  "overall_kpi_score": 83.33
}
```

**تفسير:**
- `total_break_time_seconds: 1800` = 30 دقيقة استراحة
- `break_count: 2` = أخذ استراحتين
- `avg_response_time_seconds: 900` = 15 دقيقة متوسط (يشمل وقت الاستراحة)

---

## ✅ الخلاصة

### ما تم تنفيذه:

1. ✅ **إضافة حقول جديدة** في `AgentKPI`:
   - `total_break_time_seconds`
   - `break_count`

2. ✅ **إنشاء جدول جديد** `AgentBreakSession`:
   - تتبع كل جلسة استراحة
   - تسجيل وقت البداية والنهاية والمدة

3. ✅ **تحديث `calculate_agent_kpi()`**:
   - حساب إجمالي وقت الاستراحة
   - حفظه في KPI اليومي

4. ✅ **تحديث `end_break()`**:
   - إنشاء سجل `AgentBreakSession` عند العودة من الاستراحة

5. ✅ **Migration**:
   - `0011_agentkpi_break_count_and_more.py`

---

## 🎯 النتيجة النهائية

**وقت الاستراحة الآن:**
- ✅ **يُحسب ضمن Response Time** (تلقائياً)
- ✅ **يُسجل في KPI اليومي** (للتقارير)
- ✅ **يؤثر على Overall KPI Score** (بشكل سلبي)
- ✅ **يمكن تتبعه وتحليله** (عبر `AgentBreakSession`)

---

**🎊 تم التنفيذ بنجاح!**

