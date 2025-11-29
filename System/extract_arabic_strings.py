#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
from collections import OrderedDict

def has_arabic(text):
    """Check if text contains Arabic characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def extract_arabic_from_html(content):
    """Extract Arabic strings from HTML content."""
    arabic_strings = set()
    
    # Extract text between > and <
    pattern1 = r'>([^<>]*[\u0600-\u06FF][^<>]*)<'
    matches = re.findall(pattern1, content)
    for match in matches:
        text = match.strip()
        # Clean up the text
        text = re.sub(r'^\s+|\s+$', '', text)
        text = re.sub(r'\s+', ' ', text)
        if text and has_arabic(text) and '{%' not in text and '{{' not in text:
            arabic_strings.add(text)
    
    # Extract from placeholder, title, alt attributes
    pattern2 = r'(?:placeholder|title|alt)="([^"]*[\u0600-\u06FF][^"]*)"'
    matches = re.findall(pattern2, content)
    for match in matches:
        text = match.strip()
        if text and has_arabic(text):
            arabic_strings.add(text)
    
    # Extract from option values and labels
    pattern3 = r'<option[^>]*>([^<]*[\u0600-\u06FF][^<]*)</option>'
    matches = re.findall(pattern3, content)
    for match in matches:
        text = match.strip()
        if text and has_arabic(text) and '{{' not in text:
            arabic_strings.add(text)
    
    return sorted(list(arabic_strings))

def process_template_file(file_path):
    """Process a single template file."""
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"{'='*60}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        strings = extract_arabic_from_html(content)
        
        if strings:
            print(f"\nFound {len(strings)} Arabic strings:\n")
            for i, s in enumerate(strings, 1):
                print(f"{i}. {s}")
        else:
            print("\nNo Arabic strings found.")
        
        return strings
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def generate_po_entries(strings_dict):
    """Generate .po file entries from collected strings."""
    po_entries = []
    
    for string in sorted(set([s for strings in strings_dict.values() for s in strings])):
        # Create simple English translation (you can improve this)
        # For now, just keep it as is for manual translation
        po_entry = f'\nmsgid "{string}"\nmsgstr "{string}"'
        po_entries.append(po_entry)
    
    return '\n'.join(po_entries)

# List of templates to process
templates = [
    'System/templates/admin/customers.html',
    'System/templates/admin/tickets.html',
    'System/templates/admin/templates.html',
    'System/templates/admin/reports.html',
    'System/templates/admin/settings.html',
]

base_dir = r'e:\Hive_Work\Projects\Kh_Pharmacy\final_kh\V1\Anas_S05\Anas_S04\khalifa'

all_strings = {}

print("ARABIC STRING EXTRACTION TOOL")
print("="*60)

for template in templates:
    file_path = os.path.join(base_dir, template)
    if os.path.exists(file_path):
        strings = process_template_file(file_path)
        all_strings[template] = strings
    else:
        print(f"\nFile not found: {file_path}")

# Generate .po entries
print("\n" + "="*60)
print("GENERATING .PO ENTRIES")
print("="*60)

po_content = generate_po_entries(all_strings)

# Save to file
output_file = os.path.join(base_dir, 'System', 'extracted_strings.po')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(po_content)

print(f"\n✓ Extracted strings saved to: {output_file}")
print(f"\n✓ Total unique strings: {len(set([s for strings in all_strings.values() for s in strings]))}")
