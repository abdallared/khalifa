"""
Notifications API Views
التنبيهات الفورية للموظفين
"""

import logging
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Notification, Agent
from .authentication import agent_or_admin_required

logger = logging.getLogger(__name__)


@api_view(['GET'])
@agent_or_admin_required
def get_unread_notifications(request):
    """
    جلب التنبيهات غير المقروءة للموظف
    
    GET /api/notifications/unread/
    
    Response:
    {
        "success": true,
        "count": 2,
        "notifications": [
            {
                "id": 1,
                "type": "new_ticket",
                "title": "تذكرة جديدة",
                "message": "تم تعيين تذكرة جديدة لك من أحمد",
                "ticket_id": 123,
                "customer_id": 45,
                "customer_name": "أحمد",
                "customer_phone": "201234567890",
                "created_at": "2025-01-15T10:30:00Z"
            }
        ]
    }
    """
    try:
        # الحصول على الموظف
        agent = Agent.objects.get(user=request.user)
        
        # جلب التنبيهات غير المقروءة
        notifications = Notification.objects.filter(
            agent=agent,
            is_read=False
        ).select_related('ticket', 'customer').order_by('-created_at')[:10]
        
        # تحويل إلى JSON
        notifications_data = []
        for notif in notifications:
            notifications_data.append({
                'id': notif.id,
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'ticket_id': notif.ticket.id if notif.ticket else None,
                'ticket_number': notif.ticket.ticket_number if notif.ticket else None,
                'customer_id': notif.customer.id if notif.customer else None,
                'customer_name': notif.customer.name if notif.customer else None,
                'customer_phone': notif.customer.phone_number if notif.customer else None,
                'created_at': notif.created_at.isoformat(),
                'data': notif.data
            })
        
        return Response({
            'success': True,
            'count': len(notifications_data),
            'notifications': notifications_data
        })
        
    except Agent.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Agent not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@agent_or_admin_required
def mark_notification_as_read(request, notification_id):
    """
    تعليم تنبيه كمقروء
    
    POST /api/notifications/<id>/read/
    """
    try:
        # الحصول على الموظف
        agent = Agent.objects.get(user=request.user)
        
        # جلب التنبيه
        notification = Notification.objects.get(id=notification_id, agent=agent)
        
        # تعليم كمقروء
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@agent_or_admin_required
def mark_all_as_read(request):
    """
    تعليم جميع التنبيهات كمقروءة
    
    POST /api/notifications/read-all/
    """
    try:
        # الحصول على الموظف
        agent = Agent.objects.get(user=request.user)
        
        # تعليم جميع التنبيهات كمقروءة
        updated_count = Notification.objects.filter(
            agent=agent,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': f'{updated_count} notifications marked as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking all as read: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@agent_or_admin_required
def get_notification_count(request):
    """
    عدد التنبيهات غير المقروءة (لـ badge)
    
    GET /api/notifications/count/
    
    Response:
    {
        "success": true,
        "count": 5
    }
    """
    try:
        # الحصول على الموظف
        agent = Agent.objects.get(user=request.user)
        
        # عد التنبيهات غير المقروءة
        count = Notification.objects.filter(
            agent=agent,
            is_read=False
        ).count()
        
        return Response({
            'success': True,
            'count': count
        })
        
    except Agent.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Agent not found',
            'count': 0
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting notification count: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'count': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)