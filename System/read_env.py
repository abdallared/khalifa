with open(r'..\.env', 'r', encoding='utf-8') as f:
    for line in f:
        if 'DB_' in line and not line.strip().startswith('#'):
            print(line.strip())
