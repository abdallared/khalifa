import re
import os

def has_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
    return arabic_pattern.search(text) is not None

def wrap_arabic_text(content):
    lines = content.split('\n')
    result_lines = []
    
    for line in lines:
        if '{%' in line or '{{' in line:
            parts = re.split(r'(>|<)', line)
            new_parts = []
            
            for i, part in enumerate(parts):
                if has_arabic(part) and not '{%' in part and not '{{' in part:
                    arabic_matches = re.findall(r'([^\u0600-\u06FF]*)([\u0600-\u06FF\s,.!?؟،]+)([^\u0600-\u06FF]*)', part)
                    if arabic_matches:
                        temp = part
                        for match in arabic_matches:
                            before, arabic_text, after = match
                            arabic_text = arabic_text.strip()
                            if arabic_text and 'trans' not in temp:
                                original = before + arabic_text + after
                                replacement = before + '{% trans "' + arabic_text + '" %}' + after
                                temp = temp.replace(original, replacement, 1)
                        new_parts.append(temp)
                    else:
                        new_parts.append(part)
                else:
                    new_parts.append(part)
            
            result_lines.append(''.join(new_parts))
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)

def process_template(file_path):
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '{% load i18n %}' in content:
        print(f"  Already has i18n loaded, skipping: {file_path}")
        return
    
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        if line.strip().startswith('{% load static %}'):
            new_lines.append('{% load i18n %}')
    
    content = '\n'.join(new_lines)
    
    content = wrap_arabic_text(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Completed: {file_path}")

templates = [
    'System/templates/admin/agents.html',
    'System/templates/admin/customers.html',
    'System/templates/admin/tickets.html',
    'System/templates/admin/templates.html',
    'System/templates/admin/reports.html',
    'System/templates/admin/settings.html',
    'System/templates/profile.html',
    'System/templates/login.html',
]

base_dir = r'e:\Hive_Work\Projects\Kh_Pharmacy\final_kh\V1\Anas_S05\Anas_S04\khalifa'

for template in templates:
    file_path = os.path.join(base_dir, template)
    if os.path.exists(file_path):
        process_template(file_path)
    else:
        print(f"File not found: {file_path}")

print("\n✓ All templates processed!")
