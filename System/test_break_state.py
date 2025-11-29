"""
اختبار حالة الاستراحة للموظف
Test agent break state
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import Agent, User
from django.utils import timezone


def test_agent_break_state():
    """اختبار حالة الاستراحة للموظف"""
    
    print("=" * 60)
    print("🧪 اختبار حالة الاستراحة للموظف")
    print("=" * 60)
    
    # Get all agents
    agents = Agent.objects.all()
    
    if not agents.exists():
        print("❌ لا يوجد موظفين في النظام")
        return
    
    print(f"\n📊 عدد الموظفين: {agents.count()}\n")
    
    for agent in agents:
        print(f"👤 الموظف: {agent.user.username}")
        print(f"   - ID: {agent.id}")
        print(f"   - الحالة (status): {agent.status}")
        print(f"   - في استراحة (is_on_break): {agent.is_on_break}")
        print(f"   - وقت بدء الاستراحة: {agent.break_started_at}")
        print(f"   - إجمالي دقائق الاستراحة اليوم: {agent.total_break_minutes_today}")
        print(f"   - متصل (is_online): {agent.is_online}")
        print(f"   - التذاكر النشطة: {agent.current_active_tickets}")
        
        # Check for inconsistencies
        if agent.is_on_break and agent.status != 'on_break':
            print(f"   ⚠️  تحذير: is_on_break=True لكن status={agent.status}")
        
        if not agent.is_on_break and agent.break_started_at:
            print(f"   ⚠️  تحذير: is_on_break=False لكن break_started_at موجود")
        
        if agent.is_on_break and not agent.break_started_at:
            print(f"   ⚠️  تحذير: is_on_break=True لكن break_started_at غير موجود")
        
        print()
    
    print("=" * 60)
    print("✅ انتهى الاختبار")
    print("=" * 60)


def fix_inconsistent_states():
    """إصلاح الحالات غير المتسقة"""
    
    print("\n" + "=" * 60)
    print("🔧 إصلاح الحالات غير المتسقة")
    print("=" * 60 + "\n")
    
    fixed_count = 0
    
    # Fix agents with is_on_break=False but break_started_at exists
    agents_to_fix = Agent.objects.filter(is_on_break=False).exclude(break_started_at=None)
    if agents_to_fix.exists():
        print(f"🔧 إصلاح {agents_to_fix.count()} موظف لديهم break_started_at بدون is_on_break")
        for agent in agents_to_fix:
            print(f"   - {agent.user.username}: مسح break_started_at")
            agent.break_started_at = None
            agent.save()
            fixed_count += 1
    
    # Fix agents with is_on_break=True but status != 'on_break'
    agents_to_fix = Agent.objects.filter(is_on_break=True).exclude(status='on_break')
    if agents_to_fix.exists():
        print(f"🔧 إصلاح {agents_to_fix.count()} موظف لديهم is_on_break=True لكن status خاطئ")
        for agent in agents_to_fix:
            print(f"   - {agent.user.username}: تحديث status إلى 'on_break'")
            agent.status = 'on_break'
            agent.save()
            fixed_count += 1
    
    # Fix agents with is_on_break=True but no break_started_at
    agents_to_fix = Agent.objects.filter(is_on_break=True, break_started_at=None)
    if agents_to_fix.exists():
        print(f"🔧 إصلاح {agents_to_fix.count()} موظف لديهم is_on_break=True بدون break_started_at")
        for agent in agents_to_fix:
            print(f"   - {agent.user.username}: تعيين break_started_at إلى الآن")
            agent.break_started_at = timezone.now()
            agent.save()
            fixed_count += 1
    
    if fixed_count == 0:
        print("✅ لا توجد حالات غير متسقة")
    else:
        print(f"\n✅ تم إصلاح {fixed_count} حالة")
    
    print("=" * 60)


def reset_all_breaks():
    """إعادة تعيين جميع الاستراحات"""
    
    print("\n" + "=" * 60)
    print("🔄 إعادة تعيين جميع الاستراحات")
    print("=" * 60 + "\n")
    
    agents_on_break = Agent.objects.filter(is_on_break=True)
    
    if not agents_on_break.exists():
        print("✅ لا يوجد موظفين في استراحة")
    else:
        print(f"🔄 إعادة تعيين {agents_on_break.count()} موظف في استراحة")
        for agent in agents_on_break:
            print(f"   - {agent.user.username}")
            agent.is_on_break = False
            agent.break_started_at = None
            agent.status = 'available'
            agent.save()
        print(f"\n✅ تم إعادة تعيين {agents_on_break.count()} موظف")
    
    print("=" * 60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='اختبار وإصلاح حالة الاستراحة للموظفين')
    parser.add_argument('--fix', action='store_true', help='إصلاح الحالات غير المتسقة')
    parser.add_argument('--reset', action='store_true', help='إعادة تعيين جميع الاستراحات')
    
    args = parser.parse_args()
    
    # Always show current state
    test_agent_break_state()
    
    # Fix inconsistencies if requested
    if args.fix:
        fix_inconsistent_states()
        print("\n")
        test_agent_break_state()
    
    # Reset all breaks if requested
    if args.reset:
        reset_all_breaks()
        print("\n")
        test_agent_break_state()

