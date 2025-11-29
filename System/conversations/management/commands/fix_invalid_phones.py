from django.core.management.base import BaseCommand
from django.db import models
from conversations.models import Customer
import re
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Command(BaseCommand):
    help = 'Find and mark customers with invalid phone numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually update the customer names to mark them as invalid',
        )
        parser.add_argument(
            '--update-phone',
            nargs=2,
            metavar=('OLD_PHONE', 'NEW_PHONE'),
            help='Update a specific phone number',
        )

    def handle(self, *args, **options):
        # These are actually WhatsApp LIDs, not problematic phone numbers
        # We should handle them differently
        
        if options['update_phone']:
            old_phone, new_phone = options['update_phone']
            self.update_phone_number(old_phone, new_phone)
            return
        
        # Find customers with WhatsApp LIDs (14-15 digit numbers)
        lid_customers = []
        
        # Check for LID numbers (14-15 digits)
        long_numbers = Customer.objects.filter(
            models.Q(phone_number__regex=r'^\d{14,15}$')
        )
        
        for customer in long_numbers:
            lid_customers.append({
                'customer': customer,
                'type': 'WhatsApp LID',
                'reason': f'WhatsApp Local ID ({len(customer.phone_number)} digits)'
            })
        
        if not lid_customers:
            self.stdout.write(self.style.SUCCESS('No customers with WhatsApp LIDs found!'))
            return
        
        self.stdout.write(self.style.WARNING(f'Found {len(lid_customers)} customers with WhatsApp LIDs:'))
        self.stdout.write('-' * 80)
        
        for item in lid_customers:
            customer = item['customer']
            reason = item['reason']
            
            self.stdout.write(f'ID: {customer.id}')
            self.stdout.write(f'Name: {customer.name}')
            self.stdout.write(f'Phone/LID: {customer.phone_number}')
            self.stdout.write(f'Type: {item["type"]}')
            self.stdout.write(f'Reason: {reason}')
            
            if options['fix']:
                if not customer.name.startswith('[WhatsApp LID]'):
                    old_name = customer.name
                    # Remove any existing prefix
                    clean_name = old_name.replace('[INVALID PHONE] ', '').replace('[WhatsApp LID] ', '')
                    customer.name = f'[WhatsApp LID] {clean_name}'
                    # Update wa_id to use @lid format
                    customer.wa_id = f'{customer.phone_number}@lid'
                    customer.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ Updated: {old_name} -> {customer.name}'))
                    self.stdout.write(self.style.SUCCESS(f'✅ wa_id: {customer.wa_id}'))
                else:
                    self.stdout.write(self.style.WARNING('Already marked as WhatsApp LID'))
            
            self.stdout.write('-' * 80)
        
        if not options['fix']:
            self.stdout.write(self.style.WARNING('\nThese are WhatsApp Local IDs (LIDs).'))
            self.stdout.write('Users with LIDs have not shared their phone numbers.')
            self.stdout.write('We can still send/receive messages using their LID.')
            self.stdout.write('\nTo mark these customers as LID users, run:')
            self.stdout.write('python manage.py fix_invalid_phones --fix')
    
    def update_phone_number(self, old_phone, new_phone):
        """Update a specific phone number"""
        try:
            customer = Customer.objects.get(phone_number=old_phone)
            
            self.stdout.write(f'Found customer: {customer.name}')
            self.stdout.write(f'Current phone: {customer.phone_number}')
            self.stdout.write(f'New phone: {new_phone}')
            
            # Validate new phone
            if not re.match(r'^20\d{10}$', new_phone):
                self.stdout.write(self.style.ERROR('Invalid phone format! Egyptian numbers should be 12 digits starting with 20'))
                return
            
            # Check if new phone already exists
            existing = Customer.objects.filter(phone_number=new_phone).first()
            if existing and existing.id != customer.id:
                self.stdout.write(self.style.ERROR(f'Phone number {new_phone} already exists for customer: {existing.name}'))
                return
            
            # Update phone number
            customer.phone_number = new_phone
            
            # Update wa_id
            customer.wa_id = new_phone + '@c.us'
            
            # Remove [INVALID PHONE] prefix if present
            if customer.name.startswith('[INVALID PHONE]'):
                customer.name = customer.name.replace('[INVALID PHONE] ', '')
            
            customer.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully updated phone number to {new_phone}'))
            
        except Customer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Customer with phone {old_phone} not found'))