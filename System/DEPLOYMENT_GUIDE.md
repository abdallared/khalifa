# 🚀 Deployment Guide - Khalifa Pharmacy System
# دليل نشر نظام صيدليات خليفة

## 📋 Prerequisites / المتطلبات

### Required Software / البرامج المطلوبة:
1. **Python 3.10+** (Tested with Python 3.14)
2. **PostgreSQL 13+** (Tested with PostgreSQL 18.1)
3. **Git** (for version control)

### System Requirements / متطلبات النظام:
- OS: Windows 10/11, Linux, or macOS
- RAM: Minimum 2GB (4GB+ recommended)
- Disk Space: Minimum 500MB
- Network: Internet connection for initial setup

---

## 🔧 Step 1: Install PostgreSQL / تثبيت PostgreSQL

### Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run installer and set password for `postgres` user
3. Note the port (default: 5432)

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS:
```bash
brew install postgresql@18
brew services start postgresql@18
```

---

## 📦 Step 2: Setup Project / إعداد المشروع

### 1. Clone/Download Project:
```bash
cd /path/to/your/projects
# If using git:
git clone <repository-url>
cd khalefa_Whats/System
```

### 2. Create Virtual Environment:
```bash
# Create venv
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies:
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed Django-4.2.7 djangorestframework-3.14.0 psycopg-3.2.13 ...
```

---

## 🗄️ Step 3: Configure Database / تكوين قاعدة البيانات

### 1. Create PostgreSQL Database:
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE khalifa_db;

-- Create user (optional)
CREATE USER khalifa_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE khalifa_db TO khalifa_user;

-- Exit
\q
```

### 2. Configure Environment Variables:
Create `.env` file in `System/` directory:

```bash
# Copy example file
cp .env.example .env
```

Edit `.env` file:
```ini
# Database Configuration
DB_ENGINE=postgresql
DB_NAME=khalifa_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=600
DB_CONN_TIMEOUT=10

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# WhatsApp Integration
WPPCONNECT_URL=http://localhost:21465
WPPCONNECT_SECRET=your_wppconnect_secret
```

---

## 🔄 Step 4: Run Migrations / تشغيل الترحيلات

```bash
# Check configuration
python manage.py check

# Create migrations (if needed)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, ...
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   ...
```

---

## 👤 Step 5: Create Admin User / إنشاء مستخدم مدير

```bash
python manage.py createsuperuser

# Enter:
# - Username: admin
# - Email: admin@example.com
# - Password: ********
# - Password (again): ********
```

---

## 🚀 Step 6: Run Development Server / تشغيل خادم التطوير

```bash
python manage.py runserver

# Server will start at: http://127.0.0.1:8000/
```

Access:
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API**: http://127.0.0.1:8000/api/
- **WhatsApp Status**: http://127.0.0.1:8000/api/whatsapp/status/

---

## 📊 Step 7: Verify Installation / التحقق من التثبيت

Run verification script:
```bash
python verify_database.py
```

**Expected Output:**
```
✅ PostgreSQL Connection Test: PASSED
✅ Django System Check: PASSED
✅ Database Records Count: PASSED
✅ Serializers Test: PASSED
✅ URL Configuration Test: PASSED
```

---

## 🔄 Step 8: Load Backup Data (Optional) / استعادة البيانات

If you have a backup file:

```bash
# For SQL backup:
psql -U postgres -d khalifa_db < pg_backup_1.sql

# For JSON backup:
python manage.py loaddata path/to/backup.json
```

---

## 🎯 Deployment to Production / النشر على خادم الإنتاج

### 1. Update Settings for Production:

Edit `.env`:
```ini
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=generate-strong-random-key
```

### 2. Collect Static Files:
```bash
python manage.py collectstatic --noinput
```

### 3. Use Production Server (Gunicorn):
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn khalifa_pharmacy.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 4. Setup Nginx (Recommended):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/khalefa_Whats/System/static/;
    }

    location /media/ {
        alias /path/to/khalefa_Whats/System/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 Security Checklist / قائمة الأمان

- [ ] Change default PostgreSQL password
- [ ] Generate strong Django SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS correctly
- [ ] Setup SSL/TLS certificate
- [ ] Enable PostgreSQL connection encryption
- [ ] Regular database backups
- [ ] Update dependencies regularly
- [ ] Configure firewall rules
- [ ] Enable Django security middleware

---

## 🛠️ Troubleshooting / حل المشكلات

### Issue: "No module named 'psycopg'"
**Solution:**
```bash
pip install psycopg[binary]==3.2.13
```

### Issue: "Connection refused" to PostgreSQL
**Solution:**
1. Check PostgreSQL service is running:
   ```bash
   # Windows:
   net start postgresql-x64-18
   
   # Linux:
   sudo systemctl status postgresql
   ```
2. Check connection settings in `.env`
3. Verify PostgreSQL is listening on correct port

### Issue: "FATAL: role does not exist"
**Solution:**
```bash
# Create PostgreSQL user
createuser -U postgres -P khalifa_user
```

### Issue: Migration errors
**Solution:**
```bash
# Reset migrations (⚠️ Development only)
python manage.py migrate --fake <app_name> zero
python manage.py migrate <app_name>
```

---

## 📝 Maintenance / الصيانة

### Daily Backup:
```bash
# PostgreSQL backup
pg_dump -U postgres khalifa_db > backup_$(date +%Y%m%d).sql

# Or use the provided script:
python create_pg_backup.py
```

### Check System Health:
```bash
python manage.py check --deploy
```

### View Logs:
```bash
tail -f logs/django.log
```

---

## 📞 Support / الدعم

For issues or questions:
- Check logs: `System/logs/django.log`
- Review documentation
- Contact: محمد فارس - AI Software Engineer

---

## ✅ Verification Checklist / قائمة التحقق

- [ ] Python 3.10+ installed
- [ ] PostgreSQL installed and running
- [ ] Virtual environment created and activated
- [ ] All requirements installed successfully
- [ ] `.env` file configured correctly
- [ ] Database created
- [ ] Migrations applied
- [ ] Superuser created
- [ ] Development server runs without errors
- [ ] Admin panel accessible
- [ ] API endpoints working
- [ ] WhatsApp integration configured
- [ ] Backup created successfully

---

**Last Updated:** 2025-11-25
**Version:** 1.0 (PostgreSQL Migration Complete)
