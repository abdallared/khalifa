# conversations/apps.py
from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conversations'
    verbose_name = 'نظام إدارة المحادثات'

    def ready(self):
        """
        تحميل Signals عند بدء التطبيق
        """
        import conversations.signals

