import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.core.management import call_command
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver

print("Disconnecting all signals...")

# Temporarily disable all signals
post_save.receivers = []
pre_save.receivers = []
post_delete.receivers = []
pre_delete.receivers = []

print("Loading data without signals...")

try:
    call_command('loaddata', 'backups/data_backup_20251125_123713.json', verbosity=2)
    print("\n[SUCCESS] Data loaded successfully!")
except Exception as e:
    print(f"\n[ERROR] Failed to load data: {e}")
    sys.exit(1)

print("\nReconnecting signals (restart Django to fully restore signal handlers)...")
