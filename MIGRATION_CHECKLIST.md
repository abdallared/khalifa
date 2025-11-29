# Migration Checklist - WPPConnect to Elmujib Cloud API

## ✅ Pre-Migration Checklist

Complete this checklist before switching to Elmujib Cloud API.

---

## 🔍 Step 1: Run Comprehensive Tests

### **Test 1: Comprehensive Integration Test** (Required)

**Purpose**: Tests everything end-to-end (database, Django, webhooks, API, message flow)

**Command**:
```bash
cd System

# Make sure Django server is running in another terminal
python manage.py runserver

# Then run the test
venv\Scripts\python.exe comprehensive_integration_test.py
```

**Expected Result**: ✅ All tests pass or only minor warnings

---

### **Test 2: Pre-Migration Check** (Required)

**Purpose**: Compares WPPConnect vs Elmujib configuration

**Command**:
```bash
venv\Scripts\python.exe pre_migration_check.py
```

**Expected Result**: ✅ "READY TO MIGRATE"

---

### **Test 3: Elmujib API Test** (Optional but Recommended)

**Purpose**: Validates Elmujib API specifically

**Command**:
```bash
venv\Scripts\python.exe test_elmujib_api.py
```

**Expected Result**: ✅ 24/24 tests passed (100%)

---

## 📋 Step 2: Verify Configurations

### **2.1 Check Environment Variables**

Open `.env` file and verify:

```env
# Elmujib Configuration
ELMUJIB_API_BASE_URL=https://elmujib.com/api
ELMUJIB_VENDOR_UID=a414ed0c-cd3f-4b30-ad1c-f8e548248553
ELMUJIB_BEARER_TOKEN=xY7htGpBoLcB2Y4MVArK...  # Real token, not placeholder
ELMUJIB_AUTH_METHOD=query  # or 'header'

# WPPConnect Configuration (Keep for rollback)
WPPCONNECT_PORT=3000
WPPCONNECT_HOST=localhost
WPPCONNECT_SESSION_NAME=khalifa-pharmacy
WHATSAPP_API_KEY=khalifa-pharmacy-secret-key-2025
```

**Checklist**:
- [ ] `ELMUJIB_BEARER_TOKEN` is NOT "your_bearer_token_here"
- [ ] `ELMUJIB_VENDOR_UID` is filled
- [ ] `ELMUJIB_API_BASE_URL` is correct
- [ ] `ELMUJIB_AUTH_METHOD` is set (query or header)
- [ ] WPPConnect settings are still present (for rollback)

---

### **2.2 Check Django Settings**

Open `System/khalifa_pharmacy/settings.py` and verify:

```python
# Line ~328
WHATSAPP_DRIVER = 'wppconnect'  # Current driver

# Elmujib settings should be present (lines ~344-349)
ELMUJIB_API_BASE_URL = os.getenv('ELMUJIB_API_BASE_URL', 'https://elmujib.com/api')
ELMUJIB_VENDOR_UID = os.getenv('ELMUJIB_VENDOR_UID', '')
# ... etc
```

**Checklist**:
- [ ] `WHATSAPP_DRIVER` currently set to 'wppconnect'
- [ ] All Elmujib settings are present in settings.py
- [ ] Settings load from `.env` file correctly

---

## 💾 Step 3: Backup Everything

### **3.1 Database Backup**

```bash
cd System

# Create backup directory if not exists
mkdir -p backups

# PostgreSQL Backup
pg_dump -h localhost -U postgres -d khalifa_db > backups/pre_migration_backup_$(date +%Y%m%d_%H%M%S).sql

# Or use Django backup command
python manage.py dumpdata > backups/django_data_backup.json
```

**Checklist**:
- [ ] Database backup created
- [ ] Backup file size is reasonable (not 0 bytes)
- [ ] Backup location documented

---

### **3.2 Code Backup**

