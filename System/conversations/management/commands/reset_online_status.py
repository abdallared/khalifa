"""
Django Management Command لإعادة تعيين حالة Online/Offline
python manage.py reset_online_status
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from conversations.models import User, Agent


class Command(BaseCommand):
    help = 'إعادة تعيين حالة Online/Offline لجميع المستخدمين'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-offline',
            action='store_true',
            help='تعيين جميع المستخدمين إلى Offline',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔧 بدء تحديث حالة المستخدمين...\n')

        if options['set_offline']:
            # تحديث جميع المستخدمين إلى Offline
            users_updated = User.objects.filter(is_online=True).update(is_online=False)
            agents_updated = Agent.objects.filter(is_online=True).update(
                is_online=False,
                status='offline'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم تحديث {users_updated} مستخدم إلى Offline')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم تحديث {agents_updated} موظف إلى Offline')
            )
        
        # عرض الإحصائيات
        total_users = User.objects.count()
        online_users = User.objects.filter(is_online=True).count()
        offline_users = total_users - online_users
        
        total_agents = Agent.objects.count()
        online_agents = Agent.objects.filter(is_online=True).count()
        available_agents = Agent.objects.filter(status='available').count()
        busy_agents = Agent.objects.filter(status='busy').count()
        offline_agents = Agent.objects.filter(status='offline').count()
        
        self.stdout.write('\n📊 الإحصائيات:')
        self.stdout.write(f'   👥 إجمالي المستخدمين: {total_users}')
        self.stdout.write(f'   🟢 Online: {online_users}')
        self.stdout.write(f'   ⚫ Offline: {offline_users}')
        self.stdout.write(f'\n   👨‍💼 إجمالي الموظفين: {total_agents}')
        self.stdout.write(f'   🟢 Online: {online_agents}')
        self.stdout.write(f'   ✅ Available: {available_agents}')
        self.stdout.write(f'   🔴 Busy: {busy_agents}')
        self.stdout.write(f'   ⚫ Offline: {offline_agents}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ تم الانتهاء!'))