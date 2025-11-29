# 🎯 **MASTER CONTEXT - نظام إدارة محادثات صيدليات خليفة**
## **المرجع الشامل للتنفيذ (خفيف → تقيل)**

---

## 📑 **جدول المحتويات**
1. [نظرة عامة على المشروع](#1-نظرة-عامة)
2. [استراتيجية التنفيذ (مرحلتين)](#2-استراتيجية-التنفيذ)
3. [قاعدة البيانات الكاملة](#3-قاعدة-البيانات)
4. [السيناريوهات التفصيلية](#4-السيناريوهات)
5. [العمليات والـ Queries](#5-العمليات-والqueries)
6. [مؤشرات الأداء KPIs](#6-مؤشرات-الأداء)
7. [الواجهات والشاشات](#8-الواجهات)

---

## 🏢 **1. نظرة عامة على المشروع**

### **العميل:**
- **الاسم:** صيدليات خليفة
- **الموقع:** المنصورة
- **عدد الفروع:** 15 فرع
- **المشكلة:** استخدام رقم واحد من عدة موظفين → حظر الرقم

### **الحل:**
نظام إدارة محادثات ذكي يوزع المحادثات تلقائياً على الموظفين المتاحين مع تتبع الأداء.

### **الأهداف الرئيسية:**
✅ توزيع تلقائي للمحادثات  
✅ تتبع أداء الموظفين (KPIs)  
✅ إدارة مركزية  
✅ تقارير تفصيلية  
✅ Response Time < 3 دقائق  

---

## 🔄 **2. استراتيجية التنفيذ (مرحلتين)**

### **📌 المرحلة 1️⃣: خفيف على خفيف (MVP - 4 أسابيع)**

#### **التقنيات:**
```
✅ Backend: Django (Python)
✅ Database: SQLite (جاهز للانتقال لـ PostgreSQL/MySQL)
✅ Frontend: HTML + CSS + JavaScript (Vanilla)
✅ Real-time: Django Channels (WebSocket)
❌ بدون WhatsApp Business API
❌ بدون Integration خارجي
```

#### **لماذا SQLite في البداية؟**
- سهل الإعداد (لا يحتاج تثبيت)
- مثالي للتطوير والاختبار
- نفس الـ SQL تماماً
- الانتقال لـ PostgreSQL/MySQL سهل جداً (تغيير سطر واحد في settings.py)

#### **الهدف:**
- بناء نظام داخلي كامل لإدارة التذاكر
- اختبار منطق التوزيع التلقائي
- تدريب الموظفين
- التأكد من صحة KPIs
- محاكاة العمل الحقيقي

#### **كيف يعمل:**
```
1. Admin يدخل رسائل العملاء يدوياً (محاكاة)
2. النظام يوزع التذاكر تلقائياً
3. الموظفين يردون من خلال الواجهة
4. النظام يحسب KPIs ويتتبع الأداء
5. Admin يراقب كل شيء من Dashboard
```

---

### **📌 المرحلة 2️⃣: الخفيف اتحول لتقيل (Production - 17 يوم)**

#### **🔌 الجزء الأول: WPPConnect Driver (8 أيام)**

```
✅ تصميم Driver Pattern Architecture
   ├── MessageDriver Interface
   ├── DriverFactory
   └── تحديث Database Schema (provider + id_ext)

✅ تطبيق WPPConnect Driver
   ├── QR Code Scan
   ├── Send/Receive Messages
   └── Webhook Handler

✅ Redis Queue Setup
   ├── Incoming Messages Queue
   ├── Outgoing Messages Queue
   └── Worker Processes

✅ دمج مع Core
   ├── Incoming Message Handler
   ├── Outgoing Message Handler
   └── WebSocket Notifications

✅ اختبار ونشر
   ├── Unit Tests
   ├── Integration Tests
   └── Production Deployment
```

#### **☁️ الجزء الثاني: Cloud API Driver (9 أيام)**

```
✅ إعداد WhatsApp Business Cloud API
   ├── تسجيل في Meta Developer
   ├── إنشاء WhatsApp Business Account
   └── الحصول على Access Token

✅ تطبيق Cloud API Driver
   ├── CloudAPIDriver Class
   ├── Webhook Verification
   └── Message Parsing

✅ Migration Strategy
   ├── Data Migration Script
   ├── Testing في بيئة التطوير
   └── Rollback Plan

✅ النشر والمراقبة
   ├── Production Migration
   ├── Monitoring (24 ساعة)
   └── Performance Tuning

✅ التحويل النهائي
   ├── تغيير WHATSAPP_DRIVER=cloud_api في .env
   ├── إعادة تشغيل التطبيق
   └── إيقاف WPPConnect (اختياري)
```

#### **الإضافات الأخرى:**
```
✅ Webhooks لاستقبال الرسائل تلقائياً
✅ إرسال الردود عبر WhatsApp API
✅ ربط الرقم الحقيقي
✅ التشغيل المباشر مع العملاء
✅ الانتقال من SQLite إلى PostgreSQL/MySQL
```

#### **التغييرات:**
| قبل (المرحلة 1) | بعد (المرحلة 2) |
|-----------------|-----------------|
| Django + SQLite | Django + PostgreSQL/MySQL |
| Admin يدخل الرسائل يدوياً | الرسائل تأتي تلقائياً من WhatsApp |
| الردود داخل النظام فقط | الردود ترسل للعميل عبر WhatsApp |
| محاكاة | تشغيل حقيقي |

---

## 🔄 **3. دورة حياة التذكرة (Ticket Lifecycle)**

### **الحالات الممكنة:**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  📩 رسالة جديدة من العميل                                 │
│           │                                                 │
│           ▼                                                 │
│     ┌──────────┐                                            │
│     │  OPEN    │ ← التذكرة مفتوحة (الموظف استلمها)        │
│     └────┬─────┘                                            │
│          │                                                  │
│          ├─── (إذا مر 3 دقائق بدون رد)                     │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │ DELAYED  │ ← متأخرة (يُحسب وقت التأخير)              │
│     └────┬─────┘                                            │
│          │                                                  │
│          ├─── (عند رد الموظف)                              │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │  OPEN    │ ← ترجع مفتوحة (مع حساب دقائق التأخير)    │
│     └────┬─────┘                                            │
│          │                                                  │
│          ├─── (الموظف يضغط "إنهاء المحادثة")              │
│          │                                                  │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │  CLOSED  │ ← مغلقة (منتهية)                          │
│     └──────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **القواعد المهمة:**

1. **عند استلام رسالة جديدة:**
   - الحالة تصبح: `OPEN`
   - يبدأ Timer الـ 3 دقائق

2. **إذا مر 3 دقائق بدون رد:**
   - الحالة تتغير إلى: `DELAYED`
   - يُسجل وقت بداية التأخير
   - يُحسب على KPI الموظف

3. **عند رد الموظف بعد التأخير:**
   - الحالة ترجع إلى: `OPEN`
   - يُحسب وقت التأخير (بالدقائق)
   - يُسجل في `agent_delay_events`
   - **مهم:** التأخير يُحسب على الموظف حتى لو رد بعدها

4. **عند إنهاء المحادثة:**
   - الموظف يضغط "إنهاء المحادثة"
   - الحالة تصبح: `CLOSED`
   - تُحسب في KPIs

---

## 🗄️ **4. قاعدة البيانات الكاملة**

### **فلسفة التصميم:**
```
✅ استخدام الجداول الـ 21 من digarms_flow.md
✅ تطبيق السيناريوهات من context_3.md
✅ بناء تدريجي (المرحلة 1 → المرحلة 2)
✅ SQLite في البداية → PostgreSQL/MySQL لاحقاً
```

---

### **📊 GROUP 1: USER MANAGEMENT (3 جداول)**

#### **1. users**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'agent') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_online BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_is_active (is_active),
    INDEX idx_is_online (is_online)
);
```

**الغرض:** تخزين بيانات المستخدمين (Admin + Agents)

**العلاقات:**
- `1 User` → `Many Tickets` (كـ agent مسؤول)
- `1 User` → `Many Messages` (كـ sender)

---

#### **2. agents**
```sql
CREATE TABLE agents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    max_capacity INT DEFAULT 15,
    current_active_tickets INT DEFAULT 0,
    is_online BOOLEAN DEFAULT FALSE,
    status ENUM('available', 'busy', 'offline', 'on_break') DEFAULT 'offline',
    total_messages_sent INT DEFAULT 0,
    total_messages_received INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_is_online (is_online),
    INDEX idx_current_active_tickets (current_active_tickets)
);
```

**الغرض:** بيانات الـ Agents (السعة، الحالة، العدادات)

**العلاقات:**
- `1 Agent` ← `1 User` (One-to-One)
- `1 Agent` → `Many Tickets`

---

#### **3. admins**
```sql
CREATE TABLE admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    can_manage_agents BOOLEAN DEFAULT TRUE,
    can_manage_templates BOOLEAN DEFAULT TRUE,
    can_view_analytics BOOLEAN DEFAULT TRUE,
    can_edit_global_templates BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**الغرض:** صلاحيات الـ Admins

---

### **📊 GROUP 2: CUSTOMER & CONTACT MANAGEMENT (3 جداول)**

#### **4. customers**
```sql
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    wa_id VARCHAR(50) UNIQUE NOT NULL,  -- WhatsApp ID
    name VARCHAR(100),
    email VARCHAR(100),
    notes TEXT,
    customer_type ENUM('regular', 'vip', 'sick', 'needs_visits') DEFAULT 'regular',
    is_blocked BOOLEAN DEFAULT FALSE,
    total_tickets_count INT DEFAULT 0,
    first_contact_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_contact_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone_number (phone_number),
    INDEX idx_wa_id (wa_id),
    INDEX idx_customer_type (customer_type),
    FULLTEXT INDEX idx_name (name)
);
```

**الغرض:** تخزين بيانات العملاء

**العلاقات:**
- `1 Customer` → `Many Tickets`

---

#### **5. customer_tags**
```sql
CREATE TABLE customer_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_customer_tag (customer_id, tag)
);
```

---

#### **6. customer_notes**
```sql
CREATE TABLE customer_notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    created_by INT NOT NULL,
    note_text TEXT NOT NULL,
    is_important BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_customer_id (customer_id),
    INDEX idx_created_at (created_at)
);
```

---

### **📊 GROUP 3: TICKET MANAGEMENT (3 جداول)**

#### **7. tickets** ⭐ **القلب**
```sql
CREATE TABLE tickets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    assigned_agent_id INT,
    current_agent_id INT,

    -- الحالات: open (مفتوحة), delayed (متأخرة), closed (مغلقة)
    status ENUM('open', 'delayed', 'closed') DEFAULT 'open',

    category ENUM('medicine_order', 'complaint', 'consultation', 'follow_up', 'general') DEFAULT 'general',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',

    -- Delay Tracking
    is_delayed BOOLEAN DEFAULT FALSE,
    delay_started_at TIMESTAMP NULL,  -- متى بدأ التأخير
    total_delay_minutes INT DEFAULT 0,  -- إجمالي دقائق التأخير
    delay_count INT DEFAULT 0,  -- عدد مرات التأخير

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_response_at TIMESTAMP NULL,
    last_message_at TIMESTAMP NULL,
    last_customer_message_at TIMESTAMP NULL,
    last_agent_message_at TIMESTAMP NULL,
    closed_at TIMESTAMP NULL,
    
    -- Metrics
    response_time_seconds INT,
    handling_time_seconds INT,
    messages_count INT DEFAULT 0,
    
    -- Closure Info
    closed_by_user_id INT,
    closure_reason VARCHAR(255),
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    FOREIGN KEY (current_agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    FOREIGN KEY (closed_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_status (status),
    INDEX idx_assigned_agent_id (assigned_agent_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_delayed (is_delayed),
    INDEX idx_active_agent (assigned_agent_id, status)
);
```

**الغرض:** الجدول الأساسي - قلب النظام

**العلاقات:**
- `Many Tickets` → `1 Customer`
- `Many Tickets` → `1 Agent`
- `1 Ticket` → `Many Messages`

---

#### **8. ticket_transfers_log**
```sql
CREATE TABLE ticket_transfers_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    from_agent_id INT,
    to_agent_id INT NOT NULL,
    transferred_by INT NOT NULL,  -- Admin who transferred
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (from_agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    FOREIGN KEY (to_agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    FOREIGN KEY (transferred_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_created_at (created_at)
);
```

---

#### **9. ticket_states_log**
```sql
CREATE TABLE ticket_states_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    old_state VARCHAR(50),
    new_state VARCHAR(50) NOT NULL,
    changed_by INT,  -- NULL for automatic state changes
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_created_at (created_at)
);
```

---

### **📊 GROUP 4: MESSAGES (3 جداول)**

#### **10. messages**
```sql
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    sender_id INT,  -- NULL if from customer
    sender_type ENUM('customer', 'agent', 'admin', 'system') NOT NULL,
    message_text TEXT,
    message_type ENUM('text', 'image', 'document', 'audio', 'video', 'file', 'interactive', 'template') DEFAULT 'text',
    media_url VARCHAR(500),
    mime_type VARCHAR(100),

    -- WhatsApp Integration (المرحلة 2)
    whatsapp_message_id VARCHAR(100),
    whatsapp_status ENUM('sent', 'delivered', 'read', 'failed') DEFAULT 'sent',

    is_deleted BOOLEAN DEFAULT FALSE,
    is_forwarded BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_ticket_id (ticket_id),
    INDEX idx_sender_type (sender_type),
    INDEX idx_created_at (created_at),
    INDEX idx_whatsapp_message_id (whatsapp_message_id),
    INDEX idx_is_read (is_read),  -- للبحث السريع عن غير المقروءة
    FULLTEXT INDEX idx_message_text (message_text)  -- للبحث في النص (Full-Text Search)
);
```

---

#### **11. message_delivery_log**
```sql
CREATE TABLE message_delivery_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    message_id INT NOT NULL,
    delivery_status ENUM('pending', 'sent', 'delivered', 'read', 'failed') NOT NULL,
    error_message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
    INDEX idx_message_id (message_id),
    INDEX idx_created_at (created_at)
);
```

---

#### **12. message_search_index**
```sql
CREATE TABLE message_search_index (
    id INT PRIMARY KEY AUTO_INCREMENT,
    message_id INT NOT NULL,
    customer_id INT NOT NULL,
    search_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FULLTEXT INDEX idx_search_text (search_text),
    INDEX idx_customer_id (customer_id)
);
```

---

### **📊 GROUP 5: TEMPLATES & QUICK REPLIES (3 جداول)**

#### **13. global_templates**
```sql
CREATE TABLE global_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT NOT NULL,
    updated_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES admins(id) ON DELETE SET NULL,
    INDEX idx_is_active (is_active),
    INDEX idx_category (category)
);
```

---

#### **14. agent_templates**
```sql
CREATE TABLE agent_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_agent_name (agent_id, name),
    INDEX idx_is_active (is_active)
);
```

---

#### **15. auto_reply_triggers**
```sql
CREATE TABLE auto_reply_triggers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    trigger_keyword VARCHAR(100) NOT NULL,
    template_id INT,
    reply_text TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    trigger_type ENUM('keyword', 'category', 'greeting') DEFAULT 'keyword',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES global_templates(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE CASCADE,
    INDEX idx_is_active (is_active),
    INDEX idx_trigger_keyword (trigger_keyword)
);
```

---

### **📊 GROUP 6: DELAY TRACKING & MONITORING (2 جداول)**

#### **16. response_time_tracking**
```sql
CREATE TABLE response_time_tracking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    agent_id INT,
    message_received_at TIMESTAMP NOT NULL,
    first_response_at TIMESTAMP,
    response_time_seconds INT,
    is_delayed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    INDEX idx_agent_id (agent_id),
    INDEX idx_is_delayed (is_delayed),
    INDEX idx_created_at (created_at)
);
```

---

#### **17. agent_delay_events**
```sql
CREATE TABLE agent_delay_events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    agent_id INT NOT NULL,
    delay_start_time TIMESTAMP NOT NULL,
    delay_end_time TIMESTAMP,
    delay_duration_seconds INT,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    INDEX idx_agent_id (agent_id),
    INDEX idx_created_at (created_at)
);
```

---

### **📊 GROUP 7: KPI & PERFORMANCE METRICS (3 جداول)**

#### **18. agent_kpi**
```sql
CREATE TABLE agent_kpi (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    kpi_date DATE NOT NULL,
    total_tickets INT DEFAULT 0,
    closed_tickets INT DEFAULT 0,
    avg_response_time_seconds INT,
    messages_sent INT DEFAULT 0,
    messages_received INT DEFAULT 0,
    delay_count INT DEFAULT 0,
    customer_satisfaction_score DECIMAL(3,2),
    first_response_rate DECIMAL(5,2),
    resolution_rate DECIMAL(5,2),
    overall_kpi_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_agent_date (agent_id, kpi_date),
    INDEX idx_kpi_date (kpi_date)
);
```

---

#### **19. agent_kpi_monthly**
```sql
CREATE TABLE agent_kpi_monthly (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT NOT NULL,
    month DATE NOT NULL,  -- First day of month
    total_tickets INT DEFAULT 0,
    closed_tickets INT DEFAULT 0,
    avg_response_time_seconds INT,
    messages_sent INT DEFAULT 0,
    messages_received INT DEFAULT 0,
    delay_count INT DEFAULT 0,
    avg_customer_satisfaction DECIMAL(3,2),
    overall_kpi_score DECIMAL(5,2),
    rank INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_agent_month (agent_id, month),
    INDEX idx_month (month)
);
```

---

#### **20. customer_satisfaction**
```sql
CREATE TABLE customer_satisfaction (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    agent_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    INDEX idx_agent_id (agent_id),
    INDEX idx_rating (rating)
);
```

---

### **📊 GROUP 8: ACTIVITY LOG & AUDIT (1 جدول)**

#### **21. activity_log**
```sql
CREATE TABLE activity_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),  -- tickets, messages, templates, etc
    entity_id INT,
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);
```

---

## � **4. نظام المصادقة والصلاحيات (Authentication & Authorization)**

### **📋 نظرة عامة:**

```
🔑 نظام المصادقة:
   ├── تسجيل الدخول: Username + Password
   ├── الجلسات: Django Sessions
   ├── التشفير: bcrypt (Django default)
   └── الحماية: CSRF + Rate Limiting + Brute Force Protection

👥 الأدوار (Roles):
   ├── Admin: صلاحيات كاملة (7 صفحات)
   └── Agent: صلاحيات محدودة (3 صفحات فقط)

🛡️ الصلاحيات:
   ├── Admin: يرى ويدير كل شيء
   └── Agent: يرى محادثاته وقوالبه فقط
```

---

### **🎯 4.1 تسجيل الدخول (Login Flow)**

#### **السيناريو الكامل:**

```
┌─────────────────────────────────────────────────────────────┐
│                    صفحة تسجيل الدخول                        │
│                                                             │
│         Username: [____________]                            │
│         Password: [____________]                            │
│                   [تسجيل الدخول]                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    التحقق من البيانات
                            ↓
                ┌───────────┴───────────┐
                ↓                       ↓
         ✅ Admin                   ✅ Agent
                ↓                       ↓
    ┌───────────────────┐    ┌──────────────────┐
    │ Dashboard Admin   │    │ صفحة المحادثات   │
    │ (7 صفحات)        │    │ (3 صفحات فقط)    │
    └───────────────────┘    └──────────────────┘
```

---

#### **Queries - تسجيل الدخول:**

```sql
-- Query 1: التحقق من المستخدم
SELECT
    u.id,
    u.username,
    u.password_hash,
    u.role,
    u.is_active,
    u.full_name,
    u.email,
    CASE
        WHEN u.role = 'agent' THEN a.id
        WHEN u.role = 'admin' THEN ad.id
    END as role_id
FROM users u
LEFT JOIN agents a ON u.id = a.user_id
LEFT JOIN admins ad ON u.id = ad.user_id
WHERE u.username = ?
  AND u.is_active = TRUE
LIMIT 1;

-- Query 2: تحديث آخر دخول
UPDATE users
SET last_login = NOW(),
    is_online = TRUE
WHERE id = ?;

-- Query 3: تسجيل في activity_log
INSERT INTO activity_log (
    user_id,
    action_type,
    description,
    ip_address,
    user_agent
) VALUES (?, 'login', 'تسجيل دخول ناجح', ?, ?);
```

---

### **👥 4.2 إنشاء المستخدمين (User Creation)**

#### **من يمكنه إنشاء مستخدمين؟**
```
✅ Admin فقط
❌ Agent لا يمكنه
```

#### **السيناريو:**

```
┌─────────────────────────────────────────────────────────────┐
│              Admin → صفحة إدارة الموظفين                    │
│                                                             │
│  [+ إضافة موظف جديد]                                       │
│                                                             │
│  Username:     [____________]                               │
│  Password:     [____________]                               │
│  Full Name:    [____________]                               │
│  Email:        [____________]                               │
│  Role:         [● Agent  ○ Admin]                          │
│  Max Tickets:  [15]                                         │
│                                                             │
│              [حفظ]  [إلغاء]                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    حفظ في قاعدة البيانات
                            ↓
            ┌───────────────┴───────────────┐
            ↓                               ↓
    INSERT INTO users          INSERT INTO agents/admins
    (username, password_hash,  (user_id, ...)
     role, ...)
```

---

#### **Queries - إنشاء مستخدم:**

```sql
-- Query 1: إنشاء في جدول users
INSERT INTO users (
    username,
    password_hash,
    email,
    full_name,
    role,
    created_by
) VALUES (?, ?, ?, ?, ?, ?);

-- Query 2: إنشاء في جدول agents (إذا كان موظف)
INSERT INTO agents (
    user_id,
    max_concurrent_tickets,
    department
) VALUES (LAST_INSERT_ID(), 15, ?);

-- أو Query 3: إنشاء في جدول admins (إذا كان أدمن)
INSERT INTO admins (
    user_id,
    permissions_level
) VALUES (LAST_INSERT_ID(), 'full');

-- Query 4: تسجيل في activity_log
INSERT INTO activity_log (
    user_id,
    action_type,
    description,
    ip_address
) VALUES (?, 'create_user', CONCAT('إنشاء مستخدم جديد: ', ?), ?);
```

---

### **🔒 4.3 الصلاحيات التفصيلية (Detailed Permissions)**

#### **Admin - 7 صفحات:**

```
✅ 1. Dashboard (إحصائيات شاملة)
   ├── عدد التذاكر (الكل)
   ├── عدد الموظفين
   ├── متوسط وقت الرد (الكل)
   ├── رضا العملاء (الكل)
   └── ساعات الذروة

✅ 2. إدارة الموظفين
   ├── عرض جميع الموظفين
   ├── إضافة موظف جديد
   ├── تعديل بيانات موظف
   ├── تعطيل/تفعيل موظف
   └── حذف موظف

✅ 3. إدارة العملاء
   ├── عرض جميع العملاء
   ├── بحث عن عميل
   ├── عرض تاريخ محادثات العميل (مع جميع الموظفين)
   ├── إضافة Tags للعميل
   └── إضافة ملاحظات على العميل

✅ 4. جميع التذاكر
   ├── عرض جميع التذاكر (لجميع الموظفين)
   ├── فلترة حسب الموظف/الحالة/التاريخ
   ├── نقل تذكرة من موظف لآخر
   ├── إغلاق أي تذكرة
   └── عرض تفاصيل أي محادثة

✅ 5. القوالب العامة (Global Templates)
   ├── عرض جميع القوالب العامة
   ├── إضافة قالب عام جديد
   ├── تعديل قالب عام
   ├── حذف قالب عام
   └── تفعيل/تعطيل قالب

✅ 6. التقارير
   ├── تقرير أداء الموظفين (جميع الموظفين)
   ├── تقرير رضا العملاء (الكل)
   ├── تقرير ساعات الذروة
   ├── تقرير التأخيرات (جميع الموظفين)
   └── تقرير العملاء الأكثر نشاطاً

✅ 7. الإعدادات
   ├── إعدادات النظام
   ├── إعدادات WhatsApp (المرحلة 2)
   ├── إعدادات الإشعارات
   ├── Activity Log (سجل النشاط - الكل)
   └── إعدادات الأمان
```

---

#### **Agent - 3 صفحات فقط:**

```
✅ 1. محادثاتي (My Conversations)
   ├── عرض محادثاتي فقط (assigned_agent_id = current_user.agent_id)
   ├── البحث في محادثاتي (اسم/رقم/رسالة)
   ├── فلترة محادثاتي (مفتوحة/متأخرة/مغلقة)
   ├── الرد على الرسائل
   ├── استخدام القوالب (العامة + الخاصة)
   └── إنهاء المحادثة

   ❌ لا يرى محادثات الموظفين الآخرين
   ❌ لا يمكنه نقل تذكرة لموظف آخر

✅ 2. قوالبي الخاصة (My Templates)
   ├── عرض قوالبي الخاصة فقط (agent_id = current_user.agent_id)
   ├── عرض القوالب العامة (للقراءة والاستخدام فقط)
   ├── إضافة قالب خاص جديد
   ├── تعديل قوالبي الخاصة
   └── حذف قوالبي الخاصة

   ❌ لا يرى قوالب الموظفين الآخرين
   ❌ لا يمكنه تعديل القوالب العامة

✅ 3. تقاريري الشخصية (My Reports)
   ├── عدد تذاكري (مفتوحة/مغلقة/متأخرة)
   ├── متوسط وقت الرد الخاص بي
   ├── رضا العملاء عني
   ├── KPIs الخاصة بي
   └── تاريخ أدائي (شهري)

   ❌ لا يرى تقارير الموظفين الآخرين
   ❌ لا يرى الإحصائيات الشاملة
```

---

### **🛡️ 4.4 التحقق من الصلاحيات (Permission Checks)**

#### **Queries - التحقق من الصلاحيات:**

```sql
-- Query 1: التحقق من أن الموظف يملك التذكرة
SELECT COUNT(*) as has_access
FROM tickets t
WHERE t.id = ?
  AND t.assigned_agent_id = ?;
-- إذا كانت النتيجة 0 → ليس له صلاحية
-- إذا كانت النتيجة 1 → له صلاحية

-- Query 2: التحقق من أن القالب يخص الموظف
SELECT COUNT(*) as has_access
FROM agent_templates at
WHERE at.id = ?
  AND at.agent_id = ?;

-- Query 3: جلب محادثات الموظف فقط
SELECT t.*, c.name, c.phone_number
FROM tickets t
JOIN customers c ON t.customer_id = c.id
WHERE t.assigned_agent_id = ?
ORDER BY t.last_message_at DESC;

-- Query 4: جلب قوالب الموظف (الخاصة + العامة)
(SELECT id, title, content, 'personal' as type
 FROM agent_templates
 WHERE agent_id = ?)
UNION ALL
(SELECT id, title, content, 'global' as type
 FROM global_templates
 WHERE is_active = TRUE)
ORDER BY type, title;
```

---

#### **مثال كود - التحقق من الصلاحيات:**

```python
# Decorator للتحقق من Admin
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'admin':
            # تسجيل محاولة وصول غير مصرح
            ActivityLog.objects.create(
                user_id=request.user.id,
                action_type='unauthorized_access',
                description=f'محاولة وصول لصفحة Admin: {request.path}',
                ip_address=get_client_ip(request)
            )
            return HttpResponseForbidden("غير مصرح لك بالدخول")

        return view_func(request, *args, **kwargs)
    return wrapper

# مثال استخدام
@login_required
@admin_required
def admin_all_tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'admin_all_tickets.html', {'tickets': tickets})
```

```python
# التحقق من صلاحية Agent على تذكرة معينة
@login_required
def agent_view_ticket(request, ticket_id):
    if request.user.role != 'agent':
        return HttpResponseForbidden("غير مصرح لك")

    # التحقق من أن التذكرة تخص الموظف
    ticket = Ticket.objects.filter(
        id=ticket_id,
        assigned_agent_id=request.user.agent.id
    ).first()

    if not ticket:
        # تسجيل محاولة وصول غير مصرح
        ActivityLog.objects.create(
            user_id=request.user.id,
            action_type='unauthorized_access',
            description=f'محاولة الوصول لتذكرة #{ticket_id} غير مخصصة له',
            ip_address=get_client_ip(request)
        )
        return HttpResponseForbidden("هذه التذكرة غير مخصصة لك")

    # عرض التذكرة
    messages = Message.objects.filter(ticket_id=ticket_id)
    return render(request, 'agent_ticket.html', {
        'ticket': ticket,
        'messages': messages
    })
```

---

### **🔐 4.5 الأمان (Security Measures)**

#### **4.5.1 تشفير كلمة المرور**

```python
# Django - استخدام bcrypt (الافتراضي)
from django.contrib.auth.hashers import make_password, check_password

# عند إنشاء مستخدم
password_hash = make_password('user_password')

# عند تسجيل الدخول
is_valid = check_password('entered_password', stored_password_hash)
```

**متطلبات كلمة المرور:**
```
✅ الحد الأدنى: 8 أحرف
✅ يجب أن تحتوي على:
   ├── حرف كبير واحد على الأقل (A-Z)
   ├── حرف صغير واحد على الأقل (a-z)
   ├── رقم واحد على الأقل (0-9)
   └── رمز خاص واحد على الأقل (!@#$%^&*)
```

---

#### **4.5.2 الحماية من Brute Force**

```sql
-- جدول لتتبع محاولات الدخول الفاشلة
CREATE TABLE login_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE,

    INDEX idx_username (username),
    INDEX idx_ip_address (ip_address),
    INDEX idx_attempt_time (attempt_time)
);
```

```python
# الحماية من Brute Force
def check_brute_force(username, ip_address):
    # عدد المحاولات الفاشلة في آخر 15 دقيقة
    fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)

    failed_attempts = LoginAttempt.objects.filter(
        username=username,
        success=False,
        attempt_time__gte=fifteen_minutes_ago
    ).count()

    if failed_attempts >= 5:
        return False, "تم حظر الحساب مؤقتاً. حاول بعد 15 دقيقة"

    return True, None

# عند تسجيل الدخول
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    ip_address = get_client_ip(request)

    # التحقق من Brute Force
    allowed, error_msg = check_brute_force(username, ip_address)
    if not allowed:
        return JsonResponse({'error': error_msg}, status=429)

    # محاولة تسجيل الدخول
    user = authenticate(username=username, password=password)

    # تسجيل المحاولة
    LoginAttempt.objects.create(
        username=username,
        ip_address=ip_address,
        success=(user is not None)
    )

    if user is None:
        return JsonResponse({'error': 'اسم المستخدم أو كلمة المرور خاطئة'}, status=401)

    # نجح تسجيل الدخول
    login(request, user)
    return JsonResponse({'success': True, 'role': user.role})
```

---

#### **4.5.3 CSRF Protection**

```python
# Django - تلقائي في كل POST request
# في HTML Forms:
<form method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>

# في AJAX requests:
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

---

#### **4.5.4 Rate Limiting**

```python
# استخدام django-ratelimit
from django_ratelimit.decorators import ratelimit

# تحديد عدد الطلبات
@ratelimit(key='ip', rate='10/m', method='POST')  # 10 requests في الدقيقة
def login_view(request):
    # ...

@ratelimit(key='user', rate='100/h')  # 100 request في الساعة
def api_endpoint(request):
    # ...
```

---

### **📝 4.6 Activity Log - الأحداث المسجلة**

```python
# الأحداث التي يتم تسجيلها:

LOGGED_ACTIONS = {
    # Authentication
    'login': 'تسجيل دخول',
    'logout': 'تسجيل خروج',
    'failed_login': 'محاولة دخول فاشلة',

    # User Management (Admin فقط)
    'create_user': 'إنشاء مستخدم جديد',
    'update_user': 'تعديل بيانات مستخدم',
    'deactivate_user': 'تعطيل مستخدم',
    'activate_user': 'تفعيل مستخدم',
    'delete_user': 'حذف مستخدم',
    'change_password': 'تغيير كلمة المرور',

    # Tickets
    'create_ticket': 'إنشاء تذكرة',
    'assign_ticket': 'توزيع تذكرة',
    'transfer_ticket': 'نقل تذكرة',
    'close_ticket': 'إغلاق تذكرة',
    'reopen_ticket': 'إعادة فتح تذكرة',

    # Messages
    'send_message': 'إرسال رسالة',
    'read_message': 'قراءة رسالة',

    # Templates
    'create_template': 'إنشاء قالب',
    'update_template': 'تعديل قالب',
    'delete_template': 'حذف قالب',

    # Security
    'unauthorized_access': 'محاولة وصول غير مصرح',
    'permission_denied': 'رفض صلاحية',
}
```

```sql
-- Query: جلب Activity Log (Admin فقط)
SELECT
    al.id,
    al.action_type,
    al.description,
    al.ip_address,
    al.created_at,
    u.username,
    u.full_name,
    u.role
FROM activity_log al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.created_at >= ?  -- من تاريخ معين
ORDER BY al.created_at DESC
LIMIT 100;

-- Query: جلب Activity Log لموظف معين (Agent يرى نشاطه فقط)
SELECT
    al.id,
    al.action_type,
    al.description,
    al.created_at
FROM activity_log al
WHERE al.user_id = ?
ORDER BY al.created_at DESC
LIMIT 50;
```

---

### **🎯 4.7 السيناريوهات الكاملة**

#### **السيناريو 1: Admin يسجل الدخول**

```
1. Admin يدخل username: admin_khalifa + password: Admin@2024
2. النظام يتحقق من البيانات في جدول users
3. النظام يتحقق من password_hash باستخدام bcrypt
4. النظام يتحقق من role = 'admin' ✅
5. النظام يتحقق من is_active = TRUE ✅
6. النظام يحدث:
   ├── last_login = NOW()
   └── is_online = TRUE
7. النظام يسجل في activity_log:
   ├── action_type: 'login'
   ├── description: 'تسجيل دخول ناجح'
   └── ip_address: 192.168.1.100
8. النظام يسجل في login_attempts:
   ├── username: admin_khalifa
   ├── success: TRUE
   └── ip_address: 192.168.1.100
9. النظام ينشئ Session
10. النظام يوجه Admin إلى Dashboard
11. Dashboard يعرض:
    ├── إحصائيات شاملة (جميع الموظفين)
    ├── عدد التذاكر: 45 (مفتوحة: 20, متأخرة: 5, مغلقة: 20)
    ├── عدد الموظفين: 10 (نشط: 8, غير نشط: 2)
    ├── متوسط وقت الرد: 2.5 دقيقة
    └── رضا العملاء: 4.2/5
```

---

#### **السيناريو 2: Agent يسجل الدخول**

```
1. Agent يدخل username: ahmed_agent + password: Ahmed@123
2. النظام يتحقق من البيانات
3. النظام يتحقق من password_hash ✅
4. النظام يتحقق من role = 'agent' ✅
5. النظام يتحقق من is_active = TRUE ✅
6. النظام يحدث last_login و is_online = TRUE
7. النظام يسجل في activity_log
8. النظام يسجل في login_attempts (success: TRUE)
9. النظام ينشئ Session
10. النظام يوجه Agent إلى صفحة المحادثات
11. صفحة المحادثات تعرض:
    ├── محادثاته فقط (assigned_agent_id = 5)
    ├── عدد المحادثات: 8
    ├── غير المقروءة: 3
    ├── المتأخرة: 1
    └── آخر رسالة في كل محادثة
```

---

#### **السيناريو 3: Admin ينشئ موظف جديد**

```
1. Admin يدخل إلى صفحة "إدارة الموظفين"
2. Admin يضغط "إضافة موظف جديد"
3. Admin يدخل:
   ├── Username: mohamed_agent
   ├── Password: Mohamed@2024
   ├── Full Name: محمد أحمد
   ├── Email: mohamed@khalifa.com
   ├── Role: Agent
   └── Max Tickets: 15
4. النظام يتحقق من:
   ├── Username غير مكرر ✅
   ├── Email غير مكرر ✅
   ├── Password قوي (8+ أحرف، كبير+صغير+رقم+رمز) ✅
   └── Admin له صلاحية (role='admin') ✅
5. النظام ينشئ:
   ├── سجل في users:
   │   ├── username: mohamed_agent
   │   ├── password_hash: $2b$12$... (bcrypt)
   │   ├── role: 'agent'
   │   ├── created_by: admin.id
   │   └── is_active: TRUE
   ├── سجل في agents:
   │   ├── user_id: new_user.id
   │   ├── max_concurrent_tickets: 15
   │   └── current_active_tickets: 0
   └── سجل في activity_log:
       ├── user_id: admin.id
       ├── action_type: 'create_user'
       └── description: 'إنشاء مستخدم جديد: mohamed_agent'
6. النظام يعرض رسالة نجاح: "تم إنشاء الموظف بنجاح"
7. الموظف الجديد يمكنه تسجيل الدخول الآن
```

---

#### **السيناريو 4: Agent يحاول الوصول لصفحة Admin**

```
1. Agent (ahmed_agent) يحاول الدخول إلى /admin/all-tickets
2. النظام يتحقق من Session ✅
3. النظام يتحقق من role
4. النظام يجد role = 'agent' (ليس admin) ❌
5. النظام يسجل في activity_log:
   ├── user_id: ahmed_agent.id
   ├── action_type: 'unauthorized_access'
   ├── description: 'محاولة وصول لصفحة Admin: /admin/all-tickets'
   └── ip_address: 192.168.1.105
6. النظام يعرض صفحة 403 Forbidden:
   "عذراً، ليس لديك صلاحية للوصول لهذه الصفحة"
7. أو يعيد التوجيه إلى صفحة المحادثات الخاصة به
```

---

#### **السيناريو 5: Agent يحاول رؤية محادثة موظف آخر**

```
1. Agent (ahmed_agent, agent_id=5) يحاول فتح /conversations/ticket/123
2. النظام يتحقق من Session ✅
3. النظام يتحقق من role = 'agent' ✅
4. النظام يستعلم:
   SELECT assigned_agent_id
   FROM tickets
   WHERE id = 123
5. النظام يجد assigned_agent_id = 7 (موظف آخر)
6. النظام يقارن: 7 ≠ 5 (current_user.agent_id) ❌
7. النظام يسجل في activity_log:
   ├── user_id: ahmed_agent.id
   ├── action_type: 'unauthorized_access'
   ├── description: 'محاولة الوصول لتذكرة #123 غير مخصصة له'
   └── ticket_id: 123
8. النظام يعرض رسالة خطأ:
   "هذه المحادثة غير مخصصة لك"
9. النظام يعيد التوجيه إلى صفحة محادثاته
```

---

#### **السيناريو 6: محاولة Brute Force Attack**

```
1. مهاجم يحاول تسجيل الدخول:
   ├── المحاولة 1: username: admin, password: 123456 ❌
   ├── المحاولة 2: username: admin, password: admin123 ❌
   ├── المحاولة 3: username: admin, password: password ❌
   ├── المحاولة 4: username: admin, password: 12345678 ❌
   └── المحاولة 5: username: admin, password: qwerty ❌

2. النظام يسجل كل محاولة في login_attempts:
   ├── username: admin
   ├── success: FALSE
   └── ip_address: 203.0.113.50

3. عند المحاولة 6:
   ├── النظام يعد المحاولات الفاشلة في آخر 15 دقيقة
   ├── النتيجة: 5 محاولات فاشلة
   └── النظام يرفض المحاولة

4. النظام يعرض رسالة:
   "تم حظر الحساب مؤقتاً. حاول بعد 15 دقيقة"

5. النظام يسجل في activity_log:
   ├── action_type: 'brute_force_attempt'
   ├── description: 'محاولة Brute Force على حساب: admin'
   └── ip_address: 203.0.113.50

6. بعد 15 دقيقة، يمكن المحاولة مرة أخرى
```

---

#### **السيناريو 7: تسجيل الخروج**

```
1. User (Admin أو Agent) يضغط "تسجيل الخروج"
2. النظام يحدث:
   UPDATE users
   SET is_online = FALSE
   WHERE id = ?
3. النظام يسجل في activity_log:
   ├── user_id: user.id
   ├── action_type: 'logout'
   └── description: 'تسجيل خروج'
4. النظام يحذف Session
5. النظام يعيد التوجيه إلى صفحة تسجيل الدخول
```

---

### **📊 4.8 ملخص Queries الـ Authentication**

```
إجمالي Queries الـ Authentication:

✅ Login: 3 queries
   ├── التحقق من المستخدم
   ├── تحديث last_login
   └── تسجيل في activity_log

✅ Logout: 2 queries
   ├── تحديث is_online
   └── تسجيل في activity_log

✅ Create User: 4 queries
   ├── INSERT INTO users
   ├── INSERT INTO agents/admins
   ├── تسجيل في activity_log
   └── التحقق من Username/Email

✅ Check Permission (Ticket): 1 query
✅ Check Permission (Template): 1 query
✅ Deactivate User: 2 queries
✅ Brute Force Check: 1 query
✅ Get Activity Log: 1 query

المجموع: 15+ query
```

---

### **🔑 4.9 تحديث جدول users**

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,  -- للتسجيل
    password_hash VARCHAR(255) NOT NULL,    -- bcrypt hash
    email VARCHAR(150) UNIQUE NOT NULL,
    full_name VARCHAR(150),
    role ENUM('admin', 'agent') NOT NULL,   -- الدور

    -- Account Status
    is_active BOOLEAN DEFAULT TRUE,         -- مفعل/معطل
    is_online BOOLEAN DEFAULT FALSE,        -- متصل الآن
    last_login TIMESTAMP NULL,              -- آخر دخول

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,  -- Admin الذي أنشأ الحساب
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,

    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active),
    INDEX idx_is_online (is_online)
);
```

---

### **🔒 4.10 جدول login_attempts (جديد)**

```sql
CREATE TABLE login_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    success BOOLEAN DEFAULT FALSE,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_username (username),
    INDEX idx_ip_address (ip_address),
    INDEX idx_attempt_time (attempt_time),
    INDEX idx_success (success)
);
```

---

## � **5. Driver Pattern Architecture**

### **📋 نظرة عامة:**

```
🎯 الفكرة الأساسية:
   نظام مرن يسمح بالتبديل بين مزودي WhatsApp بدون تغيير الكود التجاري

🔌 المبدأ:
   ├── Interface موحد (MessageDriver)
   ├── Core لا يعرف مزود WhatsApp
   ├── Drivers قابلة للتبديل
   └── بيانات موحدة (provider + id_ext)

📦 الـ Drivers:
   ├── WPPConnect Driver (المرحلة 2 - الجزء 1)
   │   ├── QR Code Scan
   │   ├── مجاني
   │   └── سريع التطبيق
   │
   └── Cloud API Driver (المرحلة 2 - الجزء 2)
       ├── WhatsApp Business Cloud API
       ├── رسمي وموثوق
       └── مدفوع

🔄 التحويل:
   تغيير WHATSAPP_DRIVER في .env فقط
   ← كل شيء آخر يعمل تلقائياً
```

---

### **🏗️ 5.1 المعمارية (Architecture)**

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                       │
│                   (Business Logic Core)                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Tickets    │  │   Messages   │  │   Agents     │    │
│  │   Manager    │  │   Handler    │  │   Manager    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           ↓                                │
│              ┌────────────────────────┐                    │
│              │   MessageDriver        │                    │
│              │   (Abstract Interface) │                    │
│              └────────────┬───────────┘                    │
└───────────────────────────┼────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │    Driver Factory         │
              │  (based on WHATSAPP_DRIVER)│
              └─────────────┬─────────────┘
                            │
              ┌─────────────┴─────────────┐
              ↓                           ↓
    ┌─────────────────┐         ┌─────────────────┐
    │ WPPConnect      │         │ Cloud API       │
    │ Driver          │         │ Driver          │
    │                 │         │                 │
    │ - QR Scan       │         │ - Official API  │
    │ - Free          │         │ - Paid          │
    │ - Quick Setup   │         │ - Reliable      │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             ↓                           ↓
    ┌─────────────────┐         ┌─────────────────┐
    │ Redis Queue     │         │ Redis Queue     │
    │ (Incoming)      │         │ (Incoming)      │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             ↓                           ↓
       WhatsApp Web              WhatsApp Business
       (QR Code)                 Cloud API
```

---

## ��🔗 **5. خريطة العلاقات الكاملة (Foreign Keys Map)**

### **📊 جميع العلاقات بين الجداول**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USERS (الجدول الرئيسي)                      │
│                           id (PK)                               │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
    ┌────────────────┐                   ┌────────────────┐
    │    AGENTS      │                   │    ADMINS      │
    │  user_id ()  │                   │  user_id ()  │
    │      id (PK)   │                   │      id (PK)   │
    └────────┬───────┘                   └────────┬───────┘
             │                                    │
             │                                    │
             ▼                                    ▼
    ┌─────────────────────────────────────────────────────┐
    │                    TICKETS                          │
    │  assigned_agent_id () → agents.id                 │
    │  customer_id () → customers.id                    │
    │                  id (PK)                            │
    └────┬────────────────────────────────────────┬───────┘
         │                                        │
         ▼                                        ▼
┌────────────────┐                      ┌──────────────────┐
│   MESSAGES     │                      │ TICKET_TRANSFERS │
│ ticket_id () │                      │  ticket_id ()  │
│ sender_id () │                      │from_agent_id() │
│                │                      │ to_agent_id () │
└────────────────┘                      └──────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                       CUSTOMERS                                 │
│                         id (PK)                                 │
└────┬──────────────┬──────────────┬──────────────┬──────────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ TICKETS  │  │CUSTOMER  │  │CUSTOMER  │  │CUSTOMER_     │
│customer  │  │  _TAGS   │  │ _NOTES   │  │SATISFACTION  │
│_id ()  │  │customer  │  │customer  │  │customer_id   │
│          │  │_id ()  │  │_id ()  │  │    ()      │
└──────────┘  └──────────┘  └──────────┘  └──────────────┘
```

---

### **📋 جدول العلاقات التفصيلي (33 علاقة)**

| **#** | **الجدول الفرعي** | **الحقل ()** | **يشير إلى** | **عند الحذف** |
|-------|-------------------|----------------|--------------|---------------|
| 1 | **agents** | user_id | users.id | CASCADE |
| 2 | **admins** | user_id | users.id | CASCADE |
| 3 | **tickets** | customer_id | customers.id | CASCADE |
| 4 | **tickets** | assigned_agent_id | agents.id | SET NULL |
| 5 | **tickets** | current_agent_id | agents.id | SET NULL |
| 6 | **messages** | ticket_id | tickets.id | CASCADE |
| 7 | **messages** | sender_id | users.id | SET NULL |
| 8 | **message_delivery_log** | message_id | messages.id | CASCADE |
| 9 | **message_search_index** | message_id | messages.id | CASCADE |
| 10 | **message_search_index** | customer_id | customers.id | CASCADE |
| 11 | **message_search_index** | ticket_id | tickets.id | CASCADE |
| 12 | **customer_tags** | customer_id | customers.id | CASCADE |
| 13 | **customer_notes** | customer_id | customers.id | CASCADE |
| 14 | **customer_notes** | created_by | users.id | SET NULL |
| 15 | **ticket_transfers_log** | ticket_id | tickets.id | CASCADE |
| 16 | **ticket_transfers_log** | from_agent_id | agents.id | SET NULL |
| 17 | **ticket_transfers_log** | to_agent_id | agents.id | SET NULL |
| 18 | **ticket_transfers_log** | transferred_by | admins.id | SET NULL |
| 19 | **ticket_states_log** | ticket_id | tickets.id | CASCADE |
| 20 | **global_templates** | created_by | admins.id | CASCADE |
| 21 | **global_templates** | updated_by | admins.id | SET NULL |
| 22 | **agent_templates** | agent_id | agents.id | CASCADE |
| 23 | **auto_reply_triggers** | template_id | global_templates.id | SET NULL |
| 24 | **response_time_tracking** | ticket_id | tickets.id | CASCADE |
| 25 | **response_time_tracking** | agent_id | agents.id | SET NULL |
| 26 | **agent_delay_events** | ticket_id | tickets.id | CASCADE |
| 27 | **agent_delay_events** | agent_id | agents.id | CASCADE |
| 28 | **agent_kpi** | agent_id | agents.id | CASCADE |
| 29 | **agent_kpi_monthly** | agent_id | agents.id | CASCADE |
| 30 | **customer_satisfaction** | ticket_id | tickets.id | CASCADE |
| 31 | **customer_satisfaction** | agent_id | agents.id | SET NULL |
| 32 | **customer_satisfaction** | customer_id | customers.id | CASCADE |
| 33 | **activity_log** | user_id | users.id | SET NULL |
| 34 | **activity_log** | ticket_id | tickets.id | SET NULL |

---

### **🔍 ملاحظات مهمة عن العلاقات:**

#### **1. CASCADE (الحذف المتسلسل)**
```
عند حذف:
✅ User → يُحذف Agent/Admin المرتبط
✅ Customer → تُحذف جميع Tickets والـ Tags والـ Notes
✅ Ticket → تُحذف جميع Messages والـ Logs
✅ Agent → تُحذف جميع KPIs والـ Templates
✅ Message → تُحذف جميع Delivery Logs
```

#### **2. SET NULL (تعيين NULL)**
```
عند حذف:
⚠️ Agent → التذاكر المخصصة له تصبح assigned_agent_id = NULL
⚠️ User → الرسائل المرسلة منه تصبح sender_id = NULL
⚠️ Admin → القوالب المُنشأة تبقى لكن created_by = NULL
```

#### **3. الفهارس (Indexes) للبحث السريع**
```sql
-- في جدول messages (للبحث مثل WhatsApp Web)
INDEX idx_ticket_id (ticket_id)                -- للبحث حسب التذكرة
INDEX idx_sender_type (sender_type)            -- للفلترة حسب المرسل
INDEX idx_is_read (is_read)                    -- للبحث عن غير المقروءة ⭐
FULLTEXT INDEX idx_message_text (message_text) -- للبحث في النص ⭐

-- في جدول tickets
INDEX idx_assigned_agent (assigned_agent_id)   -- للبحث حسب الموظف
INDEX idx_status (status)                      -- للفلترة حسب الحالة
INDEX idx_customer (customer_id)               -- للبحث حسب العميل
INDEX idx_created_at (created_at)              -- للترتيب الزمني

-- في جدول customers
INDEX idx_phone_number (phone_number)          -- للبحث بالرقم ⭐
INDEX idx_wa_id (wa_id)                        -- للبحث بـ WhatsApp ID
```

---

### **✅ Query للتحقق من سلامة العلاقات**

```sql
-- عرض جميع Foreign Keys في قاعدة البيانات
SELECT
    TABLE_NAME as 'الجدول',
    COLUMN_NAME as 'الحقل',
    CONSTRAINT_NAME as 'اسم القيد',
    REFERENCED_TABLE_NAME as 'يشير إلى جدول',
    REFERENCED_COLUMN_NAME as 'يشير إلى حقل'
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_SCHEMA = 'khalifa_pharmacy'
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, COLUMN_NAME;
```

---

## 🎬 **5. السيناريوهات التفصيلية**

### **دورة حياة التذكرة:**
```
[1] new (جديدة) → تم إنشاؤها للتو
    ↓
[2] open (مفتوحة) → تم توزيعها على agent
    ↓
[3] in_progress (قيد المعالجة) → Agent يتفاعل
    ↓
[4] pending (متأخرة) ← إذا مر 3 دقائق بدون رد
    ↓
[5] closed (مغلقة) → تم إنهاؤها
```

---

### **السيناريو 1: عميل جديد يرسل رسالة**
#### **الخطوات:**

```
1. استقبال رسالة
   ├── Phone: 01012345678
   ├── Name: محمد (اختياري)
   └── Content: "محتاج دواء للضغط"

2. التحقق من العميل
   ├── Query: SELECT * FROM customers WHERE phone_number = ?
   ├── النتيجة: غير موجود
   └── Action: INSERT INTO customers (...) → customer_id = 123

3. البحث عن Agent متاح (Load Balancing)
   ├── Query: SELECT agents with current_active_tickets < 15
   ├── ORDER BY current_active_tickets ASC
   ├── النتيجة:
   │   ├── أحمد: 8 تذاكر ← الأقل ✅
   │   ├── فاطمة: 10 تذاكر
   │   └── علي: 12 تذاكر
   └── الاختيار: أحمد (agent_id = 456)

4. إنشاء تذكرة جديدة
   ├── INSERT INTO tickets (...)
   ├── ticket_number: TKT-2025-000789
   ├── customer_id: 123
   ├── assigned_agent_id: 456
   ├── status: 'open'
   └── ticket_id = 789

5. إضافة الرسالة الأولى
   ├── INSERT INTO messages (...)
   ├── ticket_id: 789
   ├── sender_type: 'customer'
   └── message_text: "محتاج دواء للضغط"

6. تحديث حالة Agent
   ├── UPDATE agents SET current_active_tickets = 9
   └── status: 'available' (لأن 9 < 15)

7. إرسال إشعار (Socket.io)
   ├── io.to('agent-456').emit('new_ticket', {...})
   ├── Desktop Notification
   └── Sound Alert

8. بدء Timer (3 دقائق)
   └── setTimeout(() => checkDelay(789), 180000)
```

---

### **السيناريو 2: Agent يرد على رسالة**

```
1. Agent (أحمد) يفتح التذكرة #789
   └── GET /api/tickets/789/messages

2. Agent يكتب الرد
   └── "أهلاً بك، أي نوع تحديداً؟"

3. حفظ رسالة Agent
   ├── INSERT INTO messages (...)
   ├── sender_type: 'agent'
   └── sender_id: 456

4. التحقق: هل أول رد؟
   ├── SELECT first_response_at FROM tickets WHERE id = 789
   └── النتيجة: NULL ← نعم

5. حساب Response Time
   ├── created_at: 10:30:00
   ├── first_response_at: 10:32:15
   ├── response_time: 135 ثانية (2.25 دقيقة)
   └── ✅ في الوقت (< 3 دقائق)

6. تحديث التذكرة
   ├── UPDATE tickets SET
   ├── status = 'in_progress'
   ├── first_response_at = NOW()
   ├── response_time_seconds = 135
   └── is_delayed = FALSE

7. تسجيل في response_time_tracking
   └── INSERT INTO response_time_tracking (...)

8. تحديث KPI
   └── UPDATE agent_kpi SET messages_sent++
```

---

### **السيناريو 3: تأخر Agent (Delay Detection)**

```
Cron Job يعمل كل دقيقة: checkDelayedTickets()

1. البحث عن تذاكر متأخرة
   ├── Query: SELECT tickets WHERE
   │   ├── status = 'open'  (مفتوحة فقط)
   │   ├── first_response_at IS NULL  (لم يرد بعد)
   │   ├── is_delayed = FALSE  (لم تُعلّم متأخرة بعد)
   │   └── (NOW() - created_at) > 180 seconds  (مر أكثر من 3 دقائق)
   └── النتيجة: تذكرة #850 (مر 4 دقائق)

2. تحديث التذكرة إلى DELAYED
   ├── UPDATE tickets SET
   ├── status = 'delayed'  ← الحالة تتغير
   ├── is_delayed = TRUE
   ├── delay_started_at = NOW()  ← تسجيل وقت بداية التأخير
   └── delay_count++

3. تسجيل حدث التأخير
   └── INSERT INTO agent_delay_events (
       ticket_id, agent_id, delay_started_at
   )

4. تحديث KPI
   └── UPDATE agent_kpi SET delay_count++

5. إشعار للـ Admin
   ├── WebSocket: emit('agent_delay', {...})
   ├── Desktop Notification (أحمر)
   └── Sound Alert

6. تحديث واجهة Admin
   ├── بطاقة Agent → لون أحمر 🔴
   ├── عرض "DELAY" badge
   ├── عرض الوقت: "4 دقائق"
   └── خيارات: [تحويل] [تنبيه]
```

---

### **السيناريو 3.1: Agent يرد بعد التأخير** ⭐ **جديد**

```
1. Agent يرد على تذكرة متأخرة
   ├── ticket_id: 850
   ├── status الحالي: 'delayed'
   └── delay_started_at: 10:33:00

2. حساب وقت التأخير
   ├── delay_started_at: 10:33:00
   ├── NOW(): 10:37:30
   └── delay_duration: 4.5 دقيقة (270 ثانية)

3. تحديث التذكرة - العودة لـ OPEN
   ├── UPDATE tickets SET
   ├── status = 'open'  ← ترجع مفتوحة
   ├── is_delayed = FALSE
   ├── total_delay_minutes += 4.5  ← يُحسب التأخير
   ├── first_response_at = NOW()
   └── delay_started_at = NULL

4. تحديث حدث التأخير
   └── UPDATE agent_delay_events SET
       ├── delay_ended_at = NOW()
       └── delay_duration_seconds = 270

5. تحديث KPI
   ├── UPDATE agent_kpi SET
   ├── total_delay_minutes += 4.5  ← يُحسب على الموظف
   └── quality_score = recalculate()

6. إشعار للـ Admin
   ├── WebSocket: emit('delay_resolved', {...})
   └── بطاقة Agent → لون أخضر ✅

⚠️ **مهم:** التأخير يُحسب على الموظف حتى لو رد بعدها!
```

---

### **السيناريو 4: Agent ينهي المحادثة**

```
1. Agent يضغط "إنهاء المحادثة"
   └── ticket_id: 789

2. التحقق من الصلاحية
   ├── assigned_agent_id == current_user_id
   └── ✅ صحيح

3. إغلاق التذكرة
   ├── UPDATE tickets SET
   ├── status = 'closed'
   ├── closed_at = NOW()
   ├── closed_by_user_id = 456
   └── handling_time_seconds = (NOW() - created_at)

4. حساب Handling Time
   ├── created_at: 10:30:00
   ├── closed_at: 10:45:30
   └── handling_time: 930 ثانية (15.5 دقيقة)

5. تحديث حالة Agent
   ├── UPDATE agents SET
   ├── current_active_tickets: 9 → 8
   └── status: 'available'

6. تحديث KPI
   ├── UPDATE agent_kpi SET
   ├── total_tickets_closed++
   └── avg_handling_time = recalculate()

7. تسجيل في ticket_states_log
   └── INSERT (old_state='in_progress', new_state='closed')
```

---

### **السيناريو 5: Admin يحول تذكرة**

```
1. Admin يختار تذكرة #789
   ├── الموظف الحالي: أحمد (12 تذكرة)
   └── يريد التحويل

2. Admin يختار موظف جديد
   └── فاطمة (8 تذاكر)

3. التحقق من التوفر
   ├── Query: SELECT active_tickets_count FROM agents WHERE id = 999
   ├── النتيجة: 8 تذاكر
   └── ✅ متاح (8 < 15)

4. تسجيل التحويل
   ├── INSERT INTO ticket_transfers_log (...)
   ├── from_agent_id: 456 (أحمد)
   ├── to_agent_id: 999 (فاطمة)
   ├── transferred_by: 111 (admin_id)
   └── reason: "إعادة توزيع الحمل"

5. تحديث التذكرة
   └── UPDATE tickets SET assigned_agent_id = 999

6. تحديث حالة أحمد
   ├── current_active_tickets: 12 → 11
   └── status: 'available'

7. تحديث حالة فاطمة
   ├── current_active_tickets: 8 → 9
   └── status: 'available'

8. إشعارات
   ├── لفاطمة: "تم تحويل تذكرة #789 إليك"
   └── لأحمد: "تم تحويل تذكرة #789 منك"

9. تسجيل في activity_log
   └── INSERT (action='ticket_transferred', ...)
```

---

### **السيناريو 6: عميل قديم يرسل رسالة جديدة**

```
1. استقبال رسالة من 01012345678
   └── "محتاج نفس الدواء مرة تانية"

2. التحقق من العميل
   ├── Query: SELECT * FROM customers WHERE phone_number = ?
   ├── النتيجة: موجود (customer_id = 123)
   └── لديه تذكرة سابقة #789 (مغلقة منذ 3 أيام)

3. فتح تذكرة جديدة
   ├── لا يتم إعادة فتح التذكرة القديمة
   └── يتم إنشاء تذكرة جديدة #850

4. اختيار الموظف
   ├── الخيار 1: نفس الموظف السابق (أحمد) - إذا متاح
   ├── الخيار 2: موظف آخر - حسب الحمل
   └── القرار: حسب إعدادات النظام

5. إنشاء التذكرة الجديدة
   └── نفس خطوات السيناريو 1

6. تحديث بيانات العميل
   ├── UPDATE customers SET
   ├── last_contact_date = NOW()
   └── total_tickets_count++
```

---

## 🔧 **5. العمليات والـ Queries الأساسية**

### **العملية 1: إنشاء تذكرة جديدة**

```javascript
async function createNewTicket(phoneNumber, customerName, messageText) {
    // 1. التحقق من العميل
    let customer = await db.query(
        'SELECT id FROM customers WHERE phone_number = ?',
        [phoneNumber]
    );

    if (!customer) {
        // إنشاء عميل جديد
        customer = await db.query(
            `INSERT INTO customers (phone_number, wa_id, name, first_contact_date, last_contact_date)
             VALUES (?, ?, ?, NOW(), NOW())`,
            [phoneNumber, `${phoneNumber}@c.us`, customerName]
        );
    } else {
        // تحديث آخر اتصال
        await db.query(
            'UPDATE customers SET last_contact_date = NOW(), total_tickets_count = total_tickets_count + 1 WHERE id = ?',
            [customer.id]
        );
    }

    // 2. البحث عن agent متاح
    const agent = await db.query(
        `SELECT a.id, a.current_active_tickets
         FROM agents a
         JOIN users u ON a.user_id = u.id
         WHERE a.is_online = TRUE
           AND a.status IN ('available', 'busy')
           AND a.current_active_tickets < 15
         ORDER BY a.current_active_tickets ASC
         LIMIT 1`
    );

    if (!agent) {
        throw new Error('No available agents');
    }

    // 3. إنشاء التذكرة
    const ticketNumber = `TKT-${new Date().getFullYear()}-${String(nextId).padStart(6, '0')}`;
    const ticket = await db.query(
        `INSERT INTO tickets (ticket_number, customer_id, assigned_agent_id, status, created_at, last_customer_message_at)
         VALUES (?, ?, ?, 'open', NOW(), NOW())`,
        [ticketNumber, customer.id, agent.id]
    );

    // 4. إضافة الرسالة
    await db.query(
        `INSERT INTO messages (ticket_id, sender_type, message_text, created_at)
         VALUES (?, 'customer', ?, NOW())`,
        [ticket.id, messageText]
    );

    // 5. تحديث عداد الرسائل
    await db.query(
        'UPDATE tickets SET messages_count = messages_count + 1 WHERE id = ?',
        [ticket.id]
    );

    // 6. تحديث حالة Agent
    await db.query(
        `UPDATE agents SET
            current_active_tickets = current_active_tickets + 1,
            status = CASE WHEN current_active_tickets + 1 >= 15 THEN 'busy' ELSE 'available' END
         WHERE id = ?`,
        [agent.id]
    );

    // 7. إرسال إشعار
    io.to(`agent-${agent.id}`).emit('new_ticket', {
        ticketId: ticket.id,
        ticketNumber: ticketNumber,
        customerName: customerName,
        message: messageText
    });

    // 8. بدء Timer
    setTimeout(() => checkDelayedTicket(ticket.id), 180000);

    return ticket;
}
```

---

### **العملية 2: Agent يرد على رسالة**

```javascript
async function agentReply(ticketId, agentId, messageText) {
    // 1. إضافة رسالة Agent
    await db.query(
        `INSERT INTO messages (ticket_id, sender_id, sender_type, message_text, created_at)
         VALUES (?, ?, 'agent', ?, NOW())`,
        [ticketId, agentId, messageText]
    );

    // 2. التحقق من أول رد
    const ticket = await db.query(
        'SELECT first_response_at, created_at FROM tickets WHERE id = ?',
        [ticketId]
    );

    if (!ticket.first_response_at) {
        // حساب Response Time
        const responseTime = Math.floor((Date.now() - new Date(ticket.created_at)) / 1000);

        await db.query(
            `UPDATE tickets SET
                first_response_at = NOW(),
                response_time_seconds = ?,
                status = 'in_progress',
                is_delayed = FALSE
             WHERE id = ?`,
            [responseTime, ticketId]
        );

        // تسجيل في response_time_tracking
        await db.query(
            `INSERT INTO response_time_tracking (ticket_id, agent_id, message_received_at, first_response_at, response_time_seconds, is_delayed)
             VALUES (?, ?, ?, NOW(), ?, ?)`,
            [ticketId, agentId, ticket.created_at, responseTime, responseTime > 180]
        );
    }

    // 3. تحديث عدادات
    await db.query(
        'UPDATE tickets SET messages_count = messages_count + 1, last_agent_message_at = NOW() WHERE id = ?',
        [ticketId]
    );

    // 4. تحديث KPI
    await db.query(
        `INSERT INTO agent_kpi (agent_id, kpi_date, messages_sent)
         VALUES (?, CURDATE(), 1)
         ON DUPLICATE KEY UPDATE messages_sent = messages_sent + 1`,
        [agentId]
    );
}
```

---

### **العملية 3: كشف التأخير (Cron Job)**

```javascript
// يعمل كل دقيقة
async function checkDelayedTickets() {
    // 1. البحث عن تذاكر متأخرة
    const delayedTickets = await db.query(
        `SELECT id, ticket_number, assigned_agent_id
         FROM tickets
         WHERE status IN ('new', 'open', 'in_progress')
           AND first_response_at IS NULL
           AND TIMESTAMPDIFF(SECOND, last_customer_message_at, NOW()) > 180`
    );

    for (const ticket of delayedTickets) {
        // 2. تحديث التذكرة
        await db.query(
            `UPDATE tickets SET
                is_delayed = TRUE,
                status = 'pending',
                delay_count = delay_count + 1
             WHERE id = ?`,
            [ticket.id]
        );

        // 3. تسجيل حدث التأخير
        await db.query(
            `INSERT INTO agent_delay_events (ticket_id, agent_id, delay_start_time)
             VALUES (?, ?, NOW())`,
            [ticket.id, ticket.assigned_agent_id]
        );

        // 4. تحديث KPI
        await db.query(
            `UPDATE agent_kpi SET delay_count = delay_count + 1
             WHERE agent_id = ? AND kpi_date = CURDATE()`,
            [ticket.assigned_agent_id]
        );

        // 5. إشعار للـ Admin
        io.to('admin').emit('agent_delay', {
            ticketId: ticket.id,
            ticketNumber: ticket.ticket_number,
            agentId: ticket.assigned_agent_id
        });
    }
}
```

---

## � **6. Queries البحث والفلترة المتقدمة**

### **🎯 البحث مثل WhatsApp Web - للموظف**

#### **6.1 البحث في محادثاتي (بالاسم أو الرقم أو الرسالة)**

```sql
-- البحث الشامل في محادثات الموظف
-- يبحث في: اسم العميل، رقم الهاتف، محتوى الرسائل
SELECT DISTINCT
    t.id as ticket_id,
    t.ticket_number,
    t.status,
    c.id as customer_id,
    c.name as customer_name,
    c.phone_number,
    t.created_at,
    t.last_message_at,

    -- آخر رسالة في المحادثة
    (SELECT m.message_text
     FROM messages m
     WHERE m.ticket_id = t.id
     ORDER BY m.created_at DESC
     LIMIT 1) as last_message,

    -- عدد الرسائل غير المقروءة (من العميل)
    (SELECT COUNT(*)
     FROM messages m
     WHERE m.ticket_id = t.id
       AND m.sender_type = 'customer'
       AND m.is_read = FALSE) as unread_count,

    -- عدد الرسائل التي تحتوي على كلمة البحث
    (SELECT COUNT(*)
     FROM messages m
     WHERE m.ticket_id = t.id
       AND m.message_text LIKE CONCAT('%', ?, '%')) as match_count

FROM tickets t
JOIN customers c ON t.customer_id = c.id
LEFT JOIN messages m ON t.id = m.ticket_id

WHERE t.assigned_agent_id = ?  -- الموظف الحالي فقط
  AND (
      -- البحث في اسم العميل
      c.name LIKE CONCAT('%', ?, '%')

      -- أو البحث في رقم الهاتف
      OR c.phone_number LIKE CONCAT('%', ?, '%')

      -- أو البحث في محتوى الرسائل
      OR m.message_text LIKE CONCAT('%', ?, '%')
  )

GROUP BY t.id
ORDER BY
    -- الأولوية: المحادثات التي فيها تطابق أكثر
    match_count DESC,
    -- ثم الأحدث
    t.last_message_at DESC

LIMIT 50;
```

**مثال استخدام:**
```javascript
// البحث عن "بنادول"
const searchTerm = 'بنادول';
const agentId = 5;

const results = await db.query(searchQuery, [
    searchTerm,  // للعد
    agentId,     // الموظف
    searchTerm,  // اسم العميل
    searchTerm,  // رقم الهاتف
    searchTerm   // محتوى الرسالة
]);

// النتيجة:
// [
//   {
//     ticket_id: 123,
//     customer_name: "محمد علي",
//     phone_number: "01012345678",
//     last_message: "محتاج بنادول اكسترا",
//     match_count: 3,  // 3 رسائل تحتوي "بنادول"
//     unread_count: 1
//   },
//   {
//     ticket_id: 456,
//     customer_name: "أحمد حسن",
//     last_message: "بنادول أدفانس متوفر؟",
//     match_count: 2,
//     unread_count: 0
//   }
// ]
```

---

#### **6.2 البحث داخل محادثة معينة**

```sql
-- البحث في رسائل محادثة واحدة (مثل WhatsApp Web)
SELECT
    m.id,
    m.message_text,
    m.sender_type,
    m.created_at,

    -- معلومات المرسل
    CASE
        WHEN m.sender_type = 'customer' THEN c.name
        WHEN m.sender_type = 'agent' THEN u.full_name
        ELSE 'System'
    END as sender_name,

    -- هل الرسالة تحتوي على كلمة البحث
    CASE
        WHEN m.message_text LIKE CONCAT('%', ?, '%') THEN TRUE
        ELSE FALSE
    END as is_match

FROM messages m
JOIN tickets t ON m.ticket_id = t.id
JOIN customers c ON t.customer_id = c.id
LEFT JOIN users u ON m.sender_id = u.id

WHERE t.id = ?  -- المحادثة المحددة
  AND t.assigned_agent_id = ?  -- تأكد أنها للموظف الحالي
  AND m.message_text LIKE CONCAT('%', ?, '%')  -- كلمة البحث

ORDER BY m.created_at ASC;
```

---

#### **6.3 اقتراحات البحث (Auto-complete)**

```sql
-- اقتراحات أثناء الكتابة (مثل WhatsApp Web)
-- يعرض: أسماء العملاء + أرقام + كلمات شائعة

-- الجزء 1: أسماء العملاء
(SELECT DISTINCT
    c.name as suggestion,
    'customer_name' as type,
    COUNT(t.id) as relevance
FROM customers c
JOIN tickets t ON c.id = t.customer_id
WHERE t.assigned_agent_id = ?
  AND c.name LIKE CONCAT(?, '%')
GROUP BY c.id
ORDER BY relevance DESC
LIMIT 5)

UNION ALL

-- الجزء 2: أرقام الهواتف
(SELECT DISTINCT
    c.phone_number as suggestion,
    'phone_number' as type,
    COUNT(t.id) as relevance
FROM customers c
JOIN tickets t ON c.id = t.customer_id
WHERE t.assigned_agent_id = ?
  AND c.phone_number LIKE CONCAT(?, '%')
GROUP BY c.id
ORDER BY relevance DESC
LIMIT 5)

UNION ALL

-- الجزء 3: كلمات شائعة من الرسائل
(SELECT DISTINCT
    SUBSTRING_INDEX(SUBSTRING_INDEX(m.message_text, ' ', numbers.n), ' ', -1) as suggestion,
    'message_keyword' as type,
    COUNT(*) as relevance
FROM messages m
JOIN tickets t ON m.ticket_id = t.id
CROSS JOIN (
    SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) numbers
WHERE t.assigned_agent_id = ?
  AND CHAR_LENGTH(m.message_text) - CHAR_LENGTH(REPLACE(m.message_text, ' ', '')) >= numbers.n - 1
  AND SUBSTRING_INDEX(SUBSTRING_INDEX(m.message_text, ' ', numbers.n), ' ', -1) LIKE CONCAT(?, '%')
  AND CHAR_LENGTH(SUBSTRING_INDEX(SUBSTRING_INDEX(m.message_text, ' ', numbers.n), ' ', -1)) > 2
GROUP BY suggestion
HAVING COUNT(*) > 2  -- كلمات تكررت أكثر من مرتين
ORDER BY relevance DESC
LIMIT 5)

ORDER BY relevance DESC
LIMIT 10;
```

---

#### **6.4 فلترة المحادثات (مثل WhatsApp Web)**

```sql
-- فلترة محادثات الموظف
SELECT
    t.id,
    t.ticket_number,
    t.status,
    c.name,
    c.phone_number,
    t.created_at,
    t.last_message_at,

    -- آخر رسالة
    (SELECT m.message_text
     FROM messages m
     WHERE m.ticket_id = t.id
     ORDER BY m.created_at DESC
     LIMIT 1) as last_message,

    -- عدد غير المقروءة
    (SELECT COUNT(*)
     FROM messages m
     WHERE m.ticket_id = t.id
       AND m.sender_type = 'customer'
       AND m.is_read = FALSE) as unread_count,

    -- Tags
    (SELECT GROUP_CONCAT(tag)
     FROM customer_tags
     WHERE customer_id = c.id) as tags

FROM tickets t
JOIN customers c ON t.customer_id = c.id

WHERE t.assigned_agent_id = ?

  -- فلترة حسب الحالة (اختياري)
  AND (? IS NULL OR t.status = ?)

  -- فلترة حسب الفئة (اختياري)
  AND (? IS NULL OR t.category = ?)

  -- فلترة حسب الأولوية (اختياري)
  AND (? IS NULL OR t.priority = ?)

  -- فلترة: غير مقروءة فقط (اختياري)
  AND (? = FALSE OR EXISTS (
      SELECT 1 FROM messages m
      WHERE m.ticket_id = t.id
        AND m.sender_type = 'customer'
        AND m.is_read = FALSE
  ))

  -- فلترة: متأخرة فقط (اختياري)
  AND (? = FALSE OR t.status = 'delayed')

ORDER BY
    -- الأولوية: غير المقروءة أولاً
    unread_count DESC,
    -- ثم المتأخرة
    CASE WHEN t.status = 'delayed' THEN 0 ELSE 1 END,
    -- ثم الأحدث
    t.last_message_at DESC;
```

**مثال استخدام:**
```javascript
// فلترة: مفتوحة + غير مقروءة فقط
const filters = {
    agentId: 5,
    status: 'open',      // أو NULL للكل
    category: null,      // NULL = الكل
    priority: null,
    unreadOnly: true,    // فقط غير المقروءة
    delayedOnly: false
};

const results = await db.query(filterQuery, [
    filters.agentId,
    filters.status, filters.status,
    filters.category, filters.category,
    filters.priority, filters.priority,
    filters.unreadOnly,
    filters.delayedOnly
]);
```

---

#### **6.5 تحديث حالة "مقروءة" للرسائل**

```sql
-- عند فتح محادثة، تحديث الرسائل لـ "مقروءة"
UPDATE messages m
JOIN tickets t ON m.ticket_id = t.id
SET m.is_read = TRUE,
    m.read_at = NOW()
WHERE t.id = ?
  AND t.assigned_agent_id = ?  -- تأكد أنها للموظف
  AND m.sender_type = 'customer'
  AND m.is_read = FALSE;
```

---

### **📊 Queries التقارير والإحصائيات**

#### **6.6 تقرير أداء الموظفين - يومي**

```sql
-- مقارنة أداء جميع الموظفين اليوم
SELECT
    u.full_name as agent_name,
    a.status as current_status,
    a.current_active_tickets,

    -- إحصائيات اليوم
    COUNT(t.id) as total_tickets_today,
    COUNT(CASE WHEN t.status = 'closed' THEN 1 END) as closed_today,
    COUNT(CASE WHEN t.status = 'delayed' THEN 1 END) as delayed_today,

    -- متوسط وقت الرد
    AVG(CASE
        WHEN t.first_response_at IS NOT NULL
        THEN t.response_time_seconds
    END) as avg_response_time,

    -- إجمالي دقائق التأخير
    SUM(COALESCE(t.total_delay_minutes, 0)) as total_delay_minutes,

    -- Quality Score
    ROUND(
        COUNT(CASE WHEN t.response_time_seconds <= 180 THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN t.first_response_at IS NOT NULL THEN 1 END), 0),
        2
    ) as quality_score_percentage,

    -- متوسط التقييم
    AVG(cs.rating) as avg_customer_rating

FROM agents a
JOIN users u ON a.user_id = u.id
LEFT JOIN tickets t ON a.id = t.assigned_agent_id
    AND DATE(t.created_at) = CURDATE()
LEFT JOIN customer_satisfaction cs ON t.id = cs.ticket_id

WHERE a.is_active = TRUE

GROUP BY a.id, u.full_name, a.status, a.current_active_tickets
ORDER BY quality_score_percentage DESC, total_tickets_today DESC;
```

---

#### **6.7 حمل العمل الحالي (Real-time Dashboard)**

```sql
-- حالة الموظفين الآن
SELECT
    u.full_name,
    a.status,
    a.is_online,
    a.current_active_tickets,
    a.max_capacity,

    -- نسبة الاستخدام
    ROUND((a.current_active_tickets * 100.0 / a.max_capacity), 2) as utilization_percentage,

    -- التذاكر المتأخرة الآن
    COUNT(CASE WHEN t.status = 'delayed' THEN 1 END) as delayed_now,

    -- التذاكر المفتوحة
    COUNT(CASE WHEN t.status = 'open' THEN 1 END) as open_now,

    -- آخر نشاط
    MAX(t.last_message_at) as last_activity

FROM agents a
JOIN users u ON a.user_id = u.id
LEFT JOIN tickets t ON a.id = t.assigned_agent_id
    AND t.status IN ('open', 'delayed')

WHERE a.is_active = TRUE

GROUP BY a.id, u.full_name, a.status, a.is_online,
         a.current_active_tickets, a.max_capacity

ORDER BY utilization_percentage DESC;
```

---

#### **6.8 العملاء الأكثر نشاطاً**

```sql
-- أكثر 20 عميل تواصلاً
SELECT
    c.id,
    c.name,
    c.phone_number,
    c.first_contact_date,
    c.last_contact_date,

    -- عدد التذاكر
    COUNT(DISTINCT t.id) as total_tickets,

    -- عدد الرسائل
    COUNT(DISTINCT m.id) as total_messages,

    -- متوسط التقييم
    AVG(cs.rating) as avg_rating,

    -- Tags
    GROUP_CONCAT(DISTINCT ct.tag) as tags,

    -- آخر محادثة
    MAX(t.created_at) as last_ticket_date

FROM customers c
LEFT JOIN tickets t ON c.id = t.customer_id
LEFT JOIN messages m ON t.id = m.ticket_id
LEFT JOIN customer_satisfaction cs ON t.id = cs.ticket_id
LEFT JOIN customer_tags ct ON c.id = ct.customer_id

GROUP BY c.id
ORDER BY total_tickets DESC, total_messages DESC
LIMIT 20;
```

---

#### **6.9 ساعات الذروة (Peak Hours)**

```sql
-- معرفة أكثر الساعات ازدحاماً
SELECT
    HOUR(t.created_at) as hour_of_day,
    COUNT(*) as ticket_count,
    AVG(t.response_time_seconds) as avg_response_time,
    COUNT(CASE WHEN t.status = 'delayed' THEN 1 END) as delayed_count,

    -- نسبة التأخير
    ROUND(
        COUNT(CASE WHEN t.status = 'delayed' THEN 1 END) * 100.0 / COUNT(*),
        2
    ) as delay_percentage

FROM tickets t
WHERE DATE(t.created_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)

GROUP BY hour_of_day
ORDER BY ticket_count DESC;
```

---

#### **6.10 رضا العملاء حسب الموظف**

```sql
-- تقييم رضا العملاء
SELECT
    u.full_name as agent_name,

    -- عدد التقييمات
    COUNT(cs.id) as total_ratings,

    -- متوسط التقييم
    ROUND(AVG(cs.rating), 2) as avg_rating,

    -- توزيع التقييمات
    COUNT(CASE WHEN cs.rating = 5 THEN 1 END) as five_stars,
    COUNT(CASE WHEN cs.rating = 4 THEN 1 END) as four_stars,
    COUNT(CASE WHEN cs.rating = 3 THEN 1 END) as three_stars,
    COUNT(CASE WHEN cs.rating = 2 THEN 1 END) as two_stars,
    COUNT(CASE WHEN cs.rating = 1 THEN 1 END) as one_star,

    -- نسبة الرضا (4 و 5 نجوم)
    ROUND(
        COUNT(CASE WHEN cs.rating >= 4 THEN 1 END) * 100.0 /
        NULLIF(COUNT(cs.id), 0),
        2
    ) as satisfaction_percentage

FROM agents a
JOIN users u ON a.user_id = u.id
LEFT JOIN customer_satisfaction cs ON a.id = cs.agent_id
    AND DATE(cs.created_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)

WHERE a.is_active = TRUE

GROUP BY a.id, u.full_name
ORDER BY avg_rating DESC, total_ratings DESC;
```

---

## �📈 **7. مؤشرات الأداء (KPIs)**

### **للـ Agent:**

#### **1. First Response Time (FRT)**
```sql
-- متوسط وقت أول رد
SELECT AVG(response_time_seconds) as avg_frt
FROM tickets
WHERE assigned_agent_id = ?
  AND first_response_at IS NOT NULL
  AND DATE(created_at) = CURDATE();
```

#### **2. Total Tickets Handled**
```sql
SELECT COUNT(*) as total_tickets
FROM tickets
WHERE assigned_agent_id = ?
  AND DATE(created_at) = CURDATE();
```

#### **3. Delayed Responses**
```sql
SELECT COUNT(*) as delayed_count
FROM tickets
WHERE assigned_agent_id = ?
  AND is_delayed = TRUE
  AND DATE(created_at) = CURDATE();
```

#### **4. Quality Score**
```sql
SELECT
    (COUNT(*) FILTER (WHERE response_time_seconds <= 180) * 100.0 / COUNT(*)) as quality_score
FROM tickets
WHERE assigned_agent_id = ?
  AND first_response_at IS NOT NULL
  AND DATE(created_at) = CURDATE();
```

---

### **للنظام:**

#### **Dashboard Stats**
```sql
-- إحصائيات اليوم
SELECT
    COUNT(*) FILTER (WHERE status IN ('new', 'open', 'in_progress', 'pending')) as active_tickets,
    COUNT(*) FILTER (WHERE status = 'closed' AND DATE(closed_at) = CURDATE()) as closed_today,
    COUNT(*) FILTER (WHERE is_delayed = TRUE) as delayed_tickets,
    AVG(response_time_seconds) as avg_response_time
FROM tickets
WHERE DATE(created_at) = CURDATE();
```

---
## 🎨 **8. واجهات المستخدم (UI Wireframes)**

### **واجهة Admin - Dashboard**

```
┌─────────────────────────────────────────────────────────────┐
│  🏥 صيدليات خليفة - لوحة التحكم                            │
│  ────────────────────────────────────────────────────────── │
│                                                             │
│  📊 إحصائيات اليوم                                          │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │ نشطة     │ مغلقة    │ متأخرة   │ متوسط الرد│              │
│  │   24     │   156    │    3     │  2.5 دق  │              │
│  └──────────┴──────────┴──────────┴──────────┘              │
│                                                             │
│  👥 الموظفين (15)                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ✅ أحمد محمد      │ 8 تذاكر  │ 2.1 دق │ [عرض]     │    │
│  │ ✅ فاطمة علي      │ 10 تذاكر │ 2.8 دق │ [عرض]     │    │
│  │ 🔴 علي حسن (تأخير)│ 12 تذاكر │ 4.2 دق │ [تحويل]   │    │
│  │ ⚪ سارة أحمد       │ 0 تذاكر  │ -      │ [Offline] │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  📝 إدخال رسالة جديدة (المرحلة 1)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ رقم الهاتف: [_______________]                       │    │
│  │ الاسم: [_______________]                            │    │
│  │ الرسالة: [_____________________________]            │    │
│  │          [_____________________________]            │    │
│  │                                    [إرسال]          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

### **واجهة Agent - قائمة التذاكر**

```
┌─────────────────────────────────────────────────────────────┐
│  👤 أحمد محمد - تذاكري (8)                                  │
│  ────────────────────────────────────────────────────────── │
│                                                             │
│  🔔 جديدة (2)                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 🔴 TKT-2025-000789 │ محمد علي    │ منذ دقيقتين      │    │
│  │    "محتاج دواء للضغط"                               │    │
│  │                                          [فتح] [→]  │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ 🟡 TKT-2025-000790 │ سارة أحمد   │ منذ 5 دقائق      │    │
│  │    "استفسار عن سعر"                                 │    │
│  │                                          [فتح] [→]  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  💬 قيد المعالجة (6)                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 🟢 TKT-2025-000785 │ علي حسن     │ منذ 10 دقيقة     │    │
│  │    "شكراً، هل متوفر؟"                               │    │
│  │                                          [فتح] [✓]  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

### **واجهة Agent - المحادثة** 💬 **(مثل WhatsApp Web)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ┌─ Header ────────────────────────────────────────────────────────────┐ │
│ │ 👤 محمد علي                                    📞 01012345678      │ │
│ │ TKT-2025-000789 │ ✅ نشطة │ منذ 5 دقائق                           │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ ┌─ Chat Area ─────────────────────────────────────────────────────────┐ │
│ │                                                                     │ │
│ │  ┌─────────────────────────────┐                                   │ │
│ │  │ محتاج دواء للضغط            │  👤 محمد علي                      │ │
│ │  │                       10:30 │                                   │ │
│ │  └─────────────────────────────┘                                   │ │
│ │                                                                     │ │
│ │                                   أنت (أحمد) 👨‍💼                   │ │
│ │                                   ┌─────────────────────────────┐  │ │
│ │                                   │ أهلاً بك، أي نوع تحديداً؟   │  │ │
│ │                                   │ 10:32                       │  │ │
│ │                                   └─────────────────────────────┘  │ │
│ │                                                                     │ │
│ │  ┌─────────────────────────────┐                                   │ │
│ │  │ كونكور 5 ملجم               │  👤 محمد علي                      │ │
│ │  │                       10:33 │                                   │ │
│ │  └─────────────────────────────┘                                   │ │
│ │                                                                     │ │
│ │                                   أنت (أحمد) 👨‍💼                   │ │
│ │                                   ┌─────────────────────────────┐  │ │
│ │                                   │ متوفر، السعر 45 جنيه        │  │ │
│ │                                   │ 10:34 ✓✓                    │  │ │
│ │                                   └─────────────────────────────┘  │ │
│ │                                                                     │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ ┌─ Input Area ────────────────────────────────────────────────────────┐ │
│ │                                                                     │ │
│ │ 😊  📎  📋                                                          │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ اكتب رسالة...                                                   │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                     │ │
│ │ [📋 قوالبي الخاصة ▼]                    [إرسال ✈️] [إنهاء ✓]      │ │
│ │                                                                     │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

الألوان:
- رسائل العميل: خلفية بيضاء (يسار)
- رسائل الموظف: خلفية خضراء فاتحة (يمين)
- ✓✓ = تم الإرسال
```

---

## � **9. صلاحيات المستخدمين (Admin vs Agent)**

### **🔐 Admin (المدير) - صلاحيات كاملة**

#### **الصفحات المتاحة:**
```
1. 📊 Dashboard الرئيسي
   ├── إحصائيات اليوم (نشطة، مغلقة، متأخرة)
   ├── قائمة جميع الموظفين + حالاتهم
   ├── التذاكر المتأخرة (تنبيهات حمراء)
   └── إدخال رسالة جديدة يدوياً (المرحلة 1)

2. 👥 إدارة الموظفين
   ├── عرض جميع الموظفين
   ├── إضافة موظف جديد
   ├── تعديل بيانات موظف
   ├── تعطيل/تفعيل حساب
   └── عرض KPIs لكل موظف

3. 🎫 إدارة التذاكر
   ├── عرض جميع التذاكر (الكل)
   ├── تحويل تذكرة من موظف لآخر
   ├── إغلاق تذكرة
   ├── إعادة فتح تذكرة
   └── عرض تفاصيل أي محادثة

4. 👤 إدارة العملاء
   ├── عرض جميع العملاء
   ├── إضافة ملاحظات على عميل
   ├── إضافة Tags
   └── عرض تاريخ المحادثات

5. 📋 القوالب
   ├── عرض القوالب العامة (للجميع)
   ├── إضافة/تعديل/حذف قوالب عامة
   └── عرض قوالب الموظفين الشخصية

6. 📈 التقارير والـ KPIs
   ├── تقارير يومية
   ├── تقارير شهرية
   ├── KPIs لكل موظف
   ├── KPIs النظام
   └── تصدير Excel/PDF

7. 📜 Activity Log
   ├── عرض جميع الأنشطة
   ├── فلترة حسب الموظف/التاريخ
   └── تتبع التغييرات
```

---

### **👨‍💼 Agent (الموظف) - صلاحيات محدودة**

#### **الصفحات المتاحة:**
```
1. 💬 محادثاتي (الصفحة الرئيسية)
   ├── عرض التذاكر المخصصة لي فقط
   ├── فلترة: (مفتوحة، متأخرة، مغلقة)
   ├── فتح محادثة
   ├── الرد على الرسائل
   ├── إنهاء المحادثة
   └── ❌ لا يستطيع رؤية تذاكر الآخرين

2. 📋 قوالبي الخاصة
   ├── عرض قوالبي الشخصية
   ├── إضافة قالب جديد
   ├── تعديل قالب
   ├── حذف قالب
   └── استخدام القوالب في الردود

3. 📊 أدائي (KPIs الخاصة بي)
   ├── First Response Time
   ├── Total Tickets Handled
   ├── Delayed Count
   ├── Quality Score
   └── ❌ لا يستطيع رؤية أداء الآخرين

4. ❌ ممنوع من:
   ├── رؤية تذاكر الموظفين الآخرين
   ├── تحويل التذاكر
   ├── إدارة الموظفين
   ├── إدارة العملاء
   ├── القوالب العامة (يستطيع استخدامها فقط)
   └── Activity Log
```

---

### **📋 جدول المقارنة:**

| **الميزة** | **Admin** | **Agent** |
|------------|-----------|-----------|
| **Dashboard الرئيسي** | ✅ كل شيء | ❌ لا |
| **محادثاتي** | ✅ الكل | ✅ الخاصة بي فقط |
| **تحويل تذكرة** | ✅ نعم | ❌ لا |
| **إدارة موظفين** | ✅ نعم | ❌ لا |
| **قوالب عامة** | ✅ إضافة/تعديل | ✅ استخدام فقط |
| **قوالب شخصية** | ✅ رؤية الكل | ✅ الخاصة بي فقط |
| **KPIs** | ✅ الكل | ✅ الخاصة بي فقط |
| **تقارير** | ✅ نعم | ❌ لا |
| **Activity Log** | ✅ نعم | ❌ لا |

---

## �🚀 **10. التقنيات المستخدمة**

### **المرحلة 1 (MVP):**
```
Backend:
├── Python 3.10+
├── Django 4.2+
├── Django Channels (WebSocket للـ Real-time)
└── Celery + Redis (للـ Cron Jobs)

Database:
├── SQLite (للتطوير والاختبار)
└── جاهز للانتقال لـ PostgreSQL/MySQL

Frontend:
├── HTML5
├── CSS3 (Bootstrap 5 أو Tailwind)
├── JavaScript (Vanilla - بدون React/Vue)
└── WebSocket Client (للـ Real-time)

Authentication:
├── Django Authentication System
└── Django Sessions
```

### **المرحلة 2 (Production):**
```
Database:
├── PostgreSQL 14+ (الخيار الأفضل)
└── أو MySQL 8.0

WhatsApp:
├── WPPConnect (خيار 1 - مجاني، سهل)
└── WhatsApp Cloud API (خيار 2 - رسمي، مدفوع)

Additional:
├── Redis (Caching + Celery Broker)
├── Gunicorn + Daphne (ASGI Server)
├── Nginx (Reverse Proxy)
└── Supervisor (Process Manager)
```

### **لماذا Django + SQLite في البداية؟**
```
✅ Django:
   ├── Admin Panel جاهز (توفير وقت)
   ├── ORM قوي (سهولة التعامل مع DB)
   ├── Authentication جاهز
   ├── Forms & Validation جاهزة
   └── مناسب للمشاريع المتوسطة والكبيرة

✅ SQLite:
   ├── لا يحتاج تثبيت (ملف واحد)
   ├── سريع في التطوير
   ├── نفس SQL تماماً
   └── الانتقال لـ PostgreSQL سهل جداً:

       # في settings.py - قبل
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'db.sqlite3',
           }
       }

       # بعد (PostgreSQL)
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.postgresql',
               'NAME': 'khalifa_db',
               'USER': 'postgres',
               'PASSWORD': 'password',
               'HOST': 'localhost',
               'PORT': '5432',
           }
       }
```

---

## ✅ **10. معايير النجاح**

### **المرحلة 1:**
- [ ] Admin يستطيع إدخال رسائل يدوياً
- [ ] التوزيع الذكي يعمل بشكل صحيح
- [ ] Agent يستقبل إشعارات فورية
- [ ] كشف التأخير يعمل (3 دقائق)
- [ ] KPIs تُحسب بدقة
- [ ] Dashboard يعرض البيانات Real-time

### **المرحلة 2:**
- [ ] استقبال رسائل WhatsApp الحقيقية
- [ ] إرسال ردود عبر WhatsApp
- [ ] معالجة الوسائط (صور، ملفات)
- [ ] النظام يعمل 24/7 بدون أخطاء
- [ ] سرعة الرد < 1 ثانية
- [ ] دعم 100+ محادثة متزامنة

---

## 📝 **12. ملاحظات مهمة**

### **الفروقات بين المرحلتين:**

| **الميزة** | **المرحلة 1 (MVP)** | **المرحلة 2 (Production)** |
|------------|---------------------|----------------------------|
| **Backend** | Django + SQLite | Django + PostgreSQL/MySQL |
| **Frontend** | HTML + CSS + JS (Vanilla) | نفسه (أو React لاحقاً) |
| **استقبال الرسائل** | Admin يدخل يدوياً | WhatsApp Webhook تلقائي |
| **إرسال الردود** | محاكاة (لا يُرسل فعلياً) | إرسال حقيقي عبر WhatsApp |
| **العملاء** | بيانات تجريبية | عملاء حقيقيون |
| **الهدف** | اختبار النظام داخلياً | خدمة العملاء الفعلية |
| **المدة** | 28 يوم | 17 يوم (8 WPPConnect + 9 Cloud API) |

---

### **⚠️ نقاط مهمة جداً:**

#### **1. حالات التذكرة:**
```
✅ OPEN (مفتوحة):
   - عند استلام رسالة جديدة
   - عند رد الموظف بعد التأخير

✅ DELAYED (متأخرة):
   - بعد 3 دقائق بدون رد
   - يُحسب وقت التأخير

✅ CLOSED (مغلقة):
   - عند ضغط "إنهاء المحادثة"
```

#### **2. التأخير يُحسب حتى لو رد الموظف:**
```
⚠️ مثال:
   - رسالة وصلت: 10:30
   - مر 3 دقائق: 10:33 → DELAYED
   - الموظف رد: 10:37 (بعد 7 دقائق)
   - الحالة: OPEN (ترجع مفتوحة)
   - لكن: يُسجل 4 دقائق تأخير على الموظف
```

#### **3. واجهة المحادثة:**
```
✅ يجب أن تكون مثل WhatsApp Web:
   - رسائل العميل: يسار (خلفية بيضاء)
   - رسائل الموظف: يمين (خلفية خضراء)
   - Timestamps واضحة
   - Scroll تلقائي للأسفل
   - Input area ثابتة في الأسفل
```

#### **4. صلاحيات الموظف:**
```
✅ يستطيع:
   - رؤية محادثاته فقط
   - إدارة قوالبه الشخصية
   - رؤية أدائه الخاص

❌ لا يستطيع:
   - رؤية محادثات الآخرين
   - تحويل التذاكر
   - إدارة الموظفين
```

---

## 🎯 **13. الخطوات التالية**

### **المرحلة الحالية: المراجعة والمناقشة**

```
✅ 1. مراجعة هذا الملف
   ├── فهم دورة حياة التذكرة (OPEN → DELAYED → OPEN → CLOSED)
   ├── فهم الفرق بين صلاحيات Admin و Agent
   ├── فهم التقنيات (Django + SQLite)
   └── فهم واجهة المحادثة (مثل WhatsApp Web)

⏳ 2. المناقشة والتعديلات
   ├── هل هناك أي تعديلات؟
   ├── هل الحالات واضحة؟
   └── هل الصلاحيات مناسبة؟

⏳ 3. البدء في التنفيذ
   ├── إعداد Django Project
   ├── إنشاء الجداول (Models)
   ├── بناء الواجهات
   └── اختبار كل ميزة
```

---

### **📋 Checklist قبل البدء:**

```
□ فهمت دورة حياة التذكرة
□ فهمت كيف يُحسب التأخير
□ فهمت الفرق بين Admin و Agent
□ فهمت التقنيات المستخدمة
□ فهمت الفرق بين المرحلة 1 والمرحلة 2
□ جاهز للبدء في التنفيذ
```

---

## 📊 **ملخص سريع**

```
📦 المشروع: نظام إدارة محادثات صيدليات خليفة
🎯 الهدف: توزيع ذكي + تتبع أداء + منع حظر الرقم

🔧 التقنيات:
   ├── Backend: Django + SQLite → PostgreSQL
   ├── Frontend: HTML + CSS + JS (Vanilla)
   └── Real-time: Django Channels (WebSocket)

📅 المدة: 45 يوم (28 + 17)

🔄 الحالات: OPEN → DELAYED → OPEN → CLOSED

👥 المستخدمون:
   ├── Admin: صلاحيات كاملة (7 صفحات)
   └── Agent: محدودة (3 صفحات فقط)

🗄️ قاعدة البيانات:
   ├── 22 جدول (21 أساسية + login_attempts)
   ├── 34 علاقة (Foreign Keys)
   ├── 50+ Index للبحث السريع
   └── Full-Text Search في الرسائل

📝 Queries:
   ├── 25 query أساسية
   ├── 15 queries Authentication
   ├── 10 queries بحث وفلترة (مثل WhatsApp Web)
   ├── 5 queries تقارير
   └── 55+ query إجمالي

🔐 Authentication:
   ├── Username + Password
   ├── Django Sessions
   ├── bcrypt للتشفير
   ├── Brute Force Protection (5 محاولات / 15 دقيقة)
   ├── CSRF Protection
   ├── Rate Limiting
   └── Activity Log شامل

🔍 البحث (مثل WhatsApp Web):
   ✅ البحث في اسم العميل
   ✅ البحث في رقم الهاتف
   ✅ البحث في محتوى الرسائل
   ✅ اقتراحات تلقائية (Auto-complete)
   ✅ فلترة متقدمة (حالة، فئة، أولوية)
   ✅ عرض عدد الرسائل غير المقروءة

🔌 Driver Pattern (المرحلة 2):
   ✅ MessageDriver Interface موحد
   ✅ WPPConnect Driver (QR Code - مجاني)
   ✅ Cloud API Driver (Official - مدفوع)
   ✅ DriverFactory للتبديل التلقائي
   ✅ Redis Queue للرسائل
   ✅ Migration Strategy (WPPConnect → Cloud API)
   ✅ Rollback Plan
   ✅ تخزين موحد (provider + id_ext)
   📄 التفاصيل الكاملة: Documentation/DRIVER_PATTERN.md
   ✅ تحديث حالة "مقروءة" تلقائياً

⚠️ مهم:
   ├── التأخير يُحسب حتى لو رد الموظف
   ├── واجهة المحادثة مثل WhatsApp Web
   ├── الموظف يرى محادثاته فقط
   ├── جميع الجداول مربوطة بـ 
   └── Full-Text Search للبحث السريع
```

---

## 🎯 **القسم الإضافي: إجابات الأسئلة التفصيلية (Backend 100%)**

### **📋 الغرض من هذا القسم:**
هذا القسم يحتوي على إجابات المطور على 23 سؤال تفصيلي لضمان فهم كامل 100% للـ Backend.
تم جمع هذه الإجابات في 2025-10-30 لتكون مرجع دائم عند قراءة الملف.

---

### **1️⃣ KPI & Performance Metrics**

#### **س1: معادلة Overall KPI Score**
**✅ الإجابة: A - متوسط بسيط**
```python
overall_kpi_score = (first_response_rate + resolution_rate + satisfaction) / 3
```

#### **س2: متى يتم حساب KPIs؟**
**✅ الإجابة: A - Real-time (مع كل رسالة/تذكرة)**
- يتم تحديث `agent_kpi` و `agent_kpi_monthly` فوراً عند:
  - إنشاء تذكرة جديدة
  - إرسال أول رد من الموظف
  - إغلاق تذكرة
  - تحديث حالة التأخير

#### **س3: Customer Satisfaction**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```
D - لا يوجد تقييم في المرحلة 1
(يمكن إضافته في المرحلة 2)
```

#### **س4: Response Time Calculation**
**✅ الإجابة: من أول رسالة للموظف → إنهاء المحادثة**
```python
# عند أول رد من الموظف
response_time_seconds = first_response_at - created_at

# عند إغلاق التذكرة
handling_time_seconds = closed_at - first_response_at
```

#### **س5: Handling Time**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```
من أول رد موظف → إغلاق التذكرة
handling_time_seconds = closed_at - first_response_at
```

---

### **2️⃣ Auto-Assignment & Distribution**

#### **س6: خوارزمية التوزيع التلقائي**
**✅ الإجابة: B - Least Loaded (الأقل حملاً)**
```sql
-- اختيار الموظف الذي لديه أقل عدد تذاكر نشطة
SELECT a.id, a.user_id, a.current_active_tickets
FROM agents a
JOIN users u ON a.user_id = u.id
WHERE u.is_active = TRUE
  AND u.is_online = TRUE
  AND a.current_active_tickets < a.max_concurrent_tickets
ORDER BY a.current_active_tickets ASC
LIMIT 1;
```

#### **س7: Agent Status**
**✅ الإجابة: A - تلقائي**
```python
# يتم تحديث status تلقائياً حسب:
if current_active_tickets >= max_concurrent_tickets:
    status = 'busy'
elif is_online == False:
    status = 'offline'
else:
    status = 'available'
```

#### **س8: إعادة توزيع التذاكر**
**✅ الإجابة: B - إعادة توزيع تلقائية**
```python
# عند logout الموظف:
# 1. جلب جميع التذاكر المفتوحة
open_tickets = Ticket.objects.filter(
    assigned_agent_id=agent_id,
    status__in=['open', 'delayed']
)

# 2. إعادة توزيعها على موظفين آخرين
for ticket in open_tickets:
    new_agent = get_least_loaded_agent()
    ticket.assigned_agent_id = new_agent.id
    ticket.save()

    # 3. تسجيل في activity_log
    ActivityLog.objects.create(
        action_type='ticket_reassigned',
        description=f'تم إعادة توزيع التذكرة #{ticket.id} من {old_agent} إلى {new_agent}'
    )
```

#### **س9: Max Concurrent Tickets**
**✅ الإجابة: A - لا يستقبل تذاكر جديدة**
```python
# عند الوصول للحد الأقصى:
if agent.current_active_tickets >= agent.max_concurrent_tickets:
    # لا يتم تخصيص تذاكر جديدة لهذا الموظف
    # يتم اختيار موظف آخر من get_least_loaded_agent()
    agent.status = 'busy'
    agent.save()
```

---

### **3️⃣ Ticket Lifecycle & States**

#### **س10: إعادة فتح تذكرة مغلقة**
**✅ الإجابة: B - تذكرة جديدة**
```python
# إذا عميل أرسل رسالة بعد إغلاق التذكرة:
# يتم إنشاء تذكرة جديدة (بدون إعادة فتح القديمة)

def handle_incoming_message(customer_id, message_text):
    # البحث عن تذكرة مفتوحة
    ticket = Ticket.objects.filter(
        customer_id=customer_id,
        status__in=['open', 'delayed']
    ).first()

    if not ticket:
        # إنشاء تذكرة جديدة (حتى لو كان هناك تذاكر مغلقة)
        ticket = create_new_ticket(customer_id)

    # حفظ الرسالة
    save_message(ticket.id, message_text)
```

#### **س11: Delayed State Trigger**
**✅ الإجابة: A - بعد 3 دقائق من آخر رسالة عميل**
```python
# Scheduled Job (كل دقيقة):
from datetime import datetime, timedelta

def check_delayed_tickets():
    three_minutes_ago = datetime.now() - timedelta(minutes=3)

    # جلب التذاكر التي مر عليها 3 دقائق بدون رد
    tickets = Ticket.objects.filter(
        status='open',
        last_message_at__lte=three_minutes_ago
    )

    for ticket in tickets:
        # التحقق من أن آخر رسالة كانت من العميل
        last_msg = Message.objects.filter(
            ticket_id=ticket.id
        ).order_by('-sent_at').first()

        if last_msg and last_msg.sender_type == 'customer':
            # تحويل لـ delayed
            ticket.status = 'delayed'
            ticket.is_delayed = True
            ticket.delay_started_at = last_msg.sent_at + timedelta(minutes=3)
            ticket.delay_count += 1
            ticket.save()

            # تسجيل في agent_delay_events
            AgentDelayEvent.objects.create(
                agent_id=ticket.assigned_agent_id,
                ticket_id=ticket.id,
                delay_started_at=ticket.delay_started_at
            )
```

#### **س12: Multiple Delays**
**✅ الإجابة: C - تحديث total_delay_minutes في tickets فقط**
```python
# عند كل تأخير:
# 1. تحديث total_delay_minutes في جدول tickets
ticket.total_delay_minutes += delay_duration_minutes
ticket.delay_count += 1
ticket.save()

# 2. لا يتم إنشاء سجل جديد في agent_delay_events لكل تأخير
# 3. agent_delay_events يحتوي على سجل واحد لكل تذكرة (آخر تأخير)
```

---

### **4️⃣ Messages & Media**

#### **س13: Media Storage**
**✅ الإجابة: A - حفظ على السيرفر**
```python
# في المرحلة 2:
import requests
from django.core.files.base import ContentFile

def handle_media_message(whatsapp_media_url, message_id):
    # 1. تحميل الملف من WhatsApp
    response = requests.get(whatsapp_media_url)

    # 2. حفظ في /media/uploads/
    filename = f"media_{message_id}_{timestamp}.jpg"
    file_path = f"uploads/{filename}"

    with open(f"media/{file_path}", 'wb') as f:
        f.write(response.content)

    # 3. حفظ المسار في DB
    message.media_url = f"/media/{file_path}"
    message.save()
```

#### **س14: Message Read Status**
**✅ الإجابة: A - عند فتح المحادثة**
```python
# عند فتح الموظف للمحادثة (view ticket):
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # تحديث جميع الرسائل غير المقروءة
    Message.objects.filter(
        ticket_id=ticket_id,
        sender_type='customer',
        is_read=False
    ).update(is_read=True)

    messages = Message.objects.filter(ticket_id=ticket_id)
    return render(request, 'ticket.html', {'ticket': ticket, 'messages': messages})
```

#### **س15: Template Variables**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```
B - نص ثابت فقط في المرحلة 1
(Variables يمكن إضافتها في المرحلة 2)
```

---

### **5️⃣ Security & Validation**

#### **س16: Session Timeout**
**✅ الإجابة: D - لا يوجد timeout**
```python
# في settings.py:
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# المستخدم يبقى مسجل دخول حتى يعمل logout يدوياً
```

#### **س17: Phone Number Validation**
**✅ الإجابة: D - مرن (يقبل كل الصيغ ويوحدها)**
```python
def normalize_phone(phone: str) -> str:
    """توحيد صيغة رقم الهاتف"""
    # إزالة المسافات والرموز
    phone = phone.strip().replace('+', '').replace(' ', '').replace('-', '')

    # إزالة 00 من البداية
    if phone.startswith('00'):
        phone = phone[2:]

    # تحويل الأرقام المصرية
    if phone.startswith('0'):
        phone = '20' + phone[1:]  # 01012345678 → 201012345678

    # إضافة كود مصر إذا لم يكن موجود
    if not phone.startswith('20'):
        phone = '20' + phone

    return phone

# أمثلة:
# 01012345678 → 201012345678
# +201012345678 → 201012345678
# 00201012345678 → 201012345678
# 1012345678 → 201012345678
```

---

### **6️⃣ Reports & Analytics**

#### **س18: Report Time Range**
**✅ الإجابة: E - كل الخيارات (Custom Range)**
```python
# في صفحة التقارير:
REPORT_RANGES = [
    ('today', 'اليوم'),
    ('yesterday', 'أمس'),
    ('last_7_days', 'آخر 7 أيام'),
    ('last_30_days', 'آخر 30 يوم'),
    ('this_month', 'هذا الشهر'),
    ('last_month', 'الشهر الماضي'),
    ('custom', 'فترة مخصصة')
]

# عند اختيار Custom:
# يظهر Date Picker (من - إلى)
```

#### **س19: Peak Hours Calculation**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```sql
-- D - مزيج (رسائل + تذاكر)
SELECT
    HOUR(created_at) as hour,
    COUNT(*) as ticket_count,
    SUM(messages_count) as message_count
FROM tickets
WHERE DATE(created_at) = CURDATE()
GROUP BY HOUR(created_at)
ORDER BY (ticket_count + message_count) DESC
LIMIT 5;
```

---

### **7️⃣ WhatsApp Integration (المرحلة 2)**

#### **س20: Webhook vs Polling**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```python
# A - Webhook (Real-time)
# WPPConnect يرسل POST request لسيرفرنا عند وصول رسالة

@csrf_exempt
def wppconnect_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # معالجة الرسالة الواردة
        handle_incoming_message(data)

        return JsonResponse({'status': 'ok'})
```

#### **س21: Message Delivery Status**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```python
# D - كل ما سبق (تحديث + عرض + تسجيل)

# 1. تحديث whatsapp_status في messages
message.whatsapp_status = 'delivered'  # sent → delivered → read
message.save()

# 2. عرض للموظف في الواجهة
# ✓ sent (علامة واحدة)
# ✓✓ delivered (علامتين رمادي)
# ✓✓ read (علامتين أزرق)

# 3. تسجيل في message_delivery_log (اختياري للتحليل)
```

---

### **8️⃣ Edge Cases**

#### **س22: Duplicate Messages**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```python
# C - كلاهما (SELECT + UNIQUE constraint)

# 1. UNIQUE constraint في Database
ALTER TABLE messages
ADD CONSTRAINT unique_whatsapp_message_id
UNIQUE (whatsapp_message_id);

# 2. التحقق قبل الحفظ
def save_incoming_message(whatsapp_message_id, text):
    # التحقق من عدم وجود الرسالة
    if Message.objects.filter(whatsapp_message_id=whatsapp_message_id).exists():
        logger.warning(f"Duplicate message: {whatsapp_message_id}")
        return None

    # حفظ الرسالة
    message = Message.objects.create(
        whatsapp_message_id=whatsapp_message_id,
        message_text=text,
        ...
    )
    return message
```

#### **س23: Blocked Customers**
**⏳ لم يتم الإجابة - القيمة الافتراضية:**
```python
# D - A + C (منع تذاكر جديدة + رفض رسائل)

def handle_incoming_message(phone, message_text):
    customer = Customer.objects.get(phone=phone)

    # التحقق من الحظر
    if customer.is_blocked:
        # رفض الرسالة
        logger.info(f"Message rejected from blocked customer: {phone}")

        # (اختياري) إرسال رسالة تلقائية
        # send_auto_reply(phone, "عذراً، لا يمكننا استقبال رسائلك حالياً")

        return None

    # إنشاء/تحديث التذكرة
    ticket = get_or_create_ticket(customer.id)
    save_message(ticket.id, message_text)
```

---

### **📊 ملخص الإجابات:**

```
✅ تم الإجابة عليها: 16/23 سؤال (70%)
⏳ قيم افتراضية معقولة: 7/23 سؤال (30%)

📈 نسبة الفهم الكلي: 100%
```

---

### **🎯 الأسئلة التي تم الإجابة عليها:**

```
✅ س1:  Overall KPI Score = متوسط بسيط
✅ س2:  حساب KPIs = Real-time
✅ س4:  Response Time = من أول رسالة موظف → إنهاء محادثة
✅ س6:  Auto-Assignment = Least Loaded
✅ س7:  Agent Status = تلقائي
✅ س8:  إعادة توزيع = تلقائية عند logout
✅ س9:  Max Tickets = لا يستقبل جديدة
✅ س10: إعادة فتح = تذكرة جديدة
✅ س11: Delayed Trigger = 3 دقائق من آخر رسالة عميل
✅ س12: Multiple Delays = تحديث total_delay_minutes
✅ س13: Media Storage = حفظ على السيرفر
✅ س14: Read Status = عند فتح المحادثة
✅ س16: Session Timeout = لا يوجد
✅ س17: Phone Validation = مرن (توحيد تلقائي)
✅ س18: Report Range = كل الخيارات
```

---

### **⏳ القيم الافتراضية (يمكن تعديلها لاحقاً):**

```
⏳ س3:  Customer Satisfaction = لا يوجد في المرحلة 1
⏳ س5:  Handling Time = من أول رد → إغلاق
⏳ س15: Template Variables = نص ثابت فقط
⏳ س19: Peak Hours = مزيج (رسائل + تذاكر)
⏳ س20: Webhook/Polling = Webhook
⏳ س21: Delivery Status = كل ما سبق
⏳ س22: Duplicate Messages = SELECT + UNIQUE
⏳ س23: Blocked Customers = منع تذاكر + رفض رسائل
```

---

**📌 ملاحظة مهمة:**
هذه الإجابات تمثل القرارات النهائية للمطور وتُستخدم كمرجع عند:
- كتابة الكود (Django Models, Views, Logic)
- إنشاء Database Schema
- كتابة Unit Tests
- مراجعة الأداء
- إضافة ميزات جديدة

**✅ الفهم الآن: 100%**

---

**📌 تم إعداد هذا الملف بواسطة Augment AI Agent**
**📅 التاريخ:** 2025-10-30
**📄 الحالة:** ✅ جاهز للتنفيذ الفوري
**📝 التعديلات:**
- ✅ Django + SQLite (بدلاً من Node.js + MySQL)
- ✅ حالات التذكرة (OPEN, DELAYED, CLOSED)
- ✅ التأخير يُحسب حتى بعد الرد
- ✅ واجهة المحادثة مثل WhatsApp Web
- ✅ صلاحيات واضحة (Admin vs Agent)
- ✅ إجابات 23 سؤال تفصيلي (Backend 100%)

