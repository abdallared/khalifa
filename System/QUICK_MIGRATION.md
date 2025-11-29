# Quick Migration Guide - SQLite to PostgreSQL
# دليل الترحيل السريع

---

## ⚡ Quick Start (Windows - Using venv)

### 🎯 Option 1: Super Quick (Recommended)
```bash
# From project root - double-click:
MIGRATE_TO_POSTGRESQL.bat

# Or from command line:
MIGRATE_TO_POSTGRESQL.bat
# Then choose option 6 (Full Migration)
```

### 🎯 Option 2: From System Directory
```bash
cd System
migrate.bat
# Choose option 6 (Full Migration)
```

### 🎯 Option 3: Manual Steps

### 1️⃣ Install PostgreSQL
```bash
# Download and install PostgreSQL 15+
# https://www.postgresql.org/download/
```

### 2️⃣ Create Database
```bash
psql -U postgres
```
```sql
CREATE DATABASE khalifa_pharmacy_db WITH ENCODING 'UTF8';
\q
```

### 3️⃣ Activate Virtual Environment
```bash
cd System
call venv\Scripts\activate.bat
```

### 4️⃣ Backup Current Data
```bash
python migrate_to_postgresql.py --backup
```

### 5️⃣ Update Configuration
Edit `.env` file:
```bash
DB_ENGINE=postgresql
DB_NAME=khalifa_pharmacy_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 6️⃣ Migrate Database
```bash
# Install driver (in venv)
pip install psycopg2-binary==2.9.9

# Run migrations
python manage.py migrate

# Load backup data
python manage.py loaddata backups/data_backup_*.json

# Verify
python verify_database.py
```

---

## ✅ Verification

Test the application:
```bash
# From project root
START_SERVERS_VENV.bat
```

Or manually:
```bash
cd System
call venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

Check:
- ✅ Login works
- ✅ Data visible
- ✅ Arabic text OK
- ✅ WhatsApp integration works

---

## 🔄 Rollback (If Needed)

Edit `.env`:
```bash
DB_ENGINE=sqlite3
DB_NAME=db.sqlite3
```

Your SQLite database is still intact!

---

## 📁 Created Files

- **.env.example** - Configuration template
- **migrate_to_postgresql.py** - Migration script
- **verify_database.py** - Verification script
- **setup_postgresql.sql** - Database setup SQL
- **migrate.bat** - Windows batch script
- **MIGRATION_GUIDE.md** - Complete guide

---

## 🆘 Common Issues

**Connection refused?**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
```

**Authentication failed?**
```bash
# Reset password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';
```

**Database doesn't exist?**
```sql
CREATE DATABASE khalifa_pharmacy_db;
```

---

## 📞 Need Help?

See **MIGRATION_GUIDE.md** for detailed instructions and troubleshooting.

---

**That's it! Your database is now running on PostgreSQL! 🎉**
