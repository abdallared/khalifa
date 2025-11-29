#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import User, Agent

print("="*50)
print("FIXING AGENT1")
print("="*50)

try:
    agent1_user = User.objects.get(username='agent1')
    print(f"\nFound user: {agent1_user.username}")
    print(f"  Current status - Active: {agent1_user.is_active}, Online: {agent1_user.is_online}")
    
    agent1_user.is_active = True
    agent1_user.save()
    
    print(f"\n[SUCCESS] Updated user status:")
    print(f"  New status - Active: {agent1_user.is_active}")
    
    agent1_agent = Agent.objects.get(user=agent1_user)
    print(f"\nAgent record status:")
    print(f"  Status: {agent1_agent.status}")
    print(f"  Online: {agent1_agent.is_online}")
    print(f"  Max Capacity: {agent1_agent.max_capacity}")
    
    print("\n" + "="*50)
    print("[SUCCESS] agent1 has been activated!")
    print("You can now login with: username='agent1', password='agent123'")
    print("="*50)
    
except User.DoesNotExist:
    print("[ERROR] agent1 user not found")
except Agent.DoesNotExist:
    print("[ERROR] agent1 Agent record not found")
except Exception as e:
    print(f"[ERROR] {str(e)}")
