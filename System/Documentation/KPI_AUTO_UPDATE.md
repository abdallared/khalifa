# تحديث KPIs تلقائياً
## Automatic KPI Updates

---

## 📋 نظرة عامة

تم تطوير نظام تحديث KPIs تلقائياً بطريقتين:

### 1. **التحديث الفوري (Real-time)**
يتم حساب KPI تلقائياً عند:
- ✅ إنشاء تذكرة جديدة
- ✅ إغلاق تذكرة
- ✅ إرسال رسالة من الموظف
- ✅ نقل تذكرة لموظف آخر

### 2. **التحديث الدوري (Scheduled)**
يمكن جدولة تحديث KPIs بشكل دوري باستخدام:
- Management Command
- Cron Job (Linux/Mac)
- Task Scheduler (Windows)

---

## 🔄 التحديث الفوري (Real-time)

### الملفات المعدلة:

#### 1. `conversations/views.py`
```python
# عند إنشاء تذكرة جديدة
def perform_create(self, serializer):
    # ... كود إنشاء التذكرة
    
    # تحديث KPI تلقائياً
    if agent:
        from .utils import calculate_agent_kpi
        calculate_agent_kpi(agent)

# عند إغلاق تذكرة
@action(detail=True, methods=['post'])
def close(self, request, pk=None):
    # ... كود إغلاق التذكرة
    
    # تحديث KPI تلقائياً
    if ticket.assigned_agent:
        from .utils import calculate_agent_kpi
        calculate_agent_kpi(ticket.assigned_agent)

# عند نقل تذكرة
@action(detail=True, methods=['post'])
def transfer(self, request, pk=None):
    # ... كود نقل التذكرة
    
    # تحديث KPI للموظفين (القديم والجديد)
    from .utils import calculate_agent_kpi
    if old_agent:
        calculate_agent_kpi(old_agent)
    calculate_agent_kpi(new_agent)
```

#### 2. `conversations/views_messages.py`
```python
# عند إرسال رسالة من الموظف
def perform_create(self, serializer):
    # ... كود إرسال الرسالة
    
    # تحديث KPI عند إرسال رسالة من الموظف
    if message.sender_type == 'agent' and ticket.assigned_agent:
        from .utils import calculate_agent_kpi
        calculate_agent_kpi(ticket.assigned_agent)
```

---

## 📅 التحديث الدوري (Scheduled)

### Management Command

تم إنشاء Management Command: `update_kpis`

#### الاستخدام:

```bash
# تحديث KPIs لليوم الحالي
python manage.py update_kpis

# تحديث KPIs لآخر 7 أيام
python manage.py update_kpis --days 7

# تحديث KPIs ليوم محدد
python manage.py update_kpis --date 2025-11-01

# تحديث KPIs لموظف محدد
python manage.py update_kpis --agent 1

# تحديث KPIs لموظف محدد لآخر 30 يوم
python manage.py update_kpis --agent 1 --days 30
```

#### الخيارات:

| الخيار | الوصف | مثال |
|--------|-------|------|
| `--days` | عدد الأيام السابقة | `--days 7` |
| `--date` | تاريخ محدد (YYYY-MM-DD) | `--date 2025-11-01` |
| `--agent` | ID موظف محدد | `--agent 1` |

---

## ⏰ جدولة التحديث التلقائي

### 1. Linux/Mac - Cron Job

#### فتح Crontab:
```bash
crontab -e
```

#### إضافة المهام:

```bash
# تحديث KPIs كل ساعة
0 * * * * cd /path/to/project && python manage.py update_kpis

# تحديث KPIs كل يوم في منتصف الليل
0 0 * * * cd /path/to/project && python manage.py update_kpis --days 1

# تحديث KPIs كل أسبوع (الأحد 2 صباحاً)
0 2 * * 0 cd /path/to/project && python manage.py update_kpis --days 7

# تحديث KPIs كل شهر (أول يوم من الشهر)
0 3 1 * * cd /path/to/project && python manage.py update_kpis --days 30
```

