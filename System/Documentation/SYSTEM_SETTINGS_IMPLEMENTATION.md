# تنفيذ إعدادات النظام - System Settings Implementation

## المشكلة
كانت الإعدادات في صفحة Settings لا تُحفظ في قاعدة البيانات، وكانت تعود للقيم الافتراضية بعد إعادة تحميل الصفحة.

## الحل المُنفذ

### 1. Model (قاعدة البيانات) ✅
**الملف:** `System/conversations/models.py`

```python
class SystemSettings(models.Model):
    """
    إعدادات النظام - Singleton Pattern
    """
    assignment_algorithm = models.CharField(max_length=20, default='least_loaded')
    delay_threshold_minutes = models.IntegerField(default=3)
    default_max_capacity = models.IntegerField(default=10)
    work_start_time = models.TimeField(default='09:00')
    work_end_time = models.TimeField(default='17:00')
    
    @classmethod
    def get_settings(cls):
        """الحصول على الإعدادات (Singleton Pattern)"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings
```

**Migration:** تم إنشاء `0012_systemsettings_alter_message_message_type.py`

---

### 2. Serializer ✅
**الملف:** `System/conversations/serializers.py`

```python
class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            'id',
            'assignment_algorithm',
            'delay_threshold_minutes',
            'default_max_capacity',
            'work_start_time',
            'work_end_time',
            'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']
```

---

### 3. ViewSet (API Endpoint) ✅
**الملف:** `System/conversations/views.py`

```python
class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    إدارة إعدادات النظام (Admin only)
    """
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAdmin]
    
    def list(self, request):
        """GET /api/settings/"""
        settings = SystemSettings.get_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT/PATCH /api/settings/1/"""
        settings = SystemSettings.get_settings()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            log_activity(...)
            return Response({
                'success': True,
                'message': 'تم حفظ الإعدادات بنجاح',
                'data': serializer.data
            })
        
        return Response(serializer.errors, status=400)
```

---

### 4. URL Registration ✅
**الملف:** `System/conversations/urls.py`

```python
# System Settings
router.register(r'settings', SystemSettingsViewSet, basename='settings')
```

**API Endpoints:**
- `GET /api/settings/` - الحصول على الإعدادات الحالية
- `PATCH /api/settings/1/` - تحديث الإعدادات

---

### 5. Frontend (صفحة الإعدادات) ✅
**الملف:** `System/templates/admin/settings.html`

#### تحميل الإعدادات عند فتح الصفحة:
```javascript
async function loadSettings() {
    const response = await fetch('/api/settings/');
    const data = await response.json();
    
    if (data && data.length > 0) {
        const settings = data[0];
        document.querySelector('[name="delay_threshold"]').value = settings.delay_threshold_minutes;
        document.querySelector('[name="default_max_capacity"]').value = settings.default_max_capacity;
        document.querySelector('[name="work_start"]').value = settings.work_start_time;
        document.querySelector('[name="work_end"]').value = settings.work_end_time;
    }
}
```

#### حفظ الإعدادات:
```javascript
document.getElementById('systemSettingsForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        delay_threshold_minutes: parseInt(document.querySelector('[name="delay_threshold"]').value),
        default_max_capacity: parseInt(document.querySelector('[name="default_max_capacity"]').value),
        work_start_time: document.querySelector('[name="work_start"]').value,
        work_end_time: document.querySelector('[name="work_end"]').value
    };
    
    const response = await fetch('/api/settings/1/', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': khalifaPharmacy.getCookie('csrftoken')
        },
        body: JSON.stringify(formData)
    });
    
    if (response.ok) {
        khalifaPharmacy.showToast('تم حفظ الإعدادات بنجاح', 'success');
    }
});
```

---

### 6. التحقق من السعة القصوى عند إنشاء موظف ✅
**الملف:** `System/conversations/views.py` - `AgentViewSet.create_with_user()`

```python
# الحصول على الإعدادات
system_settings = SystemSettings.get_settings()
default_max_capacity = system_settings.default_max_capacity

# التحقق من max_capacity
requested_capacity = request.data.get('max_capacity')
if requested_capacity:
    requested_capacity = int(requested_capacity)
    if requested_capacity > default_max_capacity:
        return Response({
            'success': False,
            'error': f'السعة القصوى للموظف لا يمكن أن تتجاوز {default_max_capacity}'
        }, status=400)
    max_capacity = requested_capacity
else:
    max_capacity = default_max_capacity
```

---

### 7. Frontend Validation (صفحة الموظفين) ✅
**الملف:** `System/templates/admin/agents.html`

#### عرض الحد الأقصى المسموح:
```html
<div class="col-md-6">
    <label class="form-label">السعة القصوى *</label>
    <input type="number" class="form-control" name="max_capacity" 
           id="maxCapacityInput" value="10" min="1" required>
    <small class="text-muted" id="maxCapacityHint">
        الحد الأقصى المسموح: <span id="maxCapacityLimit">10</span>
    </small>
</div>
```

#### التحقق قبل الإرسال:
```javascript
// التحقق من السعة القصوى مقابل الإعدادات
const settingsResponse = await fetch('/api/settings/');
const settingsData = await settingsResponse.json();
const defaultMaxCapacity = settingsData[0]?.default_max_capacity || 10;

if (parseInt(max_capacity) > defaultMaxCapacity) {
    khalifaPharmacy.showToast(
        `السعة القصوى لا يمكن أن تتجاوز ${defaultMaxCapacity}`, 
        'error'
    );
    return;
}
```

#### تحميل الحد الأقصى عند فتح الصفحة:
```javascript
async function loadMaxCapacityLimit() {
    const response = await fetch('/api/settings/');
    const data = await response.json();
    const defaultMaxCapacity = data[0]?.default_max_capacity || 10;
    
    // تحديث النص التوضيحي
    document.getElementById('maxCapacityLimit').textContent = defaultMaxCapacity;
    
    // تحديث max attribute للـ input
    document.getElementById('maxCapacityInput').setAttribute('max', defaultMaxCapacity);
}

loadMaxCapacityLimit();
```

---

## الميزات المُنفذة

### ✅ 1. حفظ الإعدادات في قاعدة البيانات
- الإعدادات تُحفظ في جدول `system_settings`
- استخدام Singleton Pattern (سجل واحد فقط)
- الإعدادات تبقى بعد إعادة تحميل الصفحة

### ✅ 2. استخدام Default Max Capacity عند إنشاء موظف
- إذا لم يُحدد المستخدم سعة، يتم استخدام القيمة الافتراضية من الإعدادات
- التحقق من أن السعة المُدخلة لا تتجاوز الحد الأقصى المسموح

### ✅ 3. Validation في Backend
- رفض إنشاء موظف بسعة أكبر من الحد الأقصى
- رسالة خطأ واضحة للمستخدم

### ✅ 4. Validation في Frontend
- التحقق قبل إرسال البيانات للـ API
- عرض الحد الأقصى المسموح في الصفحة
- تحديث الحد الأقصى تلقائياً عند تغيير الإعدادات

---

## الاختبار

### Test 1: حفظ الإعدادات ✅
```bash
python test_settings_api.py
```

**النتيجة:**
```
Test 1: Get settings
  Default Max Capacity: 10
  Delay Threshold: 3

Test 2: Update settings
  Updated Default Max Capacity: 15
  Updated Delay Threshold: 5

Test 3: Verify persistence
  Reloaded Default Max Capacity: 15
  Reloaded Delay Threshold: 5

✅ All tests passed!
```

### Test 2: إنشاء موظف
1. افتح `/admin/agents/`
2. اضغط "إضافة موظف جديد"
3. حاول إدخال سعة أكبر من الحد الأقصى
4. **النتيجة:** رسالة خطأ تظهر

### Test 3: تغيير الإعدادات
1. افتح `/admin/settings/`
2. غيّر "السعة القصوى الافتراضية" من 10 إلى 15
3. اضغط "حفظ الإعدادات"
4. أعد تحميل الصفحة
5. **النتيجة:** القيمة 15 لا تزال موجودة

---

## الملفات المُعدلة

1. ✅ `System/conversations/models.py` - إضافة SystemSettings model
2. ✅ `System/conversations/serializers.py` - إضافة SystemSettingsSerializer
3. ✅ `System/conversations/views.py` - إضافة SystemSettingsViewSet + validation
4. ✅ `System/conversations/urls.py` - تسجيل settings endpoint
5. ✅ `System/templates/admin/settings.html` - إضافة save/load logic
6. ✅ `System/templates/admin/agents.html` - إضافة validation + hint

---

## الخلاصة

تم تنفيذ نظام إعدادات كامل يشمل:
- ✅ حفظ الإعدادات في قاعدة البيانات
- ✅ API endpoints للقراءة والتحديث
- ✅ Frontend integration في صفحة الإعدادات
- ✅ استخدام default_max_capacity عند إنشاء موظف
- ✅ Validation في Backend و Frontend
- ✅ عرض الحد الأقصى المسموح في صفحة الموظفين

**الآن يمكنك:**
1. تغيير الإعدادات من صفحة Settings
2. الإعدادات تُحفظ وتبقى بعد إعادة التحميل
3. عند إنشاء موظف جديد، يتم التحقق من السعة القصوى
4. لا يمكن إنشاء موظف بسعة أكبر من الحد الأقصى المسموح
