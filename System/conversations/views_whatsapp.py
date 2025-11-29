"""
WhatsApp Webhook Views
معالجة الرسائل الواردة من WhatsApp

يستقبل الرسائل من WPPConnect ويعالجها
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Customer, Ticket, Message, User, Agent
from .utils import (
    normalize_phone_number,
    generate_ticket_number,
    get_available_agent,
    assign_ticket_to_agent,
    log_activity,
    send_welcome_message,
    handle_menu_selection,
    should_send_welcome_message
)
from .whatsapp_driver import get_whatsapp_driver
from .message_queue import get_message_queue  # ✅ استيراد Message Queue

logger = logging.getLogger(__name__)


# ============================================
# Webhook Receiver
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_webhook(request):
    """
    استقبال الرسائل الواردة من WPPConnect
    
    POST /api/whatsapp/webhook/
    
    Body:
    {
        "id_ext": "...",
        "phone": "201234567890",
        "message_text": "مرحباً",
        "message_type": "chat",
        "sender_name": "أحمد",
        "timestamp": 1234567890,
        "is_from_me": false,
        "media_url": null,
        "mime_type": null
    }
    """
    try:
        # التحقق من API Key
        api_key = request.headers.get('X-API-Key')
        expected_api_key = 'khalifa-pharmacy-secret-key-2025'  # يجب أن يتطابق مع WPPConnect

        if api_key != expected_api_key:
            logger.warning(f"Invalid API Key: {api_key}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid API Key'
            }, status=401)
        
        # قراءة البيانات
        import json
        data = json.loads(request.body)
        
        logger.info(f"Webhook received from: {data.get('phone')}")
        logger.info(f"DEBUG webhook data: phone={data.get('phone')}, chat_id={data.get('chat_id')}, real_phone={data.get('real_phone')}")
        
        # استخراج البيانات
        id_ext = data.get('id_ext')
        phone = data.get('phone')
        chat_id = data.get('chat_id')  # ✅ الـ chatId الكامل (مع @c.us أو @lid)
        real_phone = data.get('real_phone')  # ✅ الرقم الحقيقي (إذا كان @lid)
        message_text = data.get('message_text', '')
        message_type = data.get('message_type', 'text')
        sender_name = data.get('sender_name', '-')
        timestamp = data.get('timestamp')
        is_from_me = data.get('is_from_me', False)
        media_url = data.get('media_url')
        mime_type = data.get('mime_type')

        # تجاهل الرسائل المرسلة مني
        if is_from_me:
            logger.info("⏭️  Skipping message from me")
            return JsonResponse({
                'success': True,
                'message': 'Message from me - skipped'
            })

        normalized_phone = None
        source_phone = real_phone or phone
        if source_phone:
            try:
                normalized_phone = normalize_phone_number(source_phone)
            except Exception:
                normalized_phone = None

        if chat_id:
            whatsapp_id = chat_id
        else:
            whatsapp_id = phone if '@' in phone else phone + '@c.us'

        # Always store 201xxxxxxxxxx for phone_number if we can normalize
        # For LID, keep phone_number empty and rely on wa_id for messaging
        if normalized_phone:
            customer, created = Customer.objects.get_or_create(
                phone_number=normalized_phone,
                defaults={
                    'name': sender_name if sender_name != '-' else f'عميل {normalized_phone[-4:]}',
                    'wa_id': whatsapp_id
                }
            )
        else:
            try:
                customer = Customer.objects.get(wa_id=whatsapp_id)
                created = False
            except Customer.DoesNotExist:
                # Generate a unique placeholder: 201000 + last 6 digits from wa_id
                lid_digits = ''.join(ch for ch in whatsapp_id.split('@')[0] if ch.isdigit())
                placeholder_suffix = lid_digits[-6:] if len(lid_digits) >= 6 else f"{lid_digits:0>6}"
                placeholder_phone = f"201000{placeholder_suffix}"
                customer, created = Customer.objects.get_or_create(
                    wa_id=whatsapp_id,
                    defaults={
                        'name': sender_name if sender_name != '-' else 'عميل واتساب',
                        'phone_number': placeholder_phone
                    }
                )

        if not created and customer.wa_id != whatsapp_id:
            customer.wa_id = whatsapp_id
            customer.save(update_fields=['wa_id'])

        if created:
            logger.info(f"New customer created: {customer.phone_number}")
            log_activity(
                user=None,
                action='customer_created',
                entity_type='customer',
                entity_id=customer.id
            )
        
        # البحث عن تذكرة مفتوحة للعميل
        open_ticket = Ticket.objects.filter(
            customer=customer,
            status__in=['open', 'pending']
        ).first()
        
        if not open_ticket:
            # إنشاء تذكرة جديدة
            logger.info(f"Creating new ticket for {customer.phone_number}")
            
            # الحصول على موظف متاح
            available_agent = get_available_agent()
            
            # إنشاء التذكرة
            ticket_number = generate_ticket_number()
            
            if not available_agent:
                logger.warning("No available agent found! Creating ticket without agent (Admin can handle it)")
                # إنشاء التذكرة بدون موظف - الأدمن يقدر يرد عليها
                open_ticket = Ticket.objects.create(
                    ticket_number=ticket_number,
                    customer=customer,
                    assigned_agent=None,  # بدون موظف
                    status='pending',  # حالة: معلقة (في انتظار موظف)
                    priority='low',  # أولوية منخفضة حتى يختار العميل
                    category='general'
                )
            else:
                # إنشاء التذكرة مع موظف متاح
                open_ticket = Ticket.objects.create(
                    ticket_number=ticket_number,
                    customer=customer,
                    assigned_agent=available_agent,
                    status='open',
                    priority='low',  # أولوية منخفضة حتى يختار العميل
                    category='general'
                )
            
            # تحديث عداد التذاكر للعميل
            customer.total_tickets_count += 1
            customer.last_contact_date = timezone.now()
            customer.save(update_fields=['total_tickets_count', 'last_contact_date'])
            
            # تعيين التذكرة للموظف (إذا كان متاح)
            if available_agent:
                assign_ticket_to_agent(open_ticket, available_agent)
                logger.info(f"Ticket created: {open_ticket.ticket_number} - Agent: {available_agent.user.username}")
            else:
                logger.info(f"Ticket created: {open_ticket.ticket_number} - No agent available (Admin can handle it)")
        
        # ✅ التحقق من عدم وجود رسالة مكررة
        if id_ext:
            existing_message = Message.objects.filter(whatsapp_message_id=id_ext).first()
            if existing_message:
                logger.warning(f"⚠️ Duplicate message detected: {id_ext} - Skipping")
                return JsonResponse({
                    'success': True,
                    'duplicate': True,
                    'ticket_id': open_ticket.id,
                    'ticket_number': open_ticket.ticket_number,
                    'message_id': existing_message.id,
                    'message': 'Message already exists - skipped'
                })
        else:
            # ✅ إذا لم يكن هناك id_ext، نتحقق من التكرار بناءً على الوقت والمحتوى
            from datetime import timedelta
            
            recent_duplicate = Message.objects.filter(
                ticket=open_ticket,
                sender_type='customer',
                message_text=message_text,
                created_at__gte=timezone.now() - timedelta(seconds=10)
            ).first()
            
            if recent_duplicate:
                logger.warning(f"⚠️ Duplicate message detected by content and time - Skipping")
                return JsonResponse({
                    'success': True,
                    'duplicate': True,
                    'ticket_id': open_ticket.id,
                    'ticket_number': open_ticket.ticket_number,
                    'message_id': recent_duplicate.id,
                    'message': 'Duplicate message by content - skipped'
                })

        # حفظ الرسالة
        message = Message.objects.create(
            ticket=open_ticket,
            sender=None,  # من العميل
            sender_type='customer',  # ✅ إضافة sender_type
            direction='incoming',
            message_text=message_text,
            message_type=message_type,
            whatsapp_message_id=id_ext,
            delivery_status='delivered',
            media_url=media_url,
            mime_type=mime_type
        )

        logger.info(f"✅ Message saved: {message.id}")
        
        # تحديث آخر رسالة في التذكرة
        open_ticket.last_message_at = timezone.now()
        open_ticket.last_customer_message_at = timezone.now()
        open_ticket.messages_count += 1
        open_ticket.save(update_fields=['last_message_at', 'last_customer_message_at', 'messages_count'])
        
        # ✅ معالجة رسالة الترحيب والقائمة المنسدلة
        try:
            # ✅ تحديث التذكرة من قاعدة البيانات للحصول على أحدث حالة
            open_ticket.refresh_from_db()
            logger.info(f"Processing message from {customer.phone_number} - Ticket {open_ticket.ticket_number}: category={open_ticket.category}, classified_at={open_ticket.category_selected_at}")
            
            # ✅ عد الرسائل مرة واحدة لاستخدامها في كل من الترحيب واختيار القائمة
            messages_count = Message.objects.filter(ticket=open_ticket, sender_type='customer').count()
            logger.info(f"Total customer messages in ticket {open_ticket.ticket_number}: {messages_count}")
            
            # ✅ التحقق من وجود رسالة ترحيب سابقة
            welcome_message_exists = Message.objects.filter(
                ticket=open_ticket,
                sender_type='agent',
                message_text__contains='مرحباً بك في صيدليات خليفة'
            ).exists()
            
            # التحقق من إرسال رسالة ترحيب للعملاء الجدد (فقط للرسالة الأولى)
            if messages_count == 1 and not welcome_message_exists and should_send_welcome_message(customer, message_text, open_ticket):
                logger.info(f"Sending welcome message to new customer: {customer.phone_number}")
                welcome_sent = send_welcome_message(customer, open_ticket)
                if welcome_sent:
                    logger.info(f"Welcome message sent successfully to {customer.phone_number}")
                else:
                    logger.warning(f"Failed to send welcome message to {customer.phone_number}")
                # ✅ لا نعالج أي شيء آخر للرسالة الأولى - فقط الترحيب
            elif messages_count >= 2 or (messages_count == 1 and welcome_message_exists):
                # ✅ التحقق من أن التذكرة لم يتم تصنيفها بعد
                if open_ticket.category_selected_at is None:
                    # ✅ معالجة اختيار القائمة من الرسالة الثانية فصاعداً حتى يختار العميل
                    logger.info(f"Processing menu selection for customer {customer.phone_number}, message #{messages_count}: '{message_text}'")
                    
                    # التحقق من اختيار القائمة المنسدلة
                    menu_selection_result = handle_menu_selection(customer, message_text, open_ticket)
                    
                    if menu_selection_result.get('success'):
                        logger.info(f"✅ Menu selection processed successfully for {customer.phone_number}: {menu_selection_result.get('message')}")
                        # تحديث تصنيف التذكرة حسب الاختيار
                        if 'category' in menu_selection_result:
                            # ✅ التصنيف تم بالفعل في handle_menu_selection - لا حاجة لإعادة الحفظ
                            # تحديث التذكرة من قاعدة البيانات للتأكد من الحفظ
                            open_ticket.refresh_from_db()
                            logger.info(f"✅ Ticket {open_ticket.ticket_number} category updated successfully: category={open_ticket.category}, priority={open_ticket.priority}, category_selected_at={open_ticket.category_selected_at}")
                    
                    elif menu_selection_result.get('message') == 'invalid_selection':
                        logger.info(f"Invalid menu selection from {customer.phone_number} (message #{messages_count}): {message_text}")
                        # عدم إرسال رسالة توضيحية تلقائية؛ اترك الأمر للموظف للرد
                else:
                    logger.info(f"✅ Customer {customer.phone_number} ticket {open_ticket.ticket_number} already classified as '{open_ticket.category}' at {open_ticket.category_selected_at} - message goes directly to agent")
                    
        except Exception as welcome_error:
            logger.error(f"Error in welcome/menu processing: {str(welcome_error)}", exc_info=True)
        
        # TODO: إرسال إشعار للموظف (WebSocket/Pusher)
        
        return JsonResponse({
            'success': True,
            'ticket_id': open_ticket.id,
            'ticket_number': open_ticket.ticket_number,
            'message_id': message.id,
            'assigned_agent': open_ticket.assigned_agent.user.username if open_ticket.assigned_agent else None
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# WhatsApp API Views
# ============================================

@api_view(['POST'])
def send_whatsapp_message(request):
    """
    إرسال رسالة WhatsApp (مع Queue & Cache)
    
    POST /api/whatsapp/send/
    
    Body:
    {
        "ticket_id": 123,
        "message": "مرحباً! كيف يمكنني مساعدتك؟"
    }
    
    ✅ التحسينات:
    - حفظ الرسالة في Database أولاً بحالة 'pending'
    - إضافة إلى Queue للإرسال التدريجي
    - Deduplication لمنع التكرار
    - Rate Limiting تلقائي
    """
    try:
        ticket_id = request.data.get('ticket_id')
        message_text = request.data.get('message')
        
        if not ticket_id or not message_text:
            return Response({
                'success': False,
                'error': 'ticket_id and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # الحصول على التذكرة
        try:
            ticket = Ticket.objects.select_related('customer', 'assigned_agent').get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Ticket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # التحقق من الصلاحيات وإنشاء تذكرة جديدة إذا لزم الأمر
        if request.user.role == 'agent':
            agent = Agent.objects.get(user=request.user)
            
            # إذا كانت التذكرة مغلقة أو معينة لموظف آخر، أنشئ تذكرة جديدة
            if ticket.status == 'closed' or ticket.assigned_agent != agent:
                # إنشاء تذكرة جديدة للعميل
                from .utils import generate_ticket_number
                
                new_ticket = Ticket.objects.create(
                    ticket_number=generate_ticket_number(),
                    customer=ticket.customer,
                    assigned_agent=agent,
                    current_agent=agent,
                    status='open',
                    priority='medium',
                    category='follow_up' if ticket.status == 'closed' else ticket.category
                )
                
                # تحديث عدد التذاكر النشطة للموظف
                agent.current_active_tickets = Ticket.objects.filter(
                    assigned_agent=agent,
                    status='open'
                ).count()
                if agent.current_active_tickets >= agent.max_capacity:
                    agent.status = 'busy'
                else:
                    agent.status = 'available'
                agent.save(update_fields=['current_active_tickets', 'status'])
                
                # استخدام التذكرة الجديدة
                ticket = new_ticket
                ticket_id = new_ticket.id
                
                logger.info(f"Created new ticket {new_ticket.ticket_number} for customer {ticket.customer.phone_number}")
        
        # ✅ استخدام Message Queue
        queue = get_message_queue()
        
        # إضافة الرسالة إلى القائمة
        result = queue.enqueue(
            ticket_id=ticket_id,
            user=request.user,
            message_text=message_text,
            message_type='text'
        )
        
        if result.get('success'):
            logger.info(f"[QUEUED] Message queued: {result.get('message_id')}")
            
            # ✅ معالجة الرسائل المعلقة فوراً (في الخلفية)
            # يمكن تعطيل هذا السطر إذا أردت معالجة يدوية/مجدولة
            queue.process_pending(batch_size=5)
            
            return Response({
                'success': True,
                'message_id': result.get('message_id'),
                'status': result.get('status'),
                'message': 'Message queued for delivery',
                'ticket_id': ticket_id,  # ✅ إرجاع ticket_id (قد يكون جديد)
                'ticket_number': ticket.ticket_number  # ✅ رقم التذكرة
            })
        else:
            # فشل في الإضافة للقائمة
            if result.get('duplicate'):
                # رسالة مكررة
                return Response({
                    'success': False,
                    'error': 'Duplicate message detected - already sent recently',
                    'duplicate': True
                }, status=status.HTTP_409_CONFLICT)
            else:
                # خطأ آخر
                logger.error(f"Failed to enqueue message: {result.get('error')}")
                return Response({
                    'success': False,
                    'error': result.get('error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def whatsapp_status(request):
    """
    الحصول على حالة اتصال WhatsApp
    
    GET /api/whatsapp/status/
    """
    try:
        driver = get_whatsapp_driver()
        status_data = driver.get_connection_status()
        
        return Response(status_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def whatsapp_qr_code(request):
    """
    الحصول على QR Code للربط
    
    GET /api/whatsapp/qr-code/
    """
    try:
        driver = get_whatsapp_driver()
        qr_data = driver.get_qr_code()
        
        return Response(qr_data)
        
    except Exception as e:
        logger.error(f"Error getting QR code: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def message_queue_stats(request):
    """
    الحصول على إحصائيات قائمة انتظار الرسائل
    
    GET /api/whatsapp/queue-stats/
    
    Response:
    {
        "success": true,
        "stats": {
            "total": 100,
            "pending": 5,
            "sending": 2,
            "sent": 85,
            "delivered": 80,
            "failed": 3
        }
    }
    """
    try:
        queue = get_message_queue()
        stats = queue.get_queue_stats()
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def process_message_queue_api(request):
    """
    معالجة قائمة الانتظار يدوياً
    
    POST /api/whatsapp/process-queue/
    
    Body (اختياري):
    {
        "batch_size": 10
    }
    """
    try:
        batch_size = request.data.get('batch_size', 10)
        
        queue = get_message_queue()
        result = queue.process_pending(batch_size=batch_size)
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error processing queue: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def retry_failed_messages(request):
    """
    إعادة محاولة الرسائل الفاشلة
    
    POST /api/whatsapp/retry-failed/
    
    Body (اختياري):
    {
        "hours": 1
    }
    """
    try:
        hours = request.data.get('hours', 1)
        
        queue = get_message_queue()
        result = queue.retry_failed(hours=hours)
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error retrying failed messages: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# WhatsApp Cloud API Webhook
# ============================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_cloud_webhook(request):
    """
    استقبال الرسائل الواردة من WhatsApp Business Cloud API
    
    GET: Webhook verification من Meta
    POST: الرسائل الواردة
    
    GET /api/whatsapp/cloud/webhook/?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
    POST /api/whatsapp/cloud/webhook/
    
    Body (POST):
    {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "...",
                        "phone_number_id": "..."
                    },
                    "contacts": [{
                        "profile": {"name": "..."},
                        "wa_id": "..."
                    }],
                    "messages": [{
                        "from": "201234567890",
                        "id": "wamid.xxx",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "مرحباً"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    """
    
    # GET: Webhook Verification
    if request.method == 'GET':
        try:
            from django.conf import settings
            from django.http import HttpResponse
            
            mode = request.GET.get('hub.mode')
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')
            
            verify_token = getattr(settings, 'WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN', '')
            
            if mode == 'subscribe' and token == verify_token:
                logger.info("✅ Webhook verified successfully")
                return HttpResponse(challenge)
            else:
                logger.warning(f"❌ Webhook verification failed: mode={mode}, token_match={token == verify_token}")
                return HttpResponse('Forbidden', status=403)
                
        except Exception as e:
            logger.error(f"Webhook verification error: {str(e)}")
            return HttpResponse('Error', status=500)
    
    # POST: Incoming Messages
    try:
        import json
        data = json.loads(request.body)
        
        logger.info(f"Cloud API webhook received: {json.dumps(data, indent=2)}")
        
        # التحقق من صحة البيانات
        if data.get('object') != 'whatsapp_business_account':
            logger.warning(f"Invalid webhook object: {data.get('object')}")
            return JsonResponse({'success': False, 'error': 'Invalid object'}, status=400)
        
        # معالجة كل entry
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # معالجة الرسائل الواردة
                messages = value.get('messages', [])
                contacts = value.get('contacts', [])
                
                for message in messages:
                    # استخراج بيانات الرسالة
                    from_number = message.get('from')  # رقم المرسل (مع كود الدولة)
                    message_id = message.get('id')
                    timestamp = int(message.get('timestamp', 0))
                    message_type = message.get('type', 'text')
                    
                    # استخراج اسم المرسل
                    sender_name = '-'
                    for contact in contacts:
                        if contact.get('wa_id') == from_number:
                            sender_name = contact.get('profile', {}).get('name', '-')
                            break
                    
                    # استخراج نص الرسالة حسب النوع
                    message_text = ''
                    media_url = None
                    mime_type = None
                    
                    if message_type == 'text':
                        message_text = message.get('text', {}).get('body', '')
                    elif message_type == 'image':
                        media_url = message.get('image', {}).get('id')  # Media ID (سيتم تحويله لـ URL)
                        message_text = message.get('image', {}).get('caption', '[صورة]')
                        mime_type = message.get('image', {}).get('mime_type')
                    elif message_type == 'video':
                        media_url = message.get('video', {}).get('id')
                        message_text = message.get('video', {}).get('caption', '[فيديو]')
                        mime_type = message.get('video', {}).get('mime_type')
                    elif message_type == 'audio':
                        media_url = message.get('audio', {}).get('id')
                        message_text = '[رسالة صوتية]'
                        mime_type = message.get('audio', {}).get('mime_type')
                    elif message_type == 'document':
                        media_url = message.get('document', {}).get('id')
                        message_text = message.get('document', {}).get('filename', '[ملف]')
                        mime_type = message.get('document', {}).get('mime_type')
                    else:
                        message_text = f'[{message_type}]'
                    
                    logger.info(f"Processing Cloud API message from {from_number}: {message_text}")
                    
                    # تطبيع رقم الهاتف
                    normalized_phone = normalize_phone_number(from_number)
                    
                    # البحث عن العميل أو إنشاءه
                    customer, created = Customer.objects.get_or_create(
                        wa_id=from_number,
                        defaults={
                            'phone_number': normalized_phone,
                            'name': sender_name,
                            'source': 'whatsapp'
                        }
                    )
                    
                    if created:
                        logger.info(f"✅ New customer created: {customer.phone_number}")
                    else:
                        # تحديث الاسم إذا تغير
                        if sender_name != '-' and customer.name != sender_name:
                            customer.name = sender_name
                            customer.save()
                    
                    # البحث عن تذكرة نشطة أو إنشاء واحدة جديدة
                    active_ticket = Ticket.objects.filter(
                        customer=customer,
                        status__in=['pending', 'in_progress']
                    ).first()
                    
                    if not active_ticket:
                        # إنشاء تذكرة جديدة
                        active_ticket = Ticket.objects.create(
                            customer=customer,
                            status='pending',
                            ticket_number=generate_ticket_number()
                        )
                        logger.info(f"✅ New ticket created: {active_ticket.ticket_number}")
                        
                        # إرسال رسالة الترحيب إذا لزم الأمر
                        if should_send_welcome_message(customer):
                            send_welcome_message(customer)
                    
                    # حفظ الرسالة
                    Message.objects.create(
                        ticket=active_ticket,
                        sender_type='customer',
                        message_text=message_text,
                        message_type=message_type,
                        id_ext=message_id,
                        media_url=media_url,
                        mime_type=mime_type,
                        delivery_status='received',
                        sent_at=timezone.datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else timezone.now()
                    )
                    
                    logger.info(f"✅ Message saved for ticket {active_ticket.ticket_number}")
                    
                    # معالجة اختيار القائمة إذا كانت التذكرة في انتظار الفئة
                    if active_ticket.status == 'pending' and not active_ticket.category:
                        menu_result = handle_menu_selection(active_ticket, message_text)
                        if menu_result.get('success'):
                            logger.info(f"✅ Menu selection processed for {customer.phone_number}")
        
        return JsonResponse({'success': True, 'message': 'Webhook processed'})
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing Cloud API webhook: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# Elmujib Cloud API Webhook
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def elmujib_webhook(request):
    try:
        from django.conf import settings
        auth_method = getattr(settings, 'ELMUJIB_AUTH_METHOD', 'header')
        expected_token = getattr(settings, 'ELMUJIB_BEARER_TOKEN', '')

        provided_token = ''
        if auth_method == 'header':
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                provided_token = auth_header[len('Bearer '):].strip()
        else:
            provided_token = request.GET.get('token', '')

        if expected_token and provided_token != expected_token:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

        import json
        data = json.loads(request.body)

        sender_info = data.get('sender') or {}
        from_number = (
            data.get('from')
            or data.get('phone')
            or sender_info.get('wa_id')
            or sender_info.get('phone')
            or sender_info.get('phone_number')
        )
        sender_name = data.get('sender_name') or sender_info.get('name') or '-'

        raw_text = data.get('text')
        if isinstance(raw_text, dict):
            raw_text = raw_text.get('body')
        message_text = data.get('message_text') or raw_text or data.get('message') or ''

        message_type = (
            data.get('type')
            or data.get('message_type')
            or ('text' if message_text else 'text')
        )

        message_id = (
            data.get('id')
            or data.get('message_id')
            or data.get('wamid')
            or data.get('id_ext')
        )
        timestamp_val = data.get('timestamp') or data.get('time') or 0

        media_url = None
        mime_type = None
        media_obj = data.get(message_type) or {}
        if message_type in ['image', 'video', 'audio', 'document']:
            media_url = media_obj.get('url') or media_obj.get('id')
            mime_type = media_obj.get('mime_type') or media_obj.get('mimeType')

        is_from_me = data.get('is_from_me', False)
        if is_from_me:
            return JsonResponse({'success': True, 'message': 'Message from me - skipped'})

        normalized_phone = None
        source_phone = from_number
        if source_phone:
            try:
                normalized_phone = normalize_phone_number(source_phone)
            except Exception:
                normalized_phone = None

        whatsapp_id = None
        if from_number:
            whatsapp_id = from_number if '@' in from_number else from_number + '@c.us'

        if normalized_phone:
            customer, created = Customer.objects.get_or_create(
                phone_number=normalized_phone,
                defaults={
                    'name': sender_name if sender_name != '-' else f'عميل {normalized_phone[-4:]}',
                    'wa_id': whatsapp_id
                }
            )
        else:
            try:
                customer = Customer.objects.get(wa_id=whatsapp_id)
                created = False
            except Customer.DoesNotExist:
                lid_digits = ''.join(ch for ch in (whatsapp_id or '').split('@')[0] if ch.isdigit())
                placeholder_suffix = lid_digits[-6:] if len(lid_digits) >= 6 else f"{lid_digits:0>6}"
                placeholder_phone = f"201000{placeholder_suffix}"
                customer, created = Customer.objects.get_or_create(
                    wa_id=whatsapp_id,
                    defaults={
                        'name': sender_name if sender_name != '-' else 'عميل واتساب',
                        'phone_number': placeholder_phone
                    }
                )

        if not created and whatsapp_id and customer.wa_id != whatsapp_id:
            customer.wa_id = whatsapp_id
            customer.save(update_fields=['wa_id'])

        open_ticket = Ticket.objects.filter(
            customer=customer,
            status__in=['open', 'pending']
        ).first()

        if not open_ticket:
            available_agent = get_available_agent()
            ticket_number = generate_ticket_number()
            if not available_agent:
                open_ticket = Ticket.objects.create(
                    ticket_number=ticket_number,
                    customer=customer,
                    assigned_agent=None,
                    status='pending',
                    priority='low',
                    category='general'
                )
            else:
                open_ticket = Ticket.objects.create(
                    ticket_number=ticket_number,
                    customer=customer,
                    assigned_agent=available_agent,
                    status='open',
                    priority='low',
                    category='general'
                )
            customer.total_tickets_count += 1
            customer.last_contact_date = timezone.now()
            customer.save(update_fields=['total_tickets_count', 'last_contact_date'])
            if available_agent:
                assign_ticket_to_agent(open_ticket, available_agent)

        if message_id:
            existing_message = Message.objects.filter(whatsapp_message_id=message_id).first()
            if existing_message:
                return JsonResponse({
                    'success': True,
                    'duplicate': True,
                    'ticket_id': open_ticket.id,
                    'ticket_number': open_ticket.ticket_number,
                    'message_id': existing_message.id,
                    'message': 'Message already exists - skipped'
                })
        else:
            from datetime import timedelta
            recent_duplicate = Message.objects.filter(
                ticket=open_ticket,
                sender_type='customer',
                message_text=message_text,
                created_at__gte=timezone.now() - timedelta(seconds=10)
            ).first()
            if recent_duplicate:
                return JsonResponse({
                    'success': True,
                    'duplicate': True,
                    'ticket_id': open_ticket.id,
                    'ticket_number': open_ticket.ticket_number,
                    'message_id': recent_duplicate.id,
                    'message': 'Duplicate message by content - skipped'
                })

        message = Message.objects.create(
            ticket=open_ticket,
            sender=None,
            sender_type='customer',
            direction='incoming',
            message_text=message_text,
            message_type=message_type or 'text',
            whatsapp_message_id=message_id,
            delivery_status='delivered',
            media_url=media_url,
            mime_type=mime_type
        )

        open_ticket.last_message_at = timezone.now()
        open_ticket.last_customer_message_at = timezone.now()
        open_ticket.messages_count += 1
        open_ticket.save(update_fields=['last_message_at', 'last_customer_message_at', 'messages_count'])

        try:
            open_ticket.refresh_from_db()
            messages_count = Message.objects.filter(ticket=open_ticket, sender_type='customer').count()
            welcome_message_exists = Message.objects.filter(
                ticket=open_ticket,
                sender_type='agent',
                message_text__contains='مرحباً بك في صيدليات خليفة'
            ).exists()
            if messages_count == 1 and not welcome_message_exists and should_send_welcome_message(customer, message_text, open_ticket):
                send_welcome_message(customer, open_ticket)
            elif messages_count >= 2 or (messages_count == 1 and welcome_message_exists):
                if open_ticket.category_selected_at is None:
                    handle_menu_selection(customer, message_text, open_ticket)
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'ticket_id': open_ticket.id,
            'ticket_number': open_ticket.ticket_number,
            'message_id': message.id,
            'assigned_agent': open_ticket.assigned_agent.user.username if open_ticket.assigned_agent else None
        })
    except Exception as e:
        logger.error(f"Elmujib webhook error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
