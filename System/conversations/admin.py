# conversations/admin.py
"""
Django Admin Configuration
تسجيل جميع الـ Models في Django Admin Panel
"""

from django.contrib import admin
from .models import (
    User, Agent, Admin,
    Customer, CustomerTag, CustomerNote,
    Ticket, TicketTransferLog, TicketStateLog,
    Message, MessageDeliveryLog, MessageSearchIndex,
    GlobalTemplate, AgentTemplate, AutoReplyTrigger,
    ResponseTimeTracking, AgentDelayEvent,
    AgentKPI, AgentKPIMonthly, CustomerSatisfaction,
    ActivityLog, LoginAttempt
)


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'role', 'is_active', 'is_online', 'last_login']
    list_filter = ['role', 'is_active', 'is_online']
    search_fields = ['username', 'email', 'full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'current_active_tickets', 'max_capacity', 'is_online']
    list_filter = ['status', 'is_online']
    search_fields = ['user__username', 'user__full_name']


@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'can_manage_agents', 'can_manage_templates', 'can_view_analytics']
    search_fields = ['user__username', 'user__full_name']


# ============================================================================
# CUSTOMER MANAGEMENT
# ============================================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'customer_type', 'is_blocked', 'total_tickets_count']
    list_filter = ['customer_type', 'is_blocked']
    search_fields = ['name', 'phone_number', 'email']


@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = ['customer', 'tag', 'created_at']
    search_fields = ['customer__name', 'tag']


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'created_by', 'is_important', 'created_at']
    list_filter = ['is_important']
    search_fields = ['customer__name', 'note_text']


# ============================================================================
# TICKET MANAGEMENT
# ============================================================================

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'customer', 'assigned_agent', 'status', 'priority', 'get_category_arabic', 'created_at']
    list_filter = ['status', 'priority', 'category', 'is_delayed']
    search_fields = ['ticket_number', 'customer__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TicketTransferLog)
class TicketTransferLogAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'from_agent', 'to_agent', 'transferred_by', 'created_at']
    search_fields = ['ticket__ticket_number']


@admin.register(TicketStateLog)
class TicketStateLogAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'old_state', 'new_state', 'changed_by', 'created_at']
    search_fields = ['ticket__ticket_number']


# ============================================================================
# MESSAGES
# ============================================================================

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'sender_type', 'message_type', 'is_read', 'created_at']
    list_filter = ['sender_type', 'message_type', 'is_read']
    search_fields = ['message_text', 'ticket__ticket_number']


@admin.register(MessageDeliveryLog)
class MessageDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ['message', 'delivery_status', 'created_at']
    list_filter = ['delivery_status']


@admin.register(MessageSearchIndex)
class MessageSearchIndexAdmin(admin.ModelAdmin):
    list_display = ['message', 'customer', 'created_at']
    search_fields = ['search_text']


# ============================================================================
# TEMPLATES
# ============================================================================

@admin.register(GlobalTemplate)
class GlobalTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'content']


@admin.register(AgentTemplate)
class AgentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent', 'category', 'is_active', 'usage_count']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'content']


@admin.register(AutoReplyTrigger)
class AutoReplyTriggerAdmin(admin.ModelAdmin):
    list_display = ['trigger_keyword', 'trigger_type', 'is_active', 'created_by']
    list_filter = ['is_active', 'trigger_type']
    search_fields = ['trigger_keyword']


# ============================================================================
# DELAY TRACKING
# ============================================================================

@admin.register(ResponseTimeTracking)
class ResponseTimeTrackingAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'agent', 'response_time_seconds', 'is_delayed', 'created_at']
    list_filter = ['is_delayed']


@admin.register(AgentDelayEvent)
class AgentDelayEventAdmin(admin.ModelAdmin):
    list_display = ['agent', 'ticket', 'delay_start_time', 'delay_duration_seconds']
    search_fields = ['agent__user__full_name']


# ============================================================================
# KPI & PERFORMANCE
# ============================================================================

@admin.register(AgentKPI)
class AgentKPIAdmin(admin.ModelAdmin):
    list_display = ['agent', 'kpi_date', 'total_tickets', 'closed_tickets', 'overall_kpi_score']
    list_filter = ['kpi_date']
    search_fields = ['agent__user__full_name']


@admin.register(AgentKPIMonthly)
class AgentKPIMonthlyAdmin(admin.ModelAdmin):
    list_display = ['agent', 'month', 'total_tickets', 'closed_tickets', 'overall_kpi_score', 'rank']
    list_filter = ['month']
    search_fields = ['agent__user__full_name']


@admin.register(CustomerSatisfaction)
class CustomerSatisfactionAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'agent', 'rating', 'created_at']
    list_filter = ['rating']


# ============================================================================
# ACTIVITY LOG
# ============================================================================

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity_type', 'entity_id', 'created_at']
    list_filter = ['action', 'entity_type']
    search_fields = ['user__username', 'action']
    readonly_fields = ['created_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'ip_address', 'success', 'attempt_time']
    list_filter = ['success']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['attempt_time']

