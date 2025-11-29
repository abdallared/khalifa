#!/usr/bin/env python
"""
Database Migration Script - SQLite to PostgreSQL
نص الترحيل من SQLite إلى PostgreSQL

Usage:
    python migrate_to_postgresql.py --backup    # Backup data only
    python migrate_to_postgresql.py --migrate   # Full migration
    python migrate_to_postgresql.py --verify    # Verify migration
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import django

# Add project directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from conversations.models import (
    User, Agent, Admin, Customer, Ticket, Message,
    CustomerTag, CustomerNote, AgentKPI, GlobalTemplate
)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DatabaseMigrator:
    """Handle database migration from SQLite to PostgreSQL"""
    
    def __init__(self):
        self.backup_dir = BASE_DIR / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def print_step(self, message, color=Colors.BLUE):
        """Print formatted step message"""
        print(f"\n{color}{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{color}{Colors.BOLD}{message}{Colors.END}")
        print(f"{color}{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    def print_success(self, message):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    
    def check_current_database(self):
        """Check current database engine"""
        self.print_step("🔍 Checking Current Database Configuration")
        
        engine = connection.settings_dict['ENGINE']
        db_name = connection.settings_dict['NAME']
        
        print(f"Database Engine: {Colors.BOLD}{engine}{Colors.END}")
        print(f"Database Name: {Colors.BOLD}{db_name}{Colors.END}")
        
        if 'sqlite' in engine:
            self.print_success("SQLite database detected - ready for migration")
            return True
        elif 'postgresql' in engine:
            self.print_warning("PostgreSQL database detected - already migrated?")
            return False
        else:
            self.print_error(f"Unsupported database: {engine}")
            return False
    
    def backup_data(self):
        """Backup SQLite database data"""
        self.print_step("💾 Backing Up SQLite Database")
        
        backup_file = self.backup_dir / f'data_backup_{self.timestamp}.json'
        
        try:
            # Export data excluding contenttypes and permissions
            with open(backup_file, 'w', encoding='utf-8') as f:
                call_command(
                    'dumpdata',
                    natural_foreign=True,
                    natural_primary=True,
                    exclude=['contenttypes', 'auth.permission'],
                    indent=2,
                    stdout=f
                )
            
            self.print_success(f"Data backed up to: {backup_file}")
            
            # Get file size
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            print(f"Backup size: {Colors.BOLD}{size_mb:.2f} MB{Colors.END}")
            
            return backup_file
            
        except Exception as e:
            self.print_error(f"Backup failed: {str(e)}")
            return None
    
    def count_records(self):
        """Count records in all models"""
        self.print_step("📊 Counting Records")
        
        models = [
            ('Users', User),
            ('Agents', Agent),
            ('Admins', Admin),
            ('Customers', Customer),
            ('Tickets', Ticket),
            ('Messages', Message),
            ('Customer Tags', CustomerTag),
            ('Customer Notes', CustomerNote),
            ('Agent KPIs', AgentKPI),
            ('Global Templates', GlobalTemplate),
        ]
        
        counts = {}
        for name, model in models:
            try:
                count = model.objects.count()
                counts[name] = count
                print(f"{name}: {Colors.BOLD}{count:,}{Colors.END}")
            except Exception as e:
                self.print_warning(f"Could not count {name}: {str(e)}")
                counts[name] = 0
        
        return counts
    
    def check_postgresql_connection(self):
        """Check PostgreSQL connection"""
        self.print_step("🔌 Checking PostgreSQL Connection")
        
        try:
            from django.db import connections
            db_conn = connections['default']
            db_conn.cursor()
            
            self.print_success("PostgreSQL connection successful")
            
            # Print connection details
            print(f"Host: {Colors.BOLD}{db_conn.settings_dict['HOST']}{Colors.END}")
            print(f"Port: {Colors.BOLD}{db_conn.settings_dict['PORT']}{Colors.END}")
            print(f"Database: {Colors.BOLD}{db_conn.settings_dict['NAME']}{Colors.END}")
            print(f"User: {Colors.BOLD}{db_conn.settings_dict['USER']}{Colors.END}")
            
            return True
            
        except Exception as e:
            self.print_error(f"PostgreSQL connection failed: {str(e)}")
            return False
    
    def run_migrations(self):
        """Run Django migrations on PostgreSQL"""
        self.print_step("🔄 Running Migrations on PostgreSQL")
        
        try:
            call_command('migrate', '--noinput')
            self.print_success("Migrations completed successfully")
            return True
        except Exception as e:
            self.print_error(f"Migration failed: {str(e)}")
            return False
    
    def load_data(self, backup_file):
        """Load data into PostgreSQL"""
        self.print_step("📥 Loading Data into PostgreSQL")
        
        if not backup_file or not backup_file.exists():
            self.print_error("Backup file not found")
            return False
        
        try:
            call_command('loaddata', str(backup_file))
            self.print_success("Data loaded successfully")
            return True
        except Exception as e:
            self.print_error(f"Data load failed: {str(e)}")
            return False
    
    def verify_migration(self, old_counts):
        """Verify migration success"""
        self.print_step("✅ Verifying Migration")
        
        new_counts = self.count_records()
        
        success = True
        for name, old_count in old_counts.items():
            new_count = new_counts.get(name, 0)
            
            if old_count == new_count:
                self.print_success(f"{name}: {old_count} → {new_count}")
            else:
                self.print_error(f"{name}: {old_count} → {new_count} (MISMATCH!)")
                success = False
        
        return success
    
    def full_migration(self):
        """Execute full migration process"""
        self.print_step("🚀 Starting Database Migration: SQLite → PostgreSQL")
        
        # Step 1: Check current database
        if not self.check_current_database():
            self.print_error("Current database check failed")
            return False
        
        # Step 2: Count records
        old_counts = self.count_records()
        
        # Step 3: Backup data
        backup_file = self.backup_data()
        if not backup_file:
            self.print_error("Backup failed - aborting migration")
            return False
        
        # Step 4: Switch to PostgreSQL (manual step)
        self.print_step("⚙️ Manual Step Required")
        print(f"{Colors.YELLOW}Please update your .env file:{Colors.END}")
        print(f"{Colors.BOLD}DB_ENGINE=postgresql{Colors.END}")
        print(f"{Colors.BOLD}DB_NAME=khalifa_pharmacy_db{Colors.END}")
        print(f"{Colors.BOLD}DB_USER=postgres{Colors.END}")
        print(f"{Colors.BOLD}DB_PASSWORD=your_password{Colors.END}")
        print(f"\n{Colors.YELLOW}Then restart the script with --continue flag{Colors.END}")
        
        return True


def main():
    """Main execution"""
    migrator = DatabaseMigrator()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate_to_postgresql.py --backup    # Backup data only")
        print("  python migrate_to_postgresql.py --migrate   # Full migration")
        print("  python migrate_to_postgresql.py --verify    # Verify migration")
        return
    
    command = sys.argv[1]
    
    if command == '--backup':
        migrator.check_current_database()
        old_counts = migrator.count_records()
        backup_file = migrator.backup_data()
        
        if backup_file:
            print(f"\n{Colors.GREEN}Backup completed successfully!{Colors.END}")
            print(f"Backup file: {Colors.BOLD}{backup_file}{Colors.END}")
            
    elif command == '--migrate':
        migrator.full_migration()
        
    elif command == '--verify':
        migrator.check_postgresql_connection()
        migrator.count_records()
        
    else:
        print(f"{Colors.RED}Unknown command: {command}{Colors.END}")


if __name__ == '__main__':
    main()
