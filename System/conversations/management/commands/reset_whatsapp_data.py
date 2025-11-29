"""
Management command to clear all WhatsApp-related data:
- Messages, Tickets, Customers and related logs/notes/tags

Usage:
    python manage.py reset_whatsapp_data

Optional flags:
    --keep-customers   Keep customers and only delete tickets/messages
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from conversations.models import (
    Message,
    MessageDeliveryLog,
    MessageSearchIndex,
    Ticket,
    TicketTransferLog,
    TicketStateLog,
    Customer,
    CustomerNote,
    CustomerTag,
    Agent
)


class Command(BaseCommand):
    help = 'Clear all WhatsApp-related data (messages, tickets, customers)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-customers',
            action='store_true',
            help='Delete tickets/messages only, keep customers'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        keep_customers = options.get('keep_customers', False)

        self.stdout.write(self.style.WARNING('⚠️  Starting data reset...'))

        # Delete message-related tables first
        msg_logs_deleted, _ = MessageDeliveryLog.objects.all().delete()
        search_idx_deleted, _ = MessageSearchIndex.objects.all().delete()
        messages_deleted, _ = Message.objects.all().delete()
        self.stdout.write(f'🗑️  Deleted: {msg_logs_deleted} delivery logs, {search_idx_deleted} search indices, {messages_deleted} messages')

        # Delete tickets and related logs
        transfers_deleted, _ = TicketTransferLog.objects.all().delete()
        states_deleted, _ = TicketStateLog.objects.all().delete()
        tickets_deleted, _ = Ticket.objects.all().delete()
        self.stdout.write(f'🗑️  Deleted: {transfers_deleted} transfers, {states_deleted} state logs, {tickets_deleted} tickets')

        # Delete customers or clean related data
        if not keep_customers:
            notes_deleted, _ = CustomerNote.objects.all().delete()
            tags_deleted, _ = CustomerTag.objects.all().delete()
            customers_deleted, _ = Customer.objects.all().delete()
            self.stdout.write(f'🗑️  Deleted: {notes_deleted} customer notes, {tags_deleted} tags, {customers_deleted} customers')
        else:
            # Reset customer counters
            updated = Customer.objects.all().update(total_tickets_count=0)
            self.stdout.write(f'♻️  Reset total_tickets_count for {updated} customers')

        # Reset agents counters
        agents_updated = Agent.objects.all().update(current_active_tickets=0)
        self.stdout.write(f'♻️  Reset current_active_tickets for {agents_updated} agents')

        self.stdout.write(self.style.SUCCESS('✅ Data reset completed successfully'))

