# conversations/permissions.py
"""
Custom Permissions
صلاحيات مخصصة للنظام

الأدوار:
1. Admin - صلاحيات كاملة
2. Agent - صلاحيات محدودة
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    صلاحية للمديرين فقط (Admin, QA, Manager, Supervisor)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'qa', 'manager', 'supervisor']
        )


class IsAgent(permissions.BasePermission):
    """
    صلاحية للموظفين فقط
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and
            request.user.role == 'agent'
        )


class IsAdminOrAgent(permissions.BasePermission):
    """
    صلاحية للمديرين أو الموظفين
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'qa', 'manager', 'supervisor', 'agent']
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    المديرون: صلاحيات كاملة
    الموظفون: قراءة فقط
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # المديرون: صلاحيات كاملة
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'qa', 'manager', 'supervisor']:
            return True
        
        # الموظفون: قراءة فقط
        if hasattr(request.user, 'role') and request.user.role == 'agent':
            return request.method in permissions.SAFE_METHODS
        
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    المالك أو المدير فقط
    """
    def has_object_permission(self, request, view, obj):
        # المديرون: صلاحيات كاملة
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'qa', 'manager', 'supervisor']:
            return True
        
        # الموظف: فقط التذاكر المعينة له
        if hasattr(request.user, 'role') and request.user.role == 'agent':
            if hasattr(obj, 'assigned_agent'):
                return obj.assigned_agent.user == request.user
            elif hasattr(obj, 'agent'):
                return obj.agent.user == request.user
        
        return False


class CanManageAgents(permissions.BasePermission):
    """
    صلاحية إدارة الموظفين
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'qa', 'manager', 'supervisor']:
            # التحقق من صلاحية can_manage_agents
            try:
                admin = request.user.admin
                return admin.can_manage_agents
            except:
                # If no admin object, allow by default for these roles
                return True
        
        return False


class CanManageTemplates(permissions.BasePermission):
    """
    صلاحية إدارة القوالب
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'qa', 'manager', 'supervisor']:
            # التحقق من صلاحية can_manage_templates
            try:
                admin = request.user.admin
                return admin.can_manage_templates
            except:
                # If no admin object, allow by default for these roles
                return True
        
        return False


class CanViewAnalytics(permissions.BasePermission):
    """
    صلاحية عرض التحليلات
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'qa', 'manager', 'supervisor']:
            # التحقق من صلاحية can_view_analytics
            try:
                admin = request.user.admin
                return admin.can_view_analytics
            except:
                # If no admin object, allow by default for these roles
                return True
        
        # الموظفون: يمكنهم رؤية تحليلاتهم الخاصة فقط
        if hasattr(request.user, 'role') and request.user.role == 'agent':
            return True
        
        return False

