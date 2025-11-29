# conversations/urls.py
"""
URL Configuration for Conversations App
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *
from .views_messages import *
from .views_analytics import *
from .views_whatsapp import (
    whatsapp_webhook,
    whatsapp_cloud_webhook,
    elmujib_webhook,
    send_whatsapp_message,
    whatsapp_status,
    whatsapp_qr_code,
    message_queue_stats,
    process_message_queue_api,
    retry_failed_messages
)
from .views import conversations_list_api, transfer_ticket_api, available_agents_api, debug_agents_api, all_conversations_api
from .views_messages import customer_messages_api
from .views_backup import (
    create_backup,
    restore_backup,
    list_backups,
    delete_backup
)


# إنشاء Router
router = DefaultRouter()

# User Management
router.register(r'users', UserViewSet, basename='user')
router.register(r'agents', AgentViewSet, basename='agent')

# Customer Management
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'customer-tags', CustomerTagViewSet, basename='customer-tag')
router.register(r'customer-notes', CustomerNoteViewSet, basename='customer-note')

# Ticket Management
router.register(r'tickets', TicketViewSet, basename='ticket')

# Message Management
router.register(r'messages', MessageViewSet, basename='message')

# Template Management
router.register(r'global-templates', GlobalTemplateViewSet, basename='global-template')
router.register(r'agent-templates', AgentTemplateViewSet, basename='agent-template')
router.register(r'auto-reply-triggers', AutoReplyTriggerViewSet, basename='auto-reply-trigger')

# KPI & Analytics
router.register(r'agent-kpi', AgentKPIViewSet, basename='agent-kpi')
router.register(r'agent-kpi-monthly', AgentKPIMonthlyViewSet, basename='agent-kpi-monthly')
router.register(r'customer-satisfaction', CustomerSatisfactionViewSet, basename='customer-satisfaction')

# System Settings
router.register(r'settings', SystemSettingsViewSet, basename='settings')


# URL Patterns
urlpatterns = [
    # Authentication
    path('auth/login/', LoginView.as_view(), name='api-login'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('auth/profile/', ProfileView.as_view(), name='api-profile'),
    
    # Dashboard & Reports
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/', ReportsView.as_view(), name='reports'),

    # WhatsApp Integration
    path('whatsapp/webhook/', whatsapp_webhook, name='whatsapp-webhook'),
    path('whatsapp/cloud/webhook/', whatsapp_cloud_webhook, name='whatsapp-cloud-webhook'),
    path('whatsapp/elmujib/webhook/', elmujib_webhook, name='whatsapp-elmujib-webhook'),
    path('whatsapp/send/', send_whatsapp_message, name='whatsapp-send'),
    path('whatsapp/status/', whatsapp_status, name='whatsapp-status'),
    path('whatsapp/qr-code/', whatsapp_qr_code, name='whatsapp-qr-code'),
    
    # ✅ Message Queue Management
    path('whatsapp/queue-stats/', message_queue_stats, name='message-queue-stats'),
    path('whatsapp/process-queue/', process_message_queue_api, name='process-message-queue'),
    path('whatsapp/retry-failed/', retry_failed_messages, name='retry-failed-messages'),
    
    # ✅ Conversations Real-time Updates
    path('conversations/', conversations_list_api, name='conversations-list'),
    path('all-conversations/', all_conversations_api, name='all-conversations'),
    
    # ✅ Ticket Transfer
    path('transfer-ticket/', transfer_ticket_api, name='transfer-ticket'),
    path('available-agents/', available_agents_api, name='available-agents'),
    path('debug-agents/', debug_agents_api, name='debug-agents'),
    
    # ✅ Customer Messages
    path('customers/<int:customer_id>/messages/', customer_messages_api, name='customer-messages'),

    # ✅ Backup & Restore
    path('backup/create/', create_backup, name='backup-create'),
    path('backup/restore/', restore_backup, name='backup-restore'),
    path('backup/list/', list_backups, name='backup-list'),
    path('backup/delete/', delete_backup, name='backup-delete'),

    # Router URLs
    path('', include(router.urls)),
]
