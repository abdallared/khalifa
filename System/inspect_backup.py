import json

backup_file = 'backups/data_backup_20251125_123713.json'

with open(backup_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find AgentKPI records
agentkpi_records = [r for r in data if r.get('model') == 'conversations.agentkpi']

print(f"Total AgentKPI records: {len(agentkpi_records)}")
print("\nFirst 3 AgentKPI records:")
for i, record in enumerate(agentkpi_records[:3]):
    print(f"\nRecord {i+1}:")
    print(f"  PK: {record.get('pk')}")
    print(f"  Agent: {record['fields'].get('agent')}")
    print(f"  KPI Date: {record['fields'].get('kpi_date')}")
    
# Find duplicates
from collections import defaultdict
duplicates = defaultdict(list)
for record in agentkpi_records:
    key = (str(record['fields'].get('agent')), record['fields'].get('kpi_date'))
    duplicates[key].append(record.get('pk'))

print("\n\nDuplicate agent+kpi_date combinations:")
for key, pks in duplicates.items():
    if len(pks) > 1:
        print(f"  Agent: {key[0]}, Date: {key[1]} -> PKs: {pks}")