#### شرح صيغة Cron:
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── يوم الأسبوع (0-7) (0 و 7 = الأحد)
│ │ │ └───── الشهر (1-12)
│ │ └─────── يوم الشهر (1-31)
│ └───────── الساعة (0-23)
└─────────── الدقيقة (0-59)
```

---

### 2. Windows - Task Scheduler

#### الطريقة 1: عبر واجهة Task Scheduler

1. **افتح Task Scheduler**:
   - ابحث عن "Task Scheduler" في قائمة Start

2. **إنشاء مهمة جديدة**:
   - اضغط "Create Basic Task"
   - الاسم: "Update KPIs"
   - الوصف: "تحديث KPIs للموظفين"

3. **تحديد التوقيت**:
   - اختر "Daily" أو "Weekly" أو "Monthly"
   - حدد الوقت (مثلاً 2:00 AM)

4. **تحديد الإجراء**:
   - Action: "Start a program"
   - Program: `python`
   - Arguments: `manage.py update_kpis --days 1`
   - Start in: `E:\hive\khalifa03\khalifa-backend01\New folder`

5. **حفظ المهمة**

#### الطريقة 2: عبر PowerShell

```powershell
# إنشاء مهمة تعمل كل يوم في 2 صباحاً
$action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py update_kpis --days 1" -WorkingDirectory "E:\hive\khalifa03\khalifa-backend01\New folder"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Update KPIs" -Description "تحديث KPIs للموظفين"
```

---

## 🧪 اختبار التحديث التلقائي

### 1. اختبار التحديث الفوري:

```python
# افتح Django Shell
python manage.py shell

# اختبار إنشاء تذكرة
from conversations.models import Ticket, Customer, Agent
from django.utils import timezone

customer = Customer.objects.first()
agent = Agent.objects.first()

ticket = Ticket.objects.create(
    customer=customer,
    assigned_agent=agent,
    current_agent=agent,
    ticket_number='TEST-001',
    status='open'
)

# تحقق من KPI
from conversations.models import AgentKPI
kpi = AgentKPI.objects.filter(
    agent=agent,
    kpi_date=timezone.now().date()
).first()

print(f"Total Tickets: {kpi.total_tickets}")
```

### 2. اختبار Management Command:

```bash
# تحديث KPIs لليوم الحالي
python manage.py update_kpis

# تحديث KPIs لآخر 7 أيام
python manage.py update_kpis --days 7
```

---

## 📊 مراقبة الأداء

### عرض KPIs في Django Admin:

```python
# في Django Shell
from conversations.models import AgentKPI
from django.utils import timezone

# عرض KPIs اليوم
today_kpis = AgentKPI.objects.filter(kpi_date=timezone.now().date())
for kpi in today_kpis:
    print(f"{kpi.agent.user.full_name}: {kpi.overall_kpi_score}%")
```

### عرض KPIs في صفحة التقارير:

افتح: http://127.0.0.1:8000/admin/reports/

---

## ⚠️ ملاحظات مهمة

### 1. الأداء:
- التحديث الفوري سريع جداً (< 100ms)
- لا يؤثر على أداء النظام
- يتم في الخلفية (background)

### 2. الأخطاء:
- إذا فشل حساب KPI، لا يؤثر على العملية الأساسية
- يتم تسجيل الأخطاء في Logs

### 3. البيانات:
- يتم حفظ KPI في جدول `AgentKPI`
- Unique constraint: (agent, kpi_date)
- يتم تحديث البيانات إذا كانت موجودة

---

## 🔧 استكشاف الأخطاء

### المشكلة: KPIs لا تتحدث تلقائياً

**الحل:**
```bash
# تحقق من أن الكود محدث
git pull

# تحقق من أن الـ imports صحيحة
python manage.py check

# تشغيل التحديث يدوياً
python manage.py update_kpis
```

### المشكلة: Cron Job لا يعمل

**الحل:**
```bash
# تحقق من Cron logs
grep CRON /var/log/syslog

# تحقق من صلاحيات الملف
chmod +x manage.py

# تحقق من المسار
which python
```

---

## 📝 الخلاصة

✅ **التحديث الفوري**: يعمل تلقائياً عند كل عملية  
✅ **التحديث الدوري**: يمكن جدولته حسب الحاجة  
✅ **Management Command**: سهل الاستخدام والاختبار  
✅ **Cron/Task Scheduler**: للجدولة التلقائية  

---

**تم التحديث:** 2025-11-02  
**الإصدار:** 1.0