```bash
# Create a git commit or zip backup
git add .
git commit -m "Pre-migration backup - WPPConnect to Elmujib"

# Or create zip backup
# (Windows)
tar -czf khalefa_whats_backup_$(date +%Y%m%d).tar.gz System/ .env
```

**Checklist**:
- [ ] Code committed to git or backed up
- [ ] `.env` file backed up separately
- [ ] Backup stored safely

---

## 🔄 Step 4: Migration Process

### **4.1 Check System Status**

Before switching, verify:

```bash
# Check Django is running
curl http://127.0.0.1:8000/

# Check database is accessible
python manage.py dbshell
# Type \q to exit

# Check current conversations count
python manage.py shell
>>> from conversations.models import Customer, Ticket
>>> print(f"Customers: {Customer.objects.count()}")
>>> print(f"Tickets: {Ticket.objects.count()}")
>>> exit()
```

**Checklist**:
- [ ] Django server running on port 8000
- [ ] Database accessible
- [ ] No active conversations being handled (optional)

---

### **4.2 Switch Provider**

```bash
cd System
venv\Scripts\python.exe switch_whatsapp_provider.py
```

**Steps**:
1. Script shows current provider: `wppconnect`
2. Select option: `2` (elmujib_cloud)
3. Confirm: `yes`
4. Verify message: "✓ Successfully switched to elmujib_cloud"

**Checklist**:
- [ ] Provider switch completed successfully
- [ ] No error messages displayed

---

### **4.3 Restart Django Server**

```bash
# In the terminal running Django server:
# Press Ctrl+C to stop

# Then restart:
python manage.py runserver
```

**Wait for**:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Checklist**:
- [ ] Server stopped cleanly
- [ ] Server restarted successfully
- [ ] No errors in startup logs

---

## ✅ Step 5: Post-Migration Verification

### **5.1 Verify Driver Switched**

```bash
python manage.py shell
```

```python
from conversations.whatsapp_driver import get_whatsapp_driver

driver = get_whatsapp_driver()
print(f"Current driver: {driver.provider_name}")
print(f"Connected: {driver.get_connection_status()}")

# Should show:
# Current driver: elmujib_cloud
# Connected: {'success': True, 'connected': True, ...}
```

**Checklist**:
- [ ] Driver is `elmujib_cloud`
- [ ] Connection status shows `connected: True`

---

### **5.2 Test Sending Message**

```bash
venv\Scripts\python.exe test_send_message_elmujib.py
```

**Edit the file first to add your phone number**, then run.

**Expected Output**:
```
✓ Message sent successfully!
  Message ID: wamid_xxx...
  Provider: elmujib_cloud
```

**Checklist**:
- [ ] Message sent successfully
- [ ] Message ID received
- [ ] You received the message on WhatsApp

---

### **5.3 Test Webhook (if possible)**

Send a message from WhatsApp to your business number and check:

```bash
# Check Django logs for incoming webhook
# Should see:
# INFO whatsapp_driver Webhook received from: 201234567890
```

**Checklist**:
- [ ] Webhook receives messages
- [ ] Customer created/updated in database
- [ ] Message stored correctly

---

### **5.4 Monitor System**

```bash
# Watch Django logs
python manage.py runserver

# In another terminal, check recent messages
python manage.py shell
```

```python
from conversations.models import Message
from datetime import datetime, timedelta

# Messages in last hour
recent = Message.objects.filter(
    created_at__gte=datetime.now() - timedelta(hours=1)
).order_by('-created_at')[:10]

for msg in recent:
    print(f"{msg.created_at} - {msg.customer.phone_number}: {msg.message_text[:50]}")
```

**Checklist**:
- [ ] New messages appear in database
- [ ] Timestamps are correct
- [ ] No errors in logs

---

## 🚨 Rollback Procedure

If something goes wrong, rollback immediately:

### **Quick Rollback**

```bash
cd System

# 1. Switch back to WPPConnect
venv\Scripts\python.exe switch_whatsapp_provider.py
# Select option 1 (wppconnect)
# Confirm: yes

# 2. Restart Django
# Ctrl+C to stop, then:
python manage.py runserver

# 3. Verify WPPConnect is running
# Check: http://localhost:3000

# 4. Test WPPConnect connection
python manage.py shell
```

```python
from conversations.whatsapp_driver import get_whatsapp_driver

driver = get_whatsapp_driver()
print(f"Driver: {driver.provider_name}")  # Should be 'wppconnect'
print(f"Status: {driver.get_connection_status()}")
```

---

## 📊 Migration Success Criteria

Your migration is successful if:

| Criteria | Status |
|----------|--------|
| ✅ All pre-migration tests pass | Required |
| ✅ Driver switches to elmujib_cloud | Required |
| ✅ Django restarts without errors | Required |
| ✅ Test message sends successfully | Required |
| ✅ Message received on WhatsApp | Required |
| ✅ Webhooks receive messages | Required |
| ✅ Database updates correctly | Required |
| ✅ No errors in Django logs | Required |
| ⚠️ WPPConnect still available for rollback | Recommended |

---

## 📝 Important Notes

### **During Migration**

- ⚠️ **Downtime**: ~30 seconds during server restart
- ⚠️ **Messages**: May be delayed during restart
- ⚠️ **Conversations**: Existing conversations remain in database
- ⚠️ **History**: All message history preserved

### **After Migration**

- ✅ **Phone Number**: May be different (Business API number)
- ✅ **Templates**: May be required for messages after 24 hours
- ✅ **QR Code**: No longer needed
- ✅ **Maintenance**: Fully managed by Elmujib

### **Cost Considerations**

- **WPPConnect**: Free (self-hosted)
- **Elmujib**: Per-message pricing (check your plan)
- **Recommendation**: Monitor first 100 messages for cost estimation

---

## 🔧 Troubleshooting

### **Issue: Tests fail with "Django server not running"**

**Solution**:
```bash
cd System
python manage.py runserver
```

Run tests in a different terminal.

---

### **Issue: "ELMUJIB_BEARER_TOKEN not configured"**

**Solution**:
1. Check `.env` file has real token (not placeholder)
2. Restart Django server after editing `.env`

---

### **Issue: "Database connection failed"**

**Solution**:
```bash
# Check PostgreSQL is running
# Windows:
services.msc
# Look for "PostgreSQL"

# Test connection
psql -h localhost -U postgres -d khalifa_db
```

---

### **Issue: "Message sent but not received"**

**Possible causes**:
1. Wrong phone number format (must be 201xxxxxxxxxx)
2. Number not registered with Business API
3. 24-hour window expired (need template message)

**Solution**:
- Check phone normalization
- Verify number in Elmujib dashboard
- Use template message if needed

---

## 📞 Support

If you encounter issues:

1. Check Django logs: `System/logs/django.log`
2. Check database: `python manage.py dbshell`
3. Re-run tests: `comprehensive_integration_test.py`
4. Review error messages carefully
5. Rollback if needed (see Rollback Procedure above)

---

## ✅ Final Checklist

Before declaring migration complete:

- [ ] All pre-migration tests passed
- [ ] Database backed up
- [ ] Code backed up
- [ ] Provider switched successfully
- [ ] Django restarted without errors
- [ ] Test message sent and received
- [ ] Webhooks working
- [ ] No errors in logs for 30 minutes
- [ ] Rollback procedure documented
- [ ] Team informed of migration
- [ ] Monitoring set up for new provider

---

**Migration Date**: _____________  
**Performed By**: _____________  
**Duration**: _____________  
**Status**: [ ] Success  [ ] Rolled Back  
**Notes**: 

_____________________________________________

---

**Last Updated**: 2025-11-27  
**System**: Khalifa Pharmacy WhatsApp Integration  
**Version**: Production-Ready
