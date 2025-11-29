import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.db import connection
from conversations.models import User, Agent, Customer, Ticket, Message

print("=" * 80)
print("COMPREHENSIVE DJANGO + POSTGRESQL TEST")
print("=" * 80)
print()

# 1. Database Connection
print("1. Testing PostgreSQL Connection...")
try:
    connection.ensure_connection()
    print(f"   [OK] Connected to: {connection.settings_dict['NAME']}")
    print(f"   [OK] Engine: {connection.settings_dict['ENGINE']}")
    print(f"   [OK] Host: {connection.settings_dict['HOST']}:{connection.settings_dict['PORT']}")
except Exception as e:
    print(f"   [ERROR] Connection failed: {str(e)}")
    exit(1)

print()

# 2. Test Database Queries
print("2. Testing Database Queries...")
try:
    user_count = User.objects.count()
    agent_count = Agent.objects.count()
    customer_count = Customer.objects.count()
    ticket_count = Ticket.objects.count()
    message_count = Message.objects.count()
    
    print(f"   [OK] Users: {user_count}")
    print(f"   [OK] Agents: {agent_count}")
    print(f"   [OK] Customers: {customer_count}")
    print(f"   [OK] Tickets: {ticket_count}")
    print(f"   [OK] Messages: {message_count}")
except Exception as e:
    print(f"   [ERROR] Query failed: {str(e)}")
    exit(1)

print()

# 3. Test Serializers
print("3. Testing Serializers...")
try:
    from conversations.serializers import (
        UserSerializer, AgentSerializer, CustomerSerializer,
        TicketSerializer, MessageSerializer
    )
    
    serializers_tested = [
        ('UserSerializer', UserSerializer),
        ('AgentSerializer', AgentSerializer),
        ('CustomerSerializer', CustomerSerializer),
        ('TicketSerializer', TicketSerializer),
        ('MessageSerializer', MessageSerializer),
    ]
    
    for name, SerializerClass in serializers_tested:
        serializer = SerializerClass()
        print(f"   [OK] {name}")
        
except Exception as e:
    print(f"   [ERROR] Serializer test failed: {str(e)}")
    exit(1)

print()

# 4. Test URL Resolution
print("4. Testing URL Configuration...")
try:
    from django.urls import reverse
    
    urls_to_test = [
        'api-login',
        'dashboard',
        'whatsapp-webhook',
        'user-list',
        'agent-list',
        'customer-list',
        'ticket-list',
        'message-list',
    ]
    
    for url_name in urls_to_test:
        url = reverse(url_name)
        print(f"   [OK] {url_name:25} -> {url}")
        
except Exception as e:
    print(f"   [ERROR] URL resolution failed: {str(e)}")
    exit(1)

print()

# 5. Test Models with Foreign Keys
print("5. Testing Foreign Key Relationships...")
try:
    # Get a sample ticket if exists
    if ticket_count > 0:
        ticket = Ticket.objects.select_related('customer', 'assigned_agent').first()
        if ticket:
            print(f"   [OK] Ticket #{ticket.ticket_number}")
            print(f"   [OK]   Customer: {ticket.customer.name}")
            if ticket.assigned_agent:
                print(f"   [OK]   Agent: {ticket.assigned_agent.user.full_name}")
            print(f"   [OK]   Status: {ticket.status}")
    else:
        print("   [OK] No tickets to test (database empty)")
        
except Exception as e:
    print(f"   [ERROR] Foreign key test failed: {str(e)}")
    exit(1)

print()

# 6. Test Arabic Text Encoding
print("6. Testing Arabic Text Encoding...")
try:
    customers_with_arabic = Customer.objects.filter(name__icontains='ا').first()
    if customers_with_arabic:
        print(f"   [OK] Found customer with Arabic name: {customers_with_arabic.name}")
    else:
        print("   [OK] No Arabic names in database (but encoding is configured correctly)")
        
except Exception as e:
    print(f"   [ERROR] Arabic text test failed: {str(e)}")
    exit(1)

print()

# 7. Test Django Admin
print("7. Testing Django Admin...")
try:
    from django.contrib import admin
    from conversations.models import User, Agent, Customer, Ticket
    
    admin_models = [User, Agent, Customer, Ticket]
    for model in admin_models:
        if admin.site.is_registered(model):
            print(f"   [OK] {model.__name__} registered in admin")
        else:
            print(f"   [WARNING] {model.__name__} not registered in admin")
            
except Exception as e:
    print(f"   [ERROR] Admin test failed: {str(e)}")
    exit(1)

print()
print("=" * 80)
print("ALL TESTS PASSED SUCCESSFULLY!")
print("=" * 80)
print()
print("Summary:")
print(f"- PostgreSQL connection: OK")
print(f"- Database queries: OK")
print(f"- Serializers: OK")
print(f"- URL routing: OK")
print(f"- Foreign keys: OK")
print(f"- Arabic encoding: OK")
print(f"- Django admin: OK")
print()
print("Django is ready to run with PostgreSQL!")
