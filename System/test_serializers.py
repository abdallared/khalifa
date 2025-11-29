import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from conversations.serializers import (
    UserSerializer, AgentSerializer, AdminSerializer,
    CustomerSerializer, CustomerTagSerializer, CustomerNoteSerializer,
    TicketSerializer, MessageSerializer,
    GlobalTemplateSerializer, AgentTemplateSerializer,
    AgentKPISerializer
)

print("Testing Serializers...")
print()

# Test serializers can be instantiated
serializers_to_test = [
    ('UserSerializer', UserSerializer),
    ('AgentSerializer', AgentSerializer),
    ('AdminSerializer', AdminSerializer),
    ('CustomerSerializer', CustomerSerializer),
    ('CustomerTagSerializer', CustomerTagSerializer),
    ('CustomerNoteSerializer', CustomerNoteSerializer),
    ('TicketSerializer', TicketSerializer),
    ('MessageSerializer', MessageSerializer),
]

errors = []
for name, SerializerClass in serializers_to_test:
    try:
        serializer = SerializerClass()
        print(f'[OK] {name} - instantiated successfully')
    except Exception as e:
        print(f'[ERROR] {name} - {str(e)}')
        errors.append((name, str(e)))

print()
if errors:
    print(f'Total errors: {len(errors)}')
    for name, error in errors:
        print(f'  - {name}: {error}')
else:
    print('All serializers passed instantiation test!')
