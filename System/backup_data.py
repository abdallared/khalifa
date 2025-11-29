import os
import sys
import django
from io import StringIO
from datetime import datetime

# Set UTF-8 for console output
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.core.management import call_command

# Create backup filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backups/data_backup_{timestamp}.json"

print(f"Starting backup to {backup_file}...")

try:
    # Open file with UTF-8 encoding
    with open(backup_file, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.Permission',
            '--exclude', 'sessions.Session',
            stdout=f
        )
    print(f"[SUCCESS] Backup completed successfully: {backup_file}")
    
except Exception as e:
    print(f"[ERROR] Error during backup: {e}")
    sys.exit(1)
