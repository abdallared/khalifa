#!/usr/bin/env python
"""
Database Verification Script
نص التحقق من قاعدة البيانات

Verifies database integrity after migration
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import django

# Add project directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.db import connection
from conversations.models import (
    User, Agent, Admin, Customer, Ticket, Message,
    TicketTransferLog, TicketStateLog, MessageDeliveryLog,
    CustomerTag, CustomerNote, AgentKPI, AgentKPIMonthly,
    GlobalTemplate, AgentTemplate, AutoReplyTrigger,
    ResponseTimeTracking, AgentDelayEvent, AgentBreakSession,
    MessageSearchIndex
)


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DatabaseVerifier:
    """Verify database integrity and data"""
    
    def __init__(self):
        self.models = [
            ('Users', User),
            ('Agents', Agent),
            ('Admins', Admin),
            ('Customers', Customer),
            ('Tickets', Ticket),
            ('Messages', Message),
            ('Ticket Transfer Logs', TicketTransferLog),
            ('Ticket State Logs', TicketStateLog),
            ('Message Delivery Logs', MessageDeliveryLog),
            ('Customer Tags', CustomerTag),
            ('Customer Notes', CustomerNote),
            ('Agent KPIs', AgentKPI),
            ('Agent KPI Monthly', AgentKPIMonthly),
            ('Global Templates', GlobalTemplate),
            ('Agent Templates', AgentTemplate),
            ('Auto Reply Triggers', AutoReplyTrigger),
            ('Response Time Tracking', ResponseTimeTracking),
            ('Agent Delay Events', AgentDelayEvent),
            ('Agent Break Sessions', AgentBreakSession),
            ('Message Search Index', MessageSearchIndex),
        ]
    
    def print_section(self, title):
        """Print section header"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    def print_success(self, message):
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def print_error(self, message):
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def print_info(self, message):
        print(f"{Colors.BOLD}{message}{Colors.END}")
    
    def check_database_engine(self):
        """Check current database engine"""
        self.print_section("🔍 Database Configuration")
        
        engine = connection.settings_dict['ENGINE']
        db_name = connection.settings_dict['NAME']
        
        print(f"Engine: {Colors.BOLD}{engine}{Colors.END}")
        print(f"Database: {Colors.BOLD}{db_name}{Colors.END}")
        
        if 'postgresql' in engine:
            self.print_success("PostgreSQL detected")
            print(f"Host: {Colors.BOLD}{connection.settings_dict.get('HOST', 'N/A')}{Colors.END}")
            print(f"Port: {Colors.BOLD}{connection.settings_dict.get('PORT', 'N/A')}{Colors.END}")
            print(f"User: {Colors.BOLD}{connection.settings_dict.get('USER', 'N/A')}{Colors.END}")
        elif 'sqlite' in engine:
            self.print_success("SQLite detected")
        else:
            self.print_error(f"Unknown database: {engine}")
    
    def count_all_records(self):
        """Count records in all models"""
        self.print_section("📊 Record Counts")
        
        total = 0
        for name, model in self.models:
            try:
                count = model.objects.count()
                total += count
                
                if count > 0:
                    print(f"{name:.<50} {Colors.GREEN}{count:>10,}{Colors.END}")
                else:
                    print(f"{name:.<50} {Colors.YELLOW}{count:>10,}{Colors.END}")
                    
            except Exception as e:
                self.print_error(f"{name}: {str(e)}")
        
        print(f"\n{Colors.BOLD}Total Records: {total:,}{Colors.END}")
        return total
    
    def check_foreign_keys(self):
        """Verify foreign key relationships"""
        self.print_section("🔗 Foreign Key Integrity")
        
        checks = [
            ('Agents → Users', Agent, 'user'),
            ('Admins → Users', Admin, 'user'),
            ('Tickets → Customers', Ticket, 'customer'),
            ('Tickets → Agents', Ticket, 'assigned_agent'),
            ('Messages → Tickets', Message, 'ticket'),
            ('Messages → Users', Message, 'sender'),
            ('Customer Tags → Customers', CustomerTag, 'customer'),
            ('Customer Notes → Customers', CustomerNote, 'customer'),
            ('Agent KPIs → Agents', AgentKPI, 'agent'),
        ]
        
        all_ok = True
        for name, model, fk_field in checks:
            try:
                total = model.objects.count()
                if total == 0:
                    print(f"{name:.<50} {Colors.YELLOW}EMPTY{Colors.END}")
                    continue
                
                # Check for NULL foreign keys where not allowed
                filter_kwargs = {f'{fk_field}__isnull': True}
                null_count = model.objects.filter(**filter_kwargs).count()
                
                if null_count == 0:
                    self.print_success(f"{name:.<50} OK")
                else:
                    self.print_error(f"{name:.<50} {null_count} NULL references")
                    all_ok = False
                    
            except Exception as e:
                self.print_error(f"{name}: {str(e)}")
                all_ok = False
        
        return all_ok
    
    def check_unique_constraints(self):
        """Verify unique constraints"""
        self.print_section("🔑 Unique Constraints")
        
        checks = [
            ('User usernames', User, 'username'),
            ('Agent → User', Agent, 'user'),
            ('Admin → User', Admin, 'user'),
            ('Customer phone numbers', Customer, 'phone_number'),
            ('Customer WhatsApp IDs', Customer, 'wa_id'),
        ]
        
        all_ok = True
        for name, model, field in checks:
            try:
                from django.db.models import Count
                
                duplicates = (model.objects
                             .values(field)
                             .annotate(count=Count(field))
                             .filter(count__gt=1))
                
                dup_count = duplicates.count()
                
                if dup_count == 0:
                    self.print_success(f"{name:.<50} OK")
                else:
                    self.print_error(f"{name:.<50} {dup_count} duplicates found")
                    all_ok = False
                    
            except Exception as e:
                self.print_error(f"{name}: {str(e)}")
                all_ok = False
        
        return all_ok
    
    def check_indexes(self):
        """Check database indexes"""
        self.print_section("📇 Database Indexes")
        
        with connection.cursor() as cursor:
            if 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    ORDER BY tablename, indexname
                """)
                
                indexes = cursor.fetchall()
                
                if indexes:
                    current_table = None
                    for schema, table, index in indexes:
                        if table != current_table:
                            print(f"\n{Colors.BOLD}{table}{Colors.END}")
                            current_table = table
                        print(f"  • {index}")
                    
                    self.print_success(f"\nTotal indexes: {len(indexes)}")
                else:
                    self.print_error("No indexes found")
                    
            elif 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT name, tbl_name 
                    FROM sqlite_master 
                    WHERE type='index' 
                    ORDER BY tbl_name, name
                """)
                
                indexes = cursor.fetchall()
                
                if indexes:
                    current_table = None
                    for index, table in indexes:
                        if table != current_table:
                            print(f"\n{Colors.BOLD}{table}{Colors.END}")
                            current_table = table
                        print(f"  • {index}")
                    
                    self.print_success(f"\nTotal indexes: {len(indexes)}")
    
    def check_arabic_text(self):
        """Verify Arabic text encoding"""
        self.print_section("🔤 Arabic Text Encoding")
        
        # Check users with Arabic names
        users_with_arabic = User.objects.filter(full_name__regex=r'[\u0600-\u06FF]')
        print(f"Users with Arabic names: {Colors.BOLD}{users_with_arabic.count()}{Colors.END}")
        
        # Sample some Arabic text
        if users_with_arabic.exists():
            sample = users_with_arabic.first()
            print(f"Sample: {Colors.GREEN}{sample.full_name}{Colors.END}")
            self.print_success("Arabic text encoding OK")
        
        # Check messages with Arabic
        messages_with_arabic = Message.objects.filter(message_text__regex=r'[\u0600-\u06FF]')
        print(f"Messages with Arabic text: {Colors.BOLD}{messages_with_arabic.count()}{Colors.END}")
        
        if messages_with_arabic.exists():
            sample = messages_with_arabic.first()
            preview = sample.message_text[:50] if sample.message_text else ""
            print(f"Sample: {Colors.GREEN}{preview}...{Colors.END}")
    
    def run_all_checks(self):
        """Run all verification checks"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}")
        print(f"DATABASE VERIFICATION REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}{Colors.END}\n")
        
        # Run all checks
        self.check_database_engine()
        total_records = self.count_all_records()
        
        if total_records == 0:
            self.print_error("\n⚠️  Database is empty - no data to verify")
            return
        
        fk_ok = self.check_foreign_keys()
        unique_ok = self.check_unique_constraints()
        self.check_indexes()
        self.check_arabic_text()
        
        # Summary
        self.print_section("📋 Verification Summary")
        
        if fk_ok and unique_ok:
            self.print_success("✓ All integrity checks passed")
            print(f"\n{Colors.GREEN}{Colors.BOLD}Database is healthy and ready!{Colors.END}")
        else:
            self.print_error("✗ Some integrity checks failed")
            print(f"\n{Colors.RED}{Colors.BOLD}Please review errors above{Colors.END}")


def main():
    verifier = DatabaseVerifier()
    verifier.run_all_checks()


if __name__ == '__main__':
    main()
