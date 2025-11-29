import json
import sys
from collections import defaultdict

# Read backup file
backup_file = 'backups/data_backup_20251125_123713.json'
output_file = 'backups/data_backup_20251125_123713_dedup.json'

print(f"Reading backup from {backup_file}...")

with open(backup_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# Track unique records for models with unique_together constraints
seen_agentkpi = set()  # (agent, kpi_date)
seen_agentkpi_monthly = set()  # (agent, month)
seen_agent_template = set()  # (agent, name)

deduplicated_data = []
duplicates_removed = 0

for record in data:
    model = record.get('model')
    fields = record.get('fields', {})
    pk = record.get('pk')
    
    # Handle AgentKPI duplicates
    if model == 'conversations.agentkpi':
        key = (fields.get('agent'), fields.get('kpi_date'))
        if key in seen_agentkpi:
            print(f"Removing duplicate AgentKPI: agent={key[0]}, kpi_date={key[1]}, pk={pk}")
            duplicates_removed += 1
            continue
        seen_agentkpi.add(key)
    
    # Handle AgentKPIMonthly duplicates
    elif model == 'conversations.agentkpimonthly':
        key = (fields.get('agent'), fields.get('month'))
        if key in seen_agentkpi_monthly:
            print(f"Removing duplicate AgentKPIMonthly: agent={key[0]}, month={key[1]}, pk={pk}")
            duplicates_removed += 1
            continue
        seen_agentkpi_monthly.add(key)
    
    # Handle AgentTemplate duplicates
    elif model == 'conversations.agenttemplate':
        key = (fields.get('agent'), fields.get('name'))
        if key in seen_agent_template:
            print(f"Removing duplicate AgentTemplate: agent={key[0]}, name={key[1]}, pk={pk}")
            duplicates_removed += 1
            continue
        seen_agent_template.add(key)
    
    deduplicated_data.append(record)

print(f"\nDuplicates removed: {duplicates_removed}")
print(f"Clean records: {len(deduplicated_data)}")

# Write deduplicated data
print(f"\nWriting deduplicated backup to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(deduplicated_data, f, ensure_ascii=False, indent=2)

print("[SUCCESS] Deduplication complete!")
