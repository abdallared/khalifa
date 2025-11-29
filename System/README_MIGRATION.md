# 🚀 PostgreSQL Migration - README
# دليل الترحيل إلى PostgreSQL

Complete migration setup from SQLite to PostgreSQL with virtual environment support.

---

## 📁 Migration Files Created

| File | Purpose |
|------|---------|
| **MIGRATE_TO_POSTGRESQL.bat** | 🚀 Quick launcher from project root |
| **migrate.bat** | 🛠️ Interactive migration tool (in System/) |
| **migrate_to_postgresql.py** | 🐍 Python migration script |
| **verify_database.py** | ✅ Database integrity checker |
| **setup_postgresql.sql** | 📊 PostgreSQL database setup |
| **MIGRATION_GUIDE.md** | 📖 Complete documentation |
| **QUICK_MIGRATION.md** | ⚡ Quick reference guide |
| **.env.example** | 🔧 Configuration template |

---

## 🎯 How to Use

### Quick Start (3 clicks!)

1. **Double-click:** `MIGRATE_TO_POSTGRESQL.bat`
2. **Choose:** Option 6 (Full Migration)
3. **Done!** 🎉

### What it does:
- ✅ Activates virtual environment automatically
- ✅ Backs up SQLite database
- ✅ Installs PostgreSQL driver
- ✅ Prompts for .env update
- ✅ Runs migrations
- ✅ Loads data
- ✅ Verifies everything

---

## 📋 Prerequisites

### Before Migration:
1. **PostgreSQL installed** (15+)
2. **Database created:**
   ```sql
   CREATE DATABASE khalifa_pharmacy_db WITH ENCODING 'UTF8';
   ```
3. **Virtual environment exists:**
   ```bash
   cd System
   python -m venv venv
   call venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

---

## 🔧 Configuration

### Update `.env` file:
```env
DB_ENGINE=postgresql
DB_NAME=khalifa_pharmacy_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 📖 Menu Options

When you run the migration tool:

1. **Backup SQLite Database** - Create backup before migration
2. **Install PostgreSQL Driver** - Install psycopg2 in venv
3. **Run Database Migrations** - Apply Django migrations
4. **Load Backup Data** - Import data from backup
5. **Verify Migration** - Check database integrity
6. **Full Migration** - Complete automated process
7. **Exit** - Close the tool

---

## ✅ Verification

After migration:
```bash
# Option 1: Use verification script
python verify_database.py

# Option 2: Use migration menu (option 5)
```

Checks:
- ✅ Database connection
- ✅ Record counts
- ✅ Foreign key integrity
- ✅ Unique constraints
- ✅ Indexes
- ✅ Arabic text encoding

---

## 🔄 Rollback

If something goes wrong:

1. **Stop servers** (if running)
2. **Edit `.env`:**
   ```env
   DB_ENGINE=sqlite3
   DB_NAME=db.sqlite3
   ```
3. **Restart:** `START_SERVERS_VENV.bat`

Your SQLite database is **never deleted** during migration!

---

## 🆘 Troubleshooting

### "Virtual environment not found"
```bash
cd System
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
```

### "PostgreSQL connection failed"
```bash
# Check if PostgreSQL is running
services.msc  # Windows
# Look for "postgresql" service
```

### "Database does not exist"
```sql
psql -U postgres
CREATE DATABASE khalifa_pharmacy_db WITH ENCODING 'UTF8';
\q
```

### "Permission denied"
```sql
GRANT ALL PRIVILEGES ON DATABASE khalifa_pharmacy_db TO postgres;
```

See **MIGRATION_GUIDE.md** for complete troubleshooting.

---

## 📦 What Gets Installed

In your virtual environment (`System\venv`):
- **psycopg2-binary==2.9.9** - PostgreSQL adapter
- All existing requirements from `requirements.txt`

---

## 🎓 Additional Resources

- **MIGRATION_GUIDE.md** - Complete step-by-step guide
- **QUICK_MIGRATION.md** - Quick reference
- **setup_postgresql.sql** - Database setup script

---

## 🎉 Success Indicators

After successful migration:
- ✅ `migrate.bat` shows "Migration completed successfully!"
- ✅ `verify_database.py` shows all green checkmarks
- ✅ Application starts: `START_SERVERS_VENV.bat`
- ✅ Data visible in application
- ✅ Arabic text displays correctly

---

## 📞 Need Help?

1. Read **MIGRATION_GUIDE.md** for detailed instructions
2. Check logs: `System/logs/django.log`
3. Run verification: `python verify_database.py`

---

**Happy Migrating! 🚀**

صيدليات خليفة - نظام إدارة المحادثات
