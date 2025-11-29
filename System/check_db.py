import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.db import connection

# Test database connection
print(f"Database Engine: {connection.settings_dict['ENGINE']}")
print(f"Database Name: {connection.settings_dict['NAME']}")
print(f"Database User: {connection.settings_dict['USER']}")
print(f"Database Host: {connection.settings_dict['HOST']}")
print(f"Database Port: {connection.settings_dict['PORT']}")

# Try to connect
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"\n[SUCCESS] Connected to database!")
        print(f"PostgreSQL Version: {version[0]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"\nExisting tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
except Exception as e:
    print(f"\n[ERROR] Failed to connect: {e}")
    sys.exit(1)
