#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import User, Agent

# Check users
print("Users:")
for user in User.objects.all():
    print(f"  {user.id}: {user.username} ({user.role})")

print("\nAgents:")
for agent in Agent.objects.all():
    print(f"  {agent.id}: {agent.user.username}")

# Check if agent1 user exists but has no Agent record
try:
    agent1_user = User.objects.get(username='agent1')
    print(f"\n'agent1' user found: {agent1_user}")
    try:
        agent1_agent = Agent.objects.get(user=agent1_user)
        print(f"'agent1' has an Agent record: {agent1_agent}")
    except Agent.DoesNotExist:
        print("'agent1' user exists but has NO Agent record - this is the problem!")
except User.DoesNotExist:
    print("\n'agent1' user does not exist")