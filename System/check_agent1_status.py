#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import User, Agent

print("="*50)
print("CHECKING AGENT1 STATUS")
print("="*50)

try:
    agent1_user = User.objects.get(username='agent1')
    print(f"\n[OK] User 'agent1' exists:")
    print(f"  - ID: {agent1_user.id}")
    print(f"  - Username: {agent1_user.username}")
    print(f"  - Role: {agent1_user.role}")
    print(f"  - Active: {agent1_user.is_active}")
    print(f"  - Online: {agent1_user.is_online}")
    
    try:
        agent1_agent = Agent.objects.get(user=agent1_user)
        print(f"\n[OK] Agent record exists:")
        print(f"  - ID: {agent1_agent.id}")
        print(f"  - Online: {agent1_agent.is_online}")
        print(f"  - Status: {agent1_agent.status}")
        print(f"  - Max Capacity: {agent1_agent.max_capacity}")
        print(f"  - Current Tickets: {agent1_agent.current_active_tickets}")
        print(f"  - Is On Break: {agent1_agent.is_on_break}")
    except Agent.DoesNotExist:
        print(f"\n[ERROR] Agent record DOES NOT EXIST - This is the problem!")
        
except User.DoesNotExist:
    print(f"\n[ERROR] User 'agent1' does not exist")

print("\n" + "="*50)
print("OTHER AGENTS FOR COMPARISON")
print("="*50)
for agent in Agent.objects.all()[:3]:
    print(f"\n- {agent.user.username}:")
    print(f"  Status: {agent.status}, Online: {agent.is_online}")
