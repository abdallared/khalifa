# Pre-Migration Tools - WPPConnect to Elmujib Cloud API

## 🎯 Purpose

These tools help you safely check and switch between WhatsApp providers without breaking your system.

---

## 📋 Available Tools

### **1. Comprehensive Integration Test** (`comprehensive_integration_test.py`) ⭐ NEW!

**Purpose**: End-to-end system validation - Tests EVERYTHING

**What it tests**:
- ✅ Database connectivity and operations
- ✅ Django server and API endpoints
- ✅ Webhook endpoints (WPPConnect & Cloud API)
- ✅ Elmujib Cloud API integration
- ✅ Message flow simulation
- ✅ Driver factory and switching
- ✅ System utilities and phone normalization

**How to run**:
```bash
cd System

# Make sure Django server is running first!
# In one terminal:
python manage.py runserver

# In another terminal:
venv\Scripts\python.exe comprehensive_integration_test.py
```

**When to use**: Before migration to ensure EVERYTHING works perfectly

**Expected output**: All tests pass or only minor warnings

---

### **2. Pre-Migration Check** (`pre_migration_check.py`)

**Purpose**: Quick comparison health check before switching providers

**What it checks**:
- ✅ Current WPPConnect status (configured, reachable, connected)
- ✅ Elmujib Cloud API configuration (credentials, endpoints)
- ✅ API endpoints validation
- ✅ Phone number normalization
- ✅ Side-by-side provider comparison
- ✅ Migration readiness report

**How to run**:
```bash
cd System
venv\Scripts\python.exe pre_migration_check.py
```

**When to use**: Before switching from WPPConnect to Elmujib

---

### **3. Provider Switcher** (`switch_whatsapp_provider.py`)

**Purpose**: Easy switching between WhatsApp providers

**Features**:
- Shows current active provider
- Lists all available providers
- Safe switching with confirmation
- Updates `settings.py` automatically
- Provides restart instructions

**How to run**:
```bash
cd System
venv\Scripts\python.exe switch_whatsapp_provider.py
```

**When to use**: To switch between providers after verification

---

## 🔄 Migration Workflow

### **Step 0: Start Django Server** (Required)
```bash
cd System
python manage.py runserver
```

Keep this running in one terminal.

---

### **Step 1: Run Comprehensive Integration Test** (Recommended)
```bash
# In a NEW terminal
cd System
venv\Scripts\python.exe comprehensive_integration_test.py
```

**Expected output**:
```
Total Tests: 21
Passed: 21
Failed: 0
Success Rate: 100%

✓ PERFECT! ALL SYSTEMS GO!
```

---

### **Step 2: Run Pre-Migration Check**
```bash
venv\Scripts\python.exe pre_migration_check.py
```

**Expected output**:
```
✓ READY TO MIGRATE

Current Provider (WPPConnect):
  [OK] Configured
  [OK] Server Reachable
  [OK] WhatsApp Connected

Target Provider (Elmujib):
  [OK] Configured
  [OK] Credentials Valid
  [OK] Ready for Use
  [OK] API Endpoints
```

### **Step 3: Switch Provider (if ready)**
```bash
venv\Scripts\python.exe switch_whatsapp_provider.py
```

Select option:
- `1` - Keep WPPConnect
- `2` - Switch to Elmujib Cloud (Recommended)
- `3` - Switch to Meta Cloud API

### **Step 4: Restart Django Server**
```bash
# Stop current server (Ctrl+C)
python manage.py runserver
```

### **Step 5: Test New Provider**
```bash
# Test sending a message with new provider
venv\Scripts\python.exe test_send_message_elmujib.py
```

---

## 📊 Check Results Explained

### **WPPConnect Status**

| Status | Meaning | Action |
|--------|---------|--------|
| **Configured** [OK] | Settings loaded | ✓ |
| **Server Reachable** [OK] | WPPConnect running | ✓ |
| **WhatsApp Connected** [OK] | Session active | ✓ Ready to use |
| **WhatsApp Connected** [WARN] | Session disconnected | Scan QR code |
| **Server Reachable** [FAIL] | Server not running | Start WPPConnect |

### **Elmujib Status**

| Status | Meaning | Action |
|--------|---------|--------|
| **Configured** [OK] | Credentials set | ✓ |
| **Credentials Valid** [OK] | Token verified | ✓ |
| **Ready for Use** [OK] | All checks pass | ✓ Ready to migrate |
| **Configured** [FAIL] | Missing credentials | Check `.env` file |

---

## ⚠️ Important Notes

### **Before Migration**
1. ✅ **Backup your database** (PostgreSQL dump)
2. ✅ **Run pre-migration check** to verify both systems
3. ✅ **Test in development** before production
4. ✅ **Document current WPPConnect session** in case of rollback

### **During Migration**
1. ⚠️ **No messages will be sent** during server restart
2. ⚠️ **Active conversations won't be affected** (stored in DB)
3. ⚠️ **Webhook URL may need updating** for Elmujib

### **After Migration**
1. ✅ **Test sending messages** immediately
2. ✅ **Monitor logs** for any errors
3. ✅ **Keep WPPConnect running** as backup (optional)
4. ✅ **Update documentation** with new provider

---

## 🔍 Provider Comparison

| Feature | WPPConnect | Elmujib Cloud API |
|---------|------------|-------------------|
| **Infrastructure** | Local server required | Cloud-based |
| **Reliability** | Depends on server | 99.9% uptime |
| **QR Code** | Required periodically | Not required |
| **Maintenance** | Manual updates | Fully managed |
| **Phone Number** | Personal WhatsApp | Business API |
| **Templates** | Not required | Required for 24h+ |
| **Cost** | Free (self-hosted) | Per-message pricing |
| **Setup Difficulty** | Complex | Simple |

---

## 🚨 Troubleshooting

### **Pre-Check Shows "NOT READY"**

**Problem**: Missing Elmujib credentials
```
[FAIL] ELMUJIB_BEARER_TOKEN
```

**Solution**: Update `.env` file:
```env
ELMUJIB_BEARER_TOKEN=your_actual_token_here
```

---

### **WPPConnect Not Reachable**

**Problem**: WPPConnect server not running
```
[FAIL] Server Reachable
     Cannot connect to WPPConnect server
```

**Solution**: Start WPPConnect server:
```bash
cd wppconnect-server
npm start
```

---

### **After Switch - Messages Not Sending**

**Problem**: Driver changed but server not restarted

**Solution**: Restart Django:
```bash
# Stop with Ctrl+C
python manage.py runserver
```

---

## 📞 Quick Test Commands

### **Test Current Provider**
```bash
cd System
python manage.py shell
```
```python
from conversations.whatsapp_driver import get_whatsapp_driver
driver = get_whatsapp_driver()
print(f"Provider: {driver.provider_name}")
status = driver.get_connection_status()
print(f"Connected: {status.get('connected')}")
```

### **Test Elmujib Specifically**
```bash
venv\Scripts\python.exe test_elmujib_api.py
```

### **Send Test Message**
```bash
venv\Scripts\python.exe test_send_message_elmujib.py
```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `pre_migration_check.py` | Comprehensive health check |
| `switch_whatsapp_provider.py` | Provider switcher tool |
| `test_elmujib_api.py` | Elmujib API test suite |
| `test_send_message_elmujib.py` | Send test message |
| `check_elmujib_status.py` | Quick status check |

---

## ✅ Final Checklist

Before going to production with Elmujib:

- [ ] Run `pre_migration_check.py` - All checks pass
- [ ] Backup database
- [ ] Test Elmujib in development environment
- [ ] Verify phone number normalization works
- [ ] Send test messages successfully
- [ ] Update monitoring/alerts for new provider
- [ ] Document rollback procedure
- [ ] Switch using `switch_whatsapp_provider.py`
- [ ] Restart Django server
- [ ] Monitor first 100 messages
- [ ] Update team documentation

---

## 🔄 Rollback Procedure

If Elmujib has issues, rollback to WPPConnect:

```bash
# 1. Run switcher
venv\Scripts\python.exe switch_whatsapp_provider.py
# Select option 1 (wppconnect)

# 2. Restart Django
# Ctrl+C then:
python manage.py runserver

# 3. Check WPPConnect is running
# Visit: http://localhost:3000

# 4. Verify connection
venv\Scripts\python.exe pre_migration_check.py
```

---

## 📚 Additional Resources

- **Elmujib Setup Guide**: `ELMUJIB_SETUP_COMPLETE.md`
- **API Integration Guide**: `ELMUJIB_CLOUD_API_GUIDE.md`
- **Integration Summary**: `ELMUJIB_INTEGRATION_SUMMARY.md`
- **Django Settings**: `System/khalifa_pharmacy/settings.py`
- **Environment Config**: `.env`

---

**Last Updated**: 2025-11-27  
**System**: Khalifa Pharmacy WhatsApp Integration  
**Status**: ✅ Ready for Migration (100% Tests Passed)
