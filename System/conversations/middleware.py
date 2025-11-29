"""
Custom Middleware for Khalifa Pharmacy
صيدليات خليفة - Middleware مخصص
"""

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


class PermanentSessionMiddleware(MiddlewareMixin):
    """
    Middleware لجعل الجلسة دائمة ولا تنتهي أبداً
    يقوم بتجديد الجلسة تلقائياً مع كل طلب
    """
    
    def process_request(self, request):
        """
        تجديد الجلسة مع كل طلب
        """
        if request.user.is_authenticated:
            # تجديد الجلسة لمدة 10 سنوات
            request.session.set_expiry(86400 * 365 * 10)
            request.session.modified = True
        
        return None


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware لتتبع آخر نشاط للمستخدم وتحديث حالة Online
    """
    
    def process_request(self, request):
        """
        تحديث حالة المستخدم عند كل طلب
        """
        if request.user.is_authenticated and hasattr(request.user, 'is_online'):
            # التحقق إذا كان المستخدم offline، قم بتحديثه إلى online
            if not request.user.is_online:
                request.user.is_online = True
                request.user.save(update_fields=['is_online'])
                
                # تحديث حالة Agent أيضاً
                if hasattr(request.user, 'role') and request.user.role == 'agent' and hasattr(request.user, 'agent'):
                    if not request.user.agent.is_online:
                        request.user.agent.is_online = True
                        request.user.agent.status = 'available'
                        request.user.agent.save(update_fields=['is_online', 'status'])
        
        return None

