#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import User, Agent

try:
    # Get the agent1 user
    agent1_user = User.objects.get(username='agent1')
    print(f"Found user: {agent1_user}")
    
    # Check if Agent record already exists
    try:
        existing_agent = Agent.objects.get(user=agent1_user)
        print(f"Agent record already exists: {existing_agent}")
    except Agent.DoesNotExist:
        # Create the Agent record
        agent1_agent = Agent.objects.create(
            user=agent1_user,
            max_capacity=15,  # Default value
            current_active_tickets=0,
            is_online=True,
            status='available'
        )
        print(f"Created Agent record: {agent1_agent}")
        print("Fix completed successfully!")
        
except User.DoesNotExist:
    print("Error: agent1 user does not exist")