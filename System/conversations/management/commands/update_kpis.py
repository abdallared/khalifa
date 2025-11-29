"""
Management Command لتحديث KPIs لجميع الموظفين
يمكن تشغيله يدوياً أو جدولته مع Cron Job

الاستخدام:
    python manage.py update_kpis                    # تحديث KPIs لليوم الحالي
    python manage.py update_kpis --days 7           # تحديث KPIs لآخر 7 أيام
    python manage.py update_kpis --date 2025-11-01  # تحديث KPIs ليوم محدد
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from conversations.models import Agent
from conversations.utils import calculate_agent_kpi


class Command(BaseCommand):
    help = 'تحديث KPIs لجميع الموظفين'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='عدد الأيام السابقة لحساب KPI لها (افتراضياً 1 يوم)'
        )
        
        parser.add_argument(
            '--date',
            type=str,
            help='تاريخ محدد بصيغة YYYY-MM-DD'
        )
        
        parser.add_argument(
            '--agent',
            type=int,
            help='ID موظف محدد (اختياري)'
        )

    def handle(self, *args, **options):
        days = options['days']
        date_str = options.get('date')
        agent_id = options.get('agent')
        
        # تحديد التواريخ
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                dates = [target_date]
            except ValueError:
                self.stdout.write(self.style.ERROR('❌ صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD'))
                return
        else:
            today = timezone.now().date()
            dates = [today - timedelta(days=i) for i in range(days)]
        
        # تحديد الموظفين
        if agent_id:
            try:
                agents = [Agent.objects.get(id=agent_id)]
            except Agent.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ الموظف #{agent_id} غير موجود'))
                return
        else:
            agents = Agent.objects.all()
        
        # بدء التحديث
        self.stdout.write(self.style.SUCCESS(f'🔄 بدء تحديث KPIs لـ {agents.count()} موظف...'))
        self.stdout.write(self.style.SUCCESS(f'📅 الفترة: {len(dates)} يوم'))
        self.stdout.write('-' * 70)
        
        total_updated = 0
        total_errors = 0
        
        for agent in agents:
            self.stdout.write(f'\n👤 {agent.user.full_name}')
            
            for date in dates:
                try:
                    kpi_data = calculate_agent_kpi(agent, date)
                    
                    if kpi_data['total_tickets'] > 0:
                        self.stdout.write(
                            f'  ✅ {date}: '
                            f'{kpi_data["total_tickets"]} تذاكر، '
                            f'{kpi_data["closed_tickets"]} مغلقة، '
                            f'KPI: {kpi_data["overall_kpi_score"]:.1f}%'
                        )
                        total_updated += 1
                    else:
                        self.stdout.write(f'  ⚪ {date}: لا توجد تذاكر')
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ {date}: خطأ - {str(e)}'))
                    total_errors += 1
        
        # النتيجة النهائية
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'✅ تم الانتهاء من تحديث KPIs'))
        self.stdout.write(self.style.SUCCESS(f'📊 تم تحديث: {total_updated} KPI'))
        
        if total_errors > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  أخطاء: {total_errors}'))

