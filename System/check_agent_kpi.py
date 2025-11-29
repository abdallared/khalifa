import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check agent_kpi table
    cursor.execute("SELECT COUNT(*) FROM agent_kpi")
    count = cursor.fetchone()[0]
    print(f"Total AgentKPI records in database: {count}")
    
    # Check for the specific problematic record
    cursor.execute("SELECT * FROM agent_kpi WHERE agent_id = 56 AND kpi_date = '2025-11-25'")
    records = cursor.fetchall()
    
    if records:
        print(f"\nFound existing record for agent=56, date=2025-11-25:")
        for record in records:
            print(f"  Record: {record}")
    else:
        print(f"\nNo record found for agent=56, date=2025-11-25")
    
    # Show all records
    if count > 0 and count < 20:
        cursor.execute("SELECT agent_id, kpi_date FROM agent_kpi ORDER BY agent_id, kpi_date")
        print(f"\nAll AgentKPI records:")
        for row in cursor.fetchall():
            print(f"  agent={row[0]}, date={row[1]}")
