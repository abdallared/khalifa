import json

backup_file = 'backups/data_backup_20251125_123713.json'

with open(backup_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find ALL AgentKPI records
agentkpi_records = [(i, r) for i, r in enumerate(data) if r.get('model') == 'conversations.agentkpi']

print(f"Total AgentKPI records: {len(agentkpi_records)}")

# Find all occurrences of agent=56, date=2025-11-25
target_agent = 56
target_date = '2025-11-25'

print(f"\nSearching for agent={target_agent}, date={target_date}...")
matches = []
for idx, record in agentkpi_records:
    if record['fields'].get('agent') == target_agent and record['fields'].get('kpi_date') == target_date:
        matches.append((idx, record))
        print(f"\nFound at JSON index {idx}:")
        print(f"  PK: {record.get('pk')}")
        print(f"  Agent: {record['fields'].get('agent')}")
        print(f"  KPI Date: {record['fields'].get('kpi_date')}")

print(f"\nTotal matches: {len(matches)}")

# Also check for any records that come BEFORE this in the JSON that might be related
if matches:
    first_match_idx = matches[0][0]
    print(f"\n10 records BEFORE first match (index {first_match_idx}):")
    start_idx = max(0, first_match_idx - 10)
    for i in range(start_idx, first_match_idx):
        rec = data[i]
        print(f"  [{i}] Model: {rec.get('model')}, PK: {rec.get('pk')}")
