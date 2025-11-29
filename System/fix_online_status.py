"""
سكريبت لتنظيف حالة Online/Offline للمستخدمين
يجب تشغيله مرة واحدة لإصلاح البيانات القديمة
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from conversations.models import User, Agent
from django.contrib.sessions.models import Session
from django.utils import timezone


def fix_online_status():
    """
    تحديث حالة جميع المستخدمين إلى Offline
    (سيتم تحديثهم إلى Online عند تسجيل الدخول)
    """
    print("🔧 بدء تنظيف حالة المستخدمين...")
    
    # 1. تحديث جميع Users إلى Offline
    users_updated = User.objects.filter(is_online=True).update(is_online=False)
    print(f"✅ تم تحديث {users_updated} مستخدم إلى Offline")
    
    # 2. تحديث جميع Agents إلى Offline
    agents_updated = Agent.objects.filter(is_online=True).update(
        is_online=False,
        status='offline'
    )
    print(f"✅ تم تحديث {agents_updated} موظف إلى Offline")
    
    # 3. عرض الجلسات النشطة
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()
    print(f"ℹ️  عدد الجلسات النشطة: {active_sessions}")
    
    print("\n✅ تم الانتهاء من التنظيف!")
    print("💡 الآن، عند تسجيل الدخول، سيتم تحديث الحالة إلى Online تلقائياً")


if __name__ == '__main__':
    fix_online_status()