# Issues and Solutions

## 1. Password Reset Not Working
**Status:** Code looks correct
**Possible Issue:** Check browser console for errors when clicking Password button
**Solution:** The API endpoint exists at `/api/agents/{id}/reset_password/`

Test it manually:
- Click Password button
- Enter new password
- Check browser console (F12) for any errors

## 2. Customer Distribution Not Working
**Root Cause:** Agents must be online and available for auto-assignment to work

**Requirements for auto-assignment:**
- `is_online = True`
- `status = 'available'`
- `is_on_break = False`
- `current_active_tickets < max_capacity`

**Solution:** Agents need to login through the system (not Django admin) to be marked as online

## 3. Remove Dummy Agents
**Solution:** Delete test agents from database

Run this in Django shell:
```python
from conversations.models import Agent, User

# List all agents
for agent in Agent.objects.all():
    print(f"ID: {agent.id}, Username: {agent.user.username}, Name: {agent.user.full_name}")

# Delete specific agent by ID
agent_id = 49  # Replace with actual ID
agent = Agent.objects.get(id=agent_id)
user = agent.user
agent.delete()
user.delete()
```

Or delete from admin agents page using the UI.
