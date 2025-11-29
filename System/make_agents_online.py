#!/usr/bin/env python
"""
جعل الموظفين متاحين للعمل (Online)
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Agent

def make_agents_online():
    """جعل الموظفين متاحين للعمل"""
    
    print("=== جعل الموظفين متاحين للعمل ===")
    
    # الحصول على أول 3 موظفين
    agents = Agent.objects.all()[:3]
    
    for agent in agents:
        # تحديث الحالة إلى available و online
        agent.is_online = True
        agent.status = 'available'
        agent.save()

        print(f"✅ تم تفعيل الموظف: {agent.user.username}")

    print(f"\n📊 الموظفين المتاحين الآن:")

    # فحص الحالة الجديدة
    online_agents = Agent.objects.filter(is_online=True, status='available')
    for agent in online_agents:
        print(f"👤 {agent.user.username}: {agent.status} - سعة {agent.current_active_tickets}/{agent.max_capacity}")
    
    print(f"\n🎉 تم تفعيل {online_agents.count()} موظفين!")
    print("📱 الآن يمكن استقبال رسائل WhatsApp بنجاح!")

if __name__ == "__main__":
    make_agents_online()
