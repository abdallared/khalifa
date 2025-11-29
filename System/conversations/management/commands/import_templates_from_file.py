import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from conversations.models import GlobalTemplate, Admin


class Command(BaseCommand):
    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        path = os.path.join(base_dir.parent, 'templates.txt')
        if not os.path.exists(path):
            self.stderr.write('templates.txt not found')
            return
        admin = Admin.objects.select_related('user').first()
        if not admin:
            self.stderr.write('No Admin user')
            return
        content = open(path, 'r', encoding='utf-8', errors='ignore').read()
        def categorize(name, body):
            s = f"{name} {body}"
            has = lambda k: k in s
            if any(has(k) for k in ['مساء الخير','صباح الخير','وعليكم السلام','شكرا','تحية','السلام']):
                return 'رد التحية'
            if any(has(k) for k in ['دفع','فودافون','كاش','انستاباي','الاجمالي','فاتوره']):
                return 'الدفع'
            if any(has(k) for k in ['عرض','غير متاح عرض']):
                return 'عروض'
            if any(has(k) for k in ['استشارة','استشارات','فتح استشارة','استكمال استشارة','تحويل استشارات']):
                return 'استشارات'
            if any(has(k) for k in ['خدمة','التمريض','مندوب','التوصيل','جاري التحضير','تم تنفيذ الاوردر','نواقص','مثيل','بديل','ضغط الاوردرات','انتظار','التواصل مع المندوب','ارسال الاصناف','صور منتجات','تحويل ماسنجر','مرتجع','عطل فني','عناوين الفروع']):
                return 'خدمات'
            return 'أخرى'
        chunks = content.split(' Edit | Details | Delete')
        keywords = [
            'للاسف', 'استأذن', 'استاذن', 'بعتذر', 'تم', 'بنعتذر', 'في انتظار', 'أقدر',
            'عميلنا العزيز', 'هل', 'سيتم', 'اضغط', 'يرجي', 'فروعنا', 'اعطاء',
            'اوردر حضرتك', 'جاري', 'لحظات', 'مساء الخير', 'صباح الخير', 'وعليكم السلام', 'شكرا'
        ]
        created = 0
        for raw in chunks:
            s = raw.strip()
            if not s:
                continue
            s = s.replace('Title Message Type', '').strip()
            m = re.search(r'\s+(Low|High)\s*$', s)
            if m:
                s = s[:m.start()].strip()
            idx = None
            for kw in keywords:
                p = s.find(kw)
                if p != -1:
                    idx = p
                    break
            if idx is None:
                parts = s.split()
                if len(parts) >= 2:
                    title = ' '.join(parts[:2])
                    body = ' '.join(parts[2:])
                else:
                    title = s
                    body = ''
            else:
                title = s[:idx].strip()
                body = s[idx:].strip()
            cat = categorize(title, body)
            obj, _ = GlobalTemplate.objects.get_or_create(
                name=title,
                defaults={
                    'content': body,
                    'category': cat,
                    'is_active': True,
                    'created_by': admin,
                    'updated_by': admin,
                }
            )
            if _ is False:
                obj.content = body
                obj.category = cat
                obj.is_active = True
                obj.updated_by = admin
                obj.save()
            created += 1
        self.stdout.write(f'Imported {created} templates')
