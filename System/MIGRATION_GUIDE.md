# PostgreSQL Migration Guide
# دليل الترحيل إلى PostgreSQL

Complete guide for migrating from SQLite to PostgreSQL database.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step-by-Step Migration](#step-by-step-migration)
3. [Verification](#verification)
4. [Rollback Procedure](#rollback-procedure)
5. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

### Required Software
- PostgreSQL 15+ installed
- Python 3.10+
- psycopg2-binary package

### Install PostgreSQL
**Windows:**
```bash
# Download from: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

---

## 🚀 Step-by-Step Migration

### Step 1: Activate Virtual Environment & Install PostgreSQL Driver

```bash
cd System
call venv\Scripts\activate.bat
```

Install PostgreSQL driver in venv:
```bash
pip install psycopg2-binary==2.9.9
```

Verify installation:
```bash
pip show psycopg2-binary
```

---

### Step 2: Setup PostgreSQL Database

#### Option A: Using SQL Script (Recommended)
```bash
# Login to PostgreSQL
psql -U postgres

# Run setup script
\i setup_postgresql.sql

# Exit
\q
```

#### Option B: Manual Setup
```sql
-- Create database
CREATE DATABASE khalifa_pharmacy_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

-- Create user (optional)
CREATE USER khalifa_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE khalifa_pharmacy_db TO khalifa_user;

-- Enable extensions
\c khalifa_pharmacy_db
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

---

### Step 3: Backup SQLite Data

**Using automated script (Windows):**
```bash
cd System
migrate.bat
# Choose option 1: Backup SQLite Database
```

**Or manually:**
```bash
cd System
call venv\Scripts\activate.bat
python migrate_to_postgresql.py --backup
```

This will create a backup file in `System/backups/` directory.

**Expected output:**
```
==================================================================
💾 Backing Up SQLite Database
==================================================================

✓ Data backed up to: backups/data_backup_20250125_143022.json
Backup size: 2.45 MB
```

---

### Step 4: Update Environment Configuration

Edit `.env` file:

```bash
# Change these lines:
DB_ENGINE=postgresql
DB_NAME=khalifa_pharmacy_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

**Important:** Keep a copy of old `.env` for rollback!

```bash
cp .env .env.sqlite.backup
```

---

### Step 5: Stop Running Services

```bash
# Stop Django server
# Press Ctrl+C in the terminal running manage.py runserver

# Stop WPPConnect (if running)
# Press Ctrl+C in wppconnect terminal
```

---

### Step 6: Run Django Migrations

```bash
cd System
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, conversations, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying conversations.0001_initial... OK
  ...
```

---

### Step 7: Load Backed Up Data

```bash
# Find your backup file
ls backups/

# Load data (replace TIMESTAMP with your backup timestamp)
python manage.py loaddata backups/data_backup_TIMESTAMP.json
```

**Alternative:** Use the migration script:
```bash
python migrate_to_postgresql.py --verify
```

---

### Step 8: Verify Migration

```bash
python verify_database.py
```

**Expected output:**
```
==================================================================
🔍 Database Configuration
==================================================================

Engine: django.db.backends.postgresql
Database: khalifa_pharmacy_db
✓ PostgreSQL detected

==================================================================
📊 Record Counts
==================================================================

Users.............................................. 15
Agents............................................. 5
Customers.......................................... 234
Tickets............................................ 567
Messages........................................... 1,234
...

✓ All integrity checks passed
```

---

### Step 9: Test Application

**Using automated script (Windows):**
```bash
# From project root
START_SERVERS_VENV.bat
```

**Or manually:**
```bash
# Terminal 1: Django server (with venv)
cd System
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000

# Terminal 2: WPPConnect
cd wppconnect-server
npm start
```

Test the following:
- ✅ Login to admin panel
- ✅ View customers
- ✅ View tickets
- ✅ Send/receive messages
- ✅ Arabic text displays correctly
- ✅ Search functionality works
- ✅ KPI reports load

---

## ✅ Verification Checklist

Run these checks after migration:

### 1. Database Connection
```bash
python manage.py dbshell
```

Should connect to PostgreSQL (not SQLite).

### 2. Record Counts
```bash
python manage.py shell
```
```python
from conversations.models import User, Customer, Ticket, Message
print(f"Users: {User.objects.count()}")
print(f"Customers: {Customer.objects.count()}")
print(f"Tickets: {Ticket.objects.count()}")
print(f"Messages: {Message.objects.count()}")
```

Compare counts with pre-migration counts.

### 3. Foreign Keys
```bash
python verify_database.py
```

All foreign key checks should pass.

### 4. Arabic Text
Check if Arabic text displays correctly:
```python
from conversations.models import User
user = User.objects.filter(full_name__regex=r'[\u0600-\u06FF]').first()
print(user.full_name)  # Should display Arabic correctly
```

### 5. Performance Test
```python
import time
from conversations.models import Message

start = time.time()
messages = list(Message.objects.select_related('ticket', 'sender')[:100])
elapsed = time.time() - start

print(f"Query time: {elapsed:.3f}s")  # Should be fast (< 1s)
```

---

## 🔄 Rollback Procedure

If migration fails, rollback to SQLite:

### Step 1: Stop Services
```bash
# Stop Django server (Ctrl+C)
```

### Step 2: Restore .env
```bash
cp .env.sqlite.backup .env
```

Or manually edit `.env`:
```bash
DB_ENGINE=sqlite3
DB_NAME=db.sqlite3
```

### Step 3: Restart Application
```bash
python manage.py runserver 0.0.0.0:8000
```

Your SQLite database (`db.sqlite3`) is still intact!

---

## 🔧 Troubleshooting

### Issue 1: Connection Refused
**Error:** `connection to server at "localhost" (::1), port 5432 failed`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # macOS
services.msc                      # Windows

# Start PostgreSQL
sudo systemctl start postgresql   # Linux
brew services start postgresql    # macOS
```

---

### Issue 2: Authentication Failed
**Error:** `FATAL: password authentication failed for user "postgres"`

**Solution:**
1. Reset PostgreSQL password:
```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';
\q
```

2. Update `.env` file with correct password

---

### Issue 3: Database Does Not Exist
**Error:** `FATAL: database "khalifa_pharmacy_db" does not exist`

**Solution:**
```bash
psql -U postgres
CREATE DATABASE khalifa_pharmacy_db;
\q
```

---

### Issue 4: Permission Denied
**Error:** `permission denied for schema public`

**Solution:**
```sql
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

---

### Issue 5: Encoding Issues with Arabic
**Error:** Arabic text displays as `???` or garbled

**Solution:**
Ensure database encoding is UTF8:
```sql
ALTER DATABASE khalifa_pharmacy_db SET client_encoding TO 'UTF8';
```

In Django settings (already configured):
```python
DATABASES = {
    'default': {
        'OPTIONS': {
            'client_encoding': 'UTF8',
        }
    }
}
```

---

### Issue 6: Data Loading Fails
**Error:** `IntegrityError: duplicate key value violates unique constraint`

**Solution:**
1. Fresh start - drop and recreate database:
```sql
DROP DATABASE khalifa_pharmacy_db;
CREATE DATABASE khalifa_pharmacy_db WITH ENCODING 'UTF8';
```

2. Run migrations again:
```bash
python manage.py migrate
```

3. Load data again:
```bash
python manage.py loaddata backups/data_backup_TIMESTAMP.json
```

---

### Issue 7: Slow Queries
**Problem:** Queries are slower than SQLite

**Solution:**
1. Analyze tables:
```sql
ANALYZE;
```

2. Create missing indexes (Django should auto-create them):
```bash
python manage.py sqlmigrate conversations 0001
```

3. Check query performance:
```sql
EXPLAIN ANALYZE SELECT * FROM messages WHERE ticket_id = 1;
```

---

## 📊 Performance Optimization

After migration, optimize PostgreSQL:

### 1. Vacuum and Analyze
```sql
VACUUM ANALYZE;
```

### 2. Update Statistics
```sql
ANALYZE verbose;
```

### 3. Tune PostgreSQL Config
Edit `postgresql.conf`:
```ini
# Increase memory (adjust based on your RAM)
shared_buffers = 256MB
work_mem = 16MB
maintenance_work_mem = 128MB

# Connection settings
max_connections = 100
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## 📝 Post-Migration Checklist

- [ ] All data migrated successfully
- [ ] Foreign keys intact
- [ ] Indexes created
- [ ] Arabic text displays correctly
- [ ] Application runs without errors
- [ ] WhatsApp integration works
- [ ] Search functionality works
- [ ] KPI calculations accurate
- [ ] Backup SQLite database archived
- [ ] PostgreSQL backups configured
- [ ] Performance acceptable

---

## 🔐 Security Best Practices

1. **Change default passwords:**
```sql
ALTER USER postgres WITH PASSWORD 'strong_random_password';
```

2. **Restrict remote access** (if not needed):
Edit `pg_hba.conf`:
```
# Only allow local connections
local   all   all   md5
host    all   all   127.0.0.1/32   md5
```

3. **Enable SSL** (production):
```sql
ALTER SYSTEM SET ssl = on;
```

4. **Regular backups:**
```bash
# Daily backup script
pg_dump -U postgres khalifa_pharmacy_db > backup_$(date +%Y%m%d).sql
```

---

## 📞 Support

If you encounter issues not covered here:

1. Check Django logs: `System/logs/django.log`
2. Check PostgreSQL logs: `/var/log/postgresql/`
3. Run verification script: `python verify_database.py`
4. Test connection: `python manage.py dbshell`

---

## 📚 Additional Resources

- [Django PostgreSQL Notes](https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

---

**Migration completed successfully! 🎉**
