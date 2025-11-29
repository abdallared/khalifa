# conversations/views_messages.py
"""
Message & Template Management Views
"""

import os
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import default_storage

from .models import *
from .serializers import *
from .permissions import *
from .utils import *


# ============================================================================
# MESSAGE MANAGEMENT VIEWS
# ============================================================================

class MessageViewSet(viewsets.ModelViewSet):
    """
    إدارة الرسائل
    """
    queryset = Message.objects.select_related('ticket__customer').all()
    serializer_class = MessageSerializer
    permission_classes = [IsAdminOrAgent]
    pagination_class = None  # ✅ إلغاء pagination - عرض كل الرسائل
    
    def create(self, request, *args, **kwargs):
        """
        Override create to handle image uploads properly
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Log the incoming request data
            logger.info(f"Creating message - Files: {list(request.FILES.keys())}, Data: {request.POST.keys()}")
            
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            logger.warning(f"Validation error creating message: {str(e)}")
            return Response({
                'error': str(e),
                'detail': 'خطأ في التحقق من البيانات'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}", exc_info=True)
            
            return Response({
                'error': str(e),
                'detail': 'فشل في إنشاء الرسالة'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # التصفية حسب التذكرة
        ticket_id = self.request.query_params.get('ticket', None)
        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)
        
        # التصفية حسب نوع المرسل
        sender_type = self.request.query_params.get('sender_type', None)
        if sender_type:
            queryset = queryset.filter(sender_type=sender_type)
        
        # البحث في النص
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(message_text__icontains=search)
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        """
        إرسال رسالة جديدة
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Handle image upload
            image_file = self.request.FILES.get('image')
            
            # Prepare base kwargs
            kwargs = {
                'sender': self.request.user,
                'sender_type': 'agent',
                'direction': 'outgoing'
            }
            
            # Initialize message_type
            message_type = 'text'
            
            if image_file:
                # Validate file size (max 5MB)
                if image_file.size > 5 * 1024 * 1024:
                    raise ValueError('حجم الصورة يجب أن يكون أقل من 5 ميجابايت')
                
                # Create unique filename
                ext = os.path.splitext(image_file.name)[1]
                filename = f"messages/{uuid.uuid4()}{ext}"

                # Save file
                try:
                    path = default_storage.save(filename, image_file)
                    media_url = f"{settings.MEDIA_URL}{path}"
                    
                    kwargs['media_url'] = media_url
                    kwargs['mime_type'] = image_file.content_type
                    message_type = 'image'
                    
                    logger.info(f"Image saved: {path} - URL: {media_url}")
                except Exception as e:
                    logger.error(f"Error saving image: {str(e)}", exc_info=True)
                    raise
            
            kwargs['message_type'] = message_type
            
            message = serializer.save(**kwargs)
            logger.info(f"Message created: {message.id} - Type: {message.message_type}")
            
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}", exc_info=True)
            raise

        # تحديث آخر رسالة في التذكرة
        ticket = message.ticket
        ticket.last_message_at = timezone.now()
        ticket.messages_count += 1

        if message.sender_type == 'customer':
            ticket.last_customer_message_at = timezone.now()

            # فحص التأخير
            update_ticket_delay_status(ticket)

        elif message.sender_type == 'agent':
            ticket.last_agent_message_at = timezone.now()

            # حساب وقت الاستجابة (إذا كانت أول رسالة من الموظف)
            if not ticket.first_response_at:
                ticket.first_response_at = timezone.now()

                if ticket.created_at:
                    response_time = timezone.now() - ticket.created_at
                    ticket.response_time_seconds = int(response_time.total_seconds())

            # إلغاء حالة التأخير
            if ticket.is_delayed:
                update_ticket_delay_status(ticket)

        ticket.save()

        # إنشاء فهرس البحث
        if message.message_text:
            MessageSearchIndex.objects.create(
                message=message,
                customer=ticket.customer,
                search_text=message.message_text
            )
        
        # تسجيل النشاط
        try:
            user = self.request.user
            if user and user.is_authenticated:
                log_activity(
                    user=user,
                    action='send_message',
                    entity_type='message',
                    entity_id=message.id,
                    request=self.request
                )
        except:
            pass

        # إرسال الرسالة إلى WhatsApp (للرسائل الصادرة من الموظف)
        if message.sender_type == 'agent' and message.direction == 'outgoing':
            try:
                from .whatsapp_driver import get_whatsapp_driver
                driver = get_whatsapp_driver()
                
                # تحضير رقم الهاتف
                customer = ticket.customer
                phone_to_use = customer.wa_id if customer.wa_id else customer.phone_number
                
                logger.info(f"Sending to WhatsApp - Phone: {phone_to_use}, Type: {message.message_type}")
                
                if message.message_type == 'text' and message.message_text:
                    # إرسال رسالة نصية
                    result = driver.send_text_message(
                        phone=phone_to_use,
                        message=message.message_text
                    )
                
                elif message.message_type == 'image' and message.media_url:
                    # إرسال صورة
                    # تحويل media_url إلى URL كامل إذا لزم الأمر
                    media_url = message.media_url
                    if not media_url.startswith('http'):
                        # إذا كانت مسارات نسبية، تحويلها إلى URL مطلقة
                        domain = getattr(settings, 'WHATSAPP_MEDIA_DOMAIN', 'http://localhost:8000')
                        # تنظيف الـ domain والـ path وبناء URL صحيح
                        domain = domain.rstrip('/')
                        path = media_url.lstrip('/')
                        media_url = f"{domain}/{path}"
                    
                    logger.info(f"Sending image to WhatsApp - URL: {media_url}")
                    logger.info(f"Message text (caption): {message.message_text}")
                    
                    result = driver.send_media_message(
                        phone=phone_to_use,
                        media_url=media_url,
                        media_type='image',
                        caption=message.message_text if message.message_text else None
                    )
                
                else:
                    result = None
                
                # حفظ معرّف رسالة WhatsApp إذا نجح الإرسال
                if result and result.get('success'):
                    message.whatsapp_message_id = result.get('message_id')
                    message.delivery_status = 'sent'
                    message.save(update_fields=['whatsapp_message_id', 'delivery_status'])
                    logger.info(f"Message sent to WhatsApp successfully: {result.get('message_id')}")
                else:
                    logger.warning(f"Failed to send to WhatsApp: {result}")
                    
            except Exception as e:
                logger.error(f"Error sending message to WhatsApp: {str(e)}", exc_info=True)
                # لا نرفع الخطأ هنا حتى لا نفشل في حفظ الرسالة
        
        # تحديث KPI للموظف تلقائياً (عند إرسال رسالة من الموظف)
        if message.sender_type == 'agent' and ticket.assigned_agent:
            try:
                from .utils import calculate_agent_kpi
                calculate_agent_kpi(ticket.assigned_agent)
            except:
                pass
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        تعليم الرسالة كمقروءة
        POST /api/messages/{id}/mark_read/
        """
        message = self.get_object()
        
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        return Response({
            'message': 'تم تعليم الرسالة كمقروءة'
        })
    
    @action(detail=False, methods=['post'])
    def mark_customer_messages_read(self, request):
        """
        تعليم جميع رسائل العميل كمقروءة
        POST /api/messages/mark_customer_messages_read/
        """
        customer_id = request.data.get('customer_id')
        
        if not customer_id:
            return Response({
                'error': 'customer_id مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # التحقق من أن المستخدم هو موظف
        if request.user.role != 'agent':
            return Response({
                'error': 'هذه العملية متاحة للموظفين فقط'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # الحصول على الموظف
        try:
            agent = Agent.objects.get(user=request.user)
        except Agent.DoesNotExist:
            return Response({
                'error': 'بيانات الموظف غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # تعليم جميع الرسائل غير المقروءة من هذا العميل كمقروءة
        unread_messages = Message.objects.filter(
            ticket__customer_id=customer_id,
            ticket__assigned_agent=agent,
            ticket__status='open',
            sender_type='customer',
            is_read=False
        )
        
        updated_count = unread_messages.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'تم تعليم {updated_count} رسالة كمقروءة',
            'updated_count': updated_count
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_messages_api(request, customer_id):
    """
    الحصول على جميع رسائل العميل من جميع تذاكره
    GET /api/customers/{customer_id}/messages/
    
    ✅ يستخدم لعرض المحادثات الكاملة للعميل
    """
    try:
        # التحقق من العميل
        customer = Customer.objects.get(id=customer_id)
        
        # الحصول على جميع تذاكر العميل
        user = request.user
        tickets_query = Ticket.objects.filter(customer=customer)
        
        # للموظفين: فقط التذاكر المعينة لهم أو التذاكر المغلقة
        if user.role == 'agent':
            try:
                agent = user.agent
                tickets_query = tickets_query.filter(
                    Q(assigned_agent=agent) | Q(current_agent=agent) | Q(status='closed')
                )
            except Agent.DoesNotExist:
                tickets_query = tickets_query.none()
            except Exception as e:
                tickets_query = tickets_query.none()
        
        tickets = tickets_query.order_by('-created_at')
        
        # تجميع جميع الرسائل من جميع التذاكر
        all_messages = []
        for ticket in tickets:
            try:
                messages = Message.objects.filter(ticket=ticket).order_by('created_at')
                for message in messages:
                    # Get sender name from sender relationship if it's an agent
                    sender_name = ''
                    if message.sender_type == 'agent' and message.sender:
                        sender_name = message.sender.full_name or message.sender.username
                    elif message.sender_type == 'customer' and hasattr(message, 'sender_name') and message.sender_name:
                        sender_name = message.sender_name
                    
                    all_messages.append({
                        'id': message.id,
                        'message_text': message.message_text,
                        'message_type': message.message_type,
                        'media_url': message.media_url,
                        'mime_type': message.mime_type,
                        'sender_type': message.sender_type,
                        'sender_name': sender_name,
                        'created_at': message.created_at.isoformat(),
                        'is_read': message.is_read,
                        'ticket_id': ticket.id,
                        'ticket_number': ticket.ticket_number,
                        'ticket_status': ticket.status
                    })
            except Exception as e:
                continue
        
        # ترتيب الرسائل حسب الوقت
        all_messages.sort(key=lambda x: x['created_at'])
        
        return Response({
            'messages': all_messages,
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone_number': customer.phone_number
            },
            'tickets_count': tickets.count()
        })
        
    except Customer.DoesNotExist:
        return Response({
            'error': 'العميل غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'حدث خطأ: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# TEMPLATE MANAGEMENT VIEWS
# ============================================================================

class GlobalTemplateViewSet(viewsets.ModelViewSet):
    """
    إدارة القوالب العامة
    ✅ الموظفون يمكنهم القراءة فقط، الأدمن يمكنه التعديل
    """
    queryset = GlobalTemplate.objects.select_related('created_by__user').all()
    serializer_class = GlobalTemplateSerializer
    permission_classes = [IsAdminOrAgent]  # ✅ السماح للموظفين بالقراءة
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # التصفية حسب الفئة
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        # التصفية حسب الحالة
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('name')

    def get_permissions(self):
        """
        ✅ الموظفون: قراءة فقط (list, retrieve)
        ✅ الأدمن: كل الصلاحيات
        """
        if self.action in ['list', 'retrieve']:
            # القراءة متاحة للجميع (admin + agent)
            return [IsAdminOrAgent()]
        else:
            # التعديل/الإضافة/الحذف للأدمن فقط
            return [IsAdmin()]

    def perform_create(self, serializer):
        user = self.request.user

        if user and user.is_authenticated and user.role == 'admin':
            try:
                admin = user.admin  # الـ related_name هو 'admin' وليس 'admin_profile'
                serializer.save(created_by=admin, updated_by=admin)
            except Exception as e:
                # إذا فشل الحصول على admin، احفظ بدون created_by
                serializer.save()
        else:
            serializer.save()


class AgentTemplateViewSet(viewsets.ModelViewSet):
    """
    إدارة قوالب الموظفين
    """
    queryset = AgentTemplate.objects.select_related('agent__user').all()
    serializer_class = AgentTemplateSerializer
    permission_classes = [IsAdminOrAgent]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        # الموظفون: فقط قوالبهم الخاصة
        if user.role == 'agent':
            try:
                agent = user.agent
                queryset = queryset.filter(agent=agent)
            except:
                return queryset.none()

        # المديرون: جميع القوالب
        
        # التصفية حسب الفئة
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('-usage_count', 'name')
    
    def perform_create(self, serializer):
        user = self.request.user

        if user and user.is_authenticated and user.role == 'agent':
            try:
                agent = user.agent
                serializer.save(agent=agent)
            except:
                serializer.save()
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """
        استخدام قالب (زيادة عداد الاستخدام)
        POST /api/agent-templates/{id}/use/
        """
        template = self.get_object()
        template.usage_count += 1
        template.save()
        
        return Response({
            'message': 'تم استخدام القالب',
            'usage_count': template.usage_count
        })


class AutoReplyTriggerViewSet(viewsets.ModelViewSet):
    """
    إدارة محفزات الرد التلقائي
    """
    queryset = AutoReplyTrigger.objects.select_related('template', 'created_by__user').all()
    serializer_class = AutoReplyTriggerSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # التصفية حسب النوع
        trigger_type = self.request.query_params.get('type', None)
        if trigger_type:
            queryset = queryset.filter(trigger_type=trigger_type)
        
        # التصفية حسب الحالة
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('trigger_keyword')
    
    def perform_create(self, serializer):
        user = self.request.user

        if user and user.is_authenticated and user.role == 'admin':
            try:
                admin = user.admin  # الـ related_name هو 'admin' وليس 'admin_profile'
                serializer.save(created_by=admin)
            except:
                serializer.save()
        else:
            serializer.save()


# ============================================================================
# CUSTOMER NOTES & TAGS VIEWS
# ============================================================================

class CustomerNoteViewSet(viewsets.ModelViewSet):
    """
    إدارة ملاحظات العملاء
    """
    queryset = CustomerNote.objects.select_related('customer', 'created_by').all()
    serializer_class = CustomerNoteSerializer
    permission_classes = [IsAdminOrAgent]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # التصفية حسب العميل
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # التصفية حسب الأهمية
        is_important = self.request.query_params.get('important', None)
        if is_important is not None:
            queryset = queryset.filter(is_important=is_important.lower() == 'true')
        
        return queryset.order_by('-is_important', '-created_at')
    
    def perform_create(self, serializer):
        user = self.request.user

        if user and user.is_authenticated:
            serializer.save(created_by=user)
        else:
            serializer.save()


class CustomerTagViewSet(viewsets.ModelViewSet):
    """
    إدارة تصنيفات العملاء
    """
    queryset = CustomerTag.objects.select_related('customer').all()
    serializer_class = CustomerTagSerializer
    permission_classes = [IsAdminOrAgent]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # التصفية حسب العميل
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        return queryset.order_by('tag')
