# conversations/authentication.py
"""
Custom Authentication Backend
لأن User model لا يرث من AbstractBaseUser
"""

from django.contrib.auth.backends import BaseBackend
from .models import User


class CustomUserBackend(BaseBackend):
    """
    Custom Authentication Backend للـ User model
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        التحقق من بيانات المستخدم
        """
        if username is None or password is None:
            return None
        
        try:
            user = User.objects.get(username=username)
            
            # التحقق من كلمة المرور
            if user.check_password(password):
                return user
            
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        الحصول على المستخدم من ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

