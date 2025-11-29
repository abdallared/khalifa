import json

backup_file = 'backups/data_backup_20251125_123713.json'

with open(backup_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find AgentKPI records for agent 56
agentkpi_records = [r for r in data if r.get('model') == 'conversations.agentkpi' and r['fields'].get('agent') == 56]

print(f"Total AgentKPI records for agent 56: {len(agentkpi_records)}")
print("\nAll records for agent 56:")
for i, record in enumerate(agentkpi_records):
    print(f"  PK: {record.get('pk')}, Date: {record['fields'].get('kpi_date')}")

# Check for duplicate dates
from collections import Counter
dates = [r['fields'].get('kpi_date') for r in agentkpi_records]
date_counts = Counter(dates)

print("\n\nDate counts:")
for date, count in date_counts.items():
    if count > 1:
        print(f"  {date}: {count} times [DUPLICATE]")
        # Show which PKs have this date
        pks = [r.get('pk') for r in agentkpi_records if r['fields'].get('kpi_date') == date]
        print(f"    PKs: {pks}")
    else:
        print(f"  {date}: {count} time")
