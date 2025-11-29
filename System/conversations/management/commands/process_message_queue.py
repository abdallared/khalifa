"""
Django Management Command: process_message_queue

معالجة قائمة انتظار الرسائل

Usage:
    python manage.py process_message_queue                # معالجة عادية
    python manage.py process_message_queue --continuous   # معالجة مستمرة
    python manage.py process_message_queue --stats        # عرض الإحصائيات فقط
    python manage.py process_message_queue --retry-failed # إعادة محاولة الفاشلة
"""

import time
import logging
from django.core.management.base import BaseCommand
from conversations.message_queue import get_message_queue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'معالجة قائمة انتظار رسائل WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='معالجة مستمرة (كل 10 ثواني)',
        )
        
        parser.add_argument(
            '--stats',
            action='store_true',
            help='عرض الإحصائيات فقط',
        )
        
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='إعادة محاولة الرسائل الفاشلة',
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='عدد الرسائل في كل دفعة (افتراضي: 10)',
        )

    def handle(self, *args, **options):
        queue = get_message_queue()
        
        # ============================================
        # عرض الإحصائيات فقط
        # ============================================
        if options['stats']:
            self.stdout.write(self.style.SUCCESS('📊 إحصائيات قائمة الانتظار:'))
            self.stdout.write('')
            
            stats = queue.get_queue_stats()
            
            self.stdout.write(f"  📨 إجمالي الرسائل: {stats['total']}")
            self.stdout.write(f"  ⏳ في الانتظار: {stats['pending']}")
            self.stdout.write(f"  📤 جاري الإرسال: {stats['sending']}")
            self.stdout.write(f"  ✅ تم الإرسال: {stats['sent']}")
            self.stdout.write(f"  📥 تم التوصيل: {stats['delivered']}")
            self.stdout.write(f"  ❌ فشلت: {stats['failed']}")
            self.stdout.write('')
            
            return
        
        # ============================================
        # إعادة محاولة الرسائل الفاشلة
        # ============================================
        if options['retry_failed']:
            self.stdout.write(self.style.WARNING('🔄 إعادة محاولة الرسائل الفاشلة...'))
            
            result = queue.retry_failed(hours=1)
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ تم إعادة تعيين {result['reset_count']} رسالة للمحاولة مرة أخرى"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"❌ فشل: {result.get('error')}"
                ))
            
            return
        
        # ============================================
        # معالجة عادية
        # ============================================
        batch_size = options['batch_size']
        
        if options['continuous']:
            self.stdout.write(self.style.SUCCESS('🔄 معالجة مستمرة (اضغط Ctrl+C للإيقاف)'))
            self.stdout.write('')
            
            try:
                while True:
                    result = queue.process_pending(batch_size=batch_size)
                    
                    if result['processed'] > 0:
                        self.stdout.write(
                            f"✅ معالجة: {result['sent']} نجحت، "
                            f"{result['failed']} فشلت"
                        )
                    else:
                        self.stdout.write('💤 لا توجد رسائل معلقة، انتظار...')
                    
                    time.sleep(10)  # انتظار 10 ثواني
                    
            except KeyboardInterrupt:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('⏹️  تم الإيقاف من قبل المستخدم'))
        
        else:
            # معالجة مرة واحدة
            self.stdout.write(self.style.SUCCESS('📤 معالجة قائمة الانتظار...'))
            
            result = queue.process_pending(batch_size=batch_size)
            
            if result['success']:
                self.stdout.write('')
                self.stdout.write(f"  ✅ نجحت: {result['sent']}")
                self.stdout.write(f"  ❌ فشلت: {result['failed']}")
                self.stdout.write(f"  📊 إجمالي: {result['processed']}")
                self.stdout.write('')
                
                if result['processed'] == 0:
                    self.stdout.write(self.style.WARNING('💤 لا توجد رسائل معلقة'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ تمت المعالجة بنجاح'))
            else:
                self.stdout.write(self.style.ERROR(f"❌ فشل: {result.get('error')}"))