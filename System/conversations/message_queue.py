"""
Message Queue Manager
إدارة قائمة انتظار الرسائل مع Cache و Deduplication

Features:
✅ Cache الرسائل قبل الإرسال
✅ Deduplication لمنع التكرار
✅ Rate Limiting لتجنب الحظر
✅ Retry Mechanism مع Exponential Backoff
✅ Batch Processing للإرسال الجماعي
"""

import hashlib
import logging
import time
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.db import transaction, OperationalError
from datetime import timedelta
import sqlite3

from .models import Message, Ticket, User
from .whatsapp_driver import get_whatsapp_driver

logger = logging.getLogger(__name__)


def retry_db_operation(func, max_retries=3, delay=0.1):
    """
    إعادة المحاولة للعمليات التي قد تفشل بسبب database lock
    """
    for attempt in range(max_retries):
        try:
            return func()
        except (OperationalError, sqlite3.OperationalError) as e:
            if 'database is locked' in str(e).lower() and attempt < max_retries - 1:
                logger.warning(f"Database locked, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2  # exponential backoff
            else:
                raise e
    return None


class MessageQueue:
    """
    Message Queue Manager
    
    Usage:
        queue = MessageQueue()
        message = queue.enqueue(ticket_id=1, user=user, text="مرحباً")
        queue.process_pending()  # معالجة كل الرسائل المعلقة
    """
    
    # إعدادات الـ Queue
    MAX_RETRY_COUNT = 3  # أقصى عدد للمحاولات
    RETRY_DELAY_SECONDS = [5, 30, 120]  # تأخير بين المحاولات (5s, 30s, 2min)
    BATCH_SIZE = 10  # عدد الرسائل لكل دفعة
    RATE_LIMIT_PER_MINUTE = 20  # أقصى عدد رسائل في الدقيقة
    
    def __init__(self):
        self.driver = get_whatsapp_driver()
        self._sent_messages_count = 0
        self._last_reset_time = time.time()
    
    def generate_message_hash(self, ticket_id: int, message_text: str, sender_id: int) -> str:
        """
        توليد Hash فريد للرسالة لمنع التكرار
        
        Args:
            ticket_id: رقم التذكرة
            message_text: نص الرسالة
            sender_id: رقم المرسل
        
        Returns:
            SHA256 hash
        """
        unique_string = f"{ticket_id}:{message_text}:{sender_id}:{timezone.now().strftime('%Y%m%d%H%M')}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
    
    def check_duplicate(self, message_hash: str, minutes: int = 5) -> bool:
        """
        التحقق من وجود رسالة مكررة في آخر X دقائق
        
        Args:
            message_hash: الـ hash المطلوب
            minutes: عدد الدقائق للبحث (افتراضي 5)
        
        Returns:
            True إذا وجدت رسالة مكررة
        """
        cutoff_time = timezone.now() - timedelta(minutes=minutes)
        
        duplicate = Message.objects.filter(
            message_hash=message_hash,
            created_at__gte=cutoff_time
        ).exists()
        
        if duplicate:
            logger.warning(f"⚠️  Duplicate message detected: {message_hash[:16]}...")
        
        return duplicate
    
    @transaction.atomic
    def enqueue(
        self,
        ticket_id: int,
        user: User,
        message_text: str,
        message_type: str = 'text',
        media_url: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        إضافة رسالة إلى قائمة الانتظار
        
        Args:
            ticket_id: رقم التذكرة
            user: المستخدم المرسل
            message_text: نص الرسالة
            message_type: نوع الرسالة (text, image, etc)
            media_url: رابط الميديا (اختياري)
            mime_type: نوع الملف (اختياري)
        
        Returns:
            Dict مع success و message_id
        """
        try:
            # الحصول على التذكرة
            try:
                ticket = Ticket.objects.select_related('customer').get(id=ticket_id)
            except Ticket.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Ticket not found'
                }
            
            # ✅ التحقق من صحة رقم الهاتف أو LID
            customer_phone = ticket.customer.phone_number
            
            # Check if this is a WhatsApp LID (14-15 digits)
            is_lid = False
            if len(customer_phone) >= 14 and len(customer_phone) <= 15:
                # This is likely a WhatsApp LID
                is_lid = True
                logger.info(f"🔒 Detected WhatsApp LID: {customer_phone}")
                
                # Make sure wa_id is set correctly for LID
                if not ticket.customer.wa_id or '@lid' not in ticket.customer.wa_id:
                    ticket.customer.wa_id = f"{customer_phone}@lid"
                    ticket.customer.save(update_fields=['wa_id'])
                    logger.info(f"✅ Updated wa_id to: {ticket.customer.wa_id}")
            
            # Only validate if it's not a LID
            if not is_lid and not customer_phone.startswith('20'):
                # Check for invalid phone numbers (non-Egyptian, non-LID)
                if len(customer_phone) < 10 or len(customer_phone) > 13:
                    logger.error(f"❌ Invalid phone number format: {customer_phone}")
                    return {
                        'success': False,
                        'error': f'Invalid phone number format: {customer_phone}',
                        'invalid_phone': True,
                        'phone_number': customer_phone,
                        'reason': 'Invalid phone number format'
                    }
            
            # توليد Hash للرسالة
            message_hash = self.generate_message_hash(ticket_id, message_text, user.id)
            
            # التحقق من التكرار
            if self.check_duplicate(message_hash, minutes=5):
                logger.warning(f"Duplicate message rejected for ticket {ticket_id}")
                return {
                    'success': False,
                    'error': 'Duplicate message detected',
                    'duplicate': True
                }
            
            # حفظ الرسالة بحالة 'pending' مع retry للـ database lock
            def create_message():
                return Message.objects.create(
                    ticket=ticket,
                    sender=user,
                    sender_type='agent' if user.role == 'agent' else 'admin',
                    direction='outgoing',
                    message_text=message_text,
                    message_type=message_type,
                    media_url=media_url,
                    mime_type=mime_type,
                    delivery_status='pending',
                    message_hash=message_hash,
                    retry_count=0
                )

            message = retry_db_operation(create_message)

            logger.info(f"[QUEUED] Message queued: {message.id} for ticket {ticket_id}")

            # تحديث آخر رسالة في التذكرة مع retry
            def update_ticket():
                ticket.last_message_at = timezone.now()
                # تحديث last_agent_message_at لإلغاء حالة التأخير
                if user.role in ['agent', 'admin']:
                    ticket.last_agent_message_at = timezone.now()
                    ticket.save(update_fields=['last_message_at', 'last_agent_message_at'])
                    
                    # إلغاء حالة التأخير فوراً
                    from .utils import update_ticket_delay_status
                    update_ticket_delay_status(ticket)
                else:
                    ticket.save(update_fields=['last_message_at'])
                return True

            retry_db_operation(update_ticket)
            
            return {
                'success': True,
                'message_id': message.id,
                'status': 'queued',
                'message': 'Message queued for delivery'
            }
            
        except Exception as e:
            logger.error(f"Error enqueueing message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_rate_limit(self) -> bool:
        """
        التحقق من Rate Limit
        
        Returns:
            True إذا يمكن الإرسال
        """
        current_time = time.time()
        
        # إعادة تعيين العداد كل دقيقة
        if current_time - self._last_reset_time >= 60:
            self._sent_messages_count = 0
            self._last_reset_time = current_time
        
        # التحقق من الحد
        if self._sent_messages_count >= self.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"⚠️  Rate limit reached: {self._sent_messages_count}/min")
            return False
        
        return True
    
    @transaction.atomic
    def process_message(self, message: Message) -> bool:
        """
        معالجة رسالة واحدة (إرسالها عبر WhatsApp)
        
        Args:
            message: الرسالة المطلوب إرسالها
        
        Returns:
            True إذا نجح الإرسال
        """
        try:
            # التحقق من Rate Limit
            if not self._check_rate_limit():
                logger.info("Rate limit reached, pausing...")
                time.sleep(3)  # انتظار 3 ثواني
                return False
            
            # تحديث الحالة إلى 'sending'
            message.delivery_status = 'sending'
            message.last_retry_at = timezone.now()
            message.save(update_fields=['delivery_status', 'last_retry_at'])
            
            # تحديد نوع الإرسال
            # ✅ استخدام wa_id بدلاً من phone_number (يحتوي على @lid أو @c.us الصحيح)
            customer_wa_id = message.ticket.customer.wa_id

            if message.message_type == 'text' or not message.media_url:
                # إرسال نص
                result = self.driver.send_text_message(
                    phone=customer_wa_id,
                    message=message.message_text
                )
            else:
                # إرسال ميديا
                result = self.driver.send_media_message(
                    phone=customer_wa_id,
                    media_url=message.media_url,
                    media_type=message.message_type,
                    caption=message.message_text
                )
            
            if result.get('success'):
                # نجح الإرسال ✅
                message.delivery_status = 'sent'
                message.whatsapp_message_id = result.get('message_id')
                message.sent_at = timezone.now()
                message.error_message = None
                message.save(update_fields=[
                    'delivery_status',
                    'whatsapp_message_id',
                    'sent_at',
                    'error_message'
                ])
                
                self._sent_messages_count += 1
                logger.info(f"[SUCCESS] Message {message.id} sent successfully")
                return True
            else:
                # فشل الإرسال ❌
                error_msg = result.get('error', 'Unknown error')

                # ✅ إذا كان الخطأ بسبب @lid، نضع رسالة واضحة
                if '@lid' in customer_wa_id or 'lid' in error_msg.lower():
                    error_msg = f"⚠️ حساب واتساب للأعمال: لا يمكن إرسال رسائل آلية لهذا العميل. يُرجى الرد يدوياً من تطبيق WhatsApp."
                    message.delivery_status = 'failed'  # فشل نهائي
                    message.retry_count = self.MAX_RETRY_COUNT  # لا نعيد المحاولة
                else:
                    message.retry_count += 1
                    message.delivery_status = 'failed' if message.retry_count >= self.MAX_RETRY_COUNT else 'pending'

                message.error_message = error_msg
                message.save(update_fields=[
                    'retry_count',
                    'delivery_status',
                    'error_message'
                ])
                
                logger.error(f"[FAILED] Message {message.id} failed: {message.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {str(e)}", exc_info=True)
            
            # تسجيل الفشل
            message.retry_count += 1
            message.delivery_status = 'failed' if message.retry_count >= self.MAX_RETRY_COUNT else 'pending'
            message.error_message = str(e)
            message.save(update_fields=[
                'retry_count',
                'delivery_status',
                'error_message'
            ])
            
            return False
    
    def process_pending(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        معالجة جميع الرسائل المعلقة
        
        Args:
            batch_size: عدد الرسائل في الدفعة (اختياري)
        
        Returns:
            Dict مع إحصائيات المعالجة
        """
        batch_size = batch_size or self.BATCH_SIZE
        
        # جلب الرسائل المعلقة
        pending_messages = Message.objects.filter(
            delivery_status='pending',
            retry_count__lt=self.MAX_RETRY_COUNT
        ).order_by('created_at')[:batch_size]
        
        if not pending_messages.exists():
            logger.info("No pending messages to process")
            return {
                'success': True,
                'processed': 0,
                'sent': 0,
                'failed': 0,
                'message': 'No pending messages'
            }
        
        logger.info(f"Processing {pending_messages.count()} pending messages...")
        
        sent_count = 0
        failed_count = 0
        
        for message in pending_messages:
            # التحقق من وقت الانتظار بين المحاولات
            if message.retry_count > 0 and message.last_retry_at:
                delay_seconds = self.RETRY_DELAY_SECONDS[min(message.retry_count - 1, len(self.RETRY_DELAY_SECONDS) - 1)]
                time_since_last_retry = (timezone.now() - message.last_retry_at).total_seconds()
                
                if time_since_last_retry < delay_seconds:
                    logger.info(f"Message {message.id} waiting for retry delay...")
                    continue
            
            # معالجة الرسالة
            success = self.process_message(message)
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
            
            # تأخير بسيط بين الرسائل (Rate Limiting)
            time.sleep(0.5)
        
        logger.info(f"[PROCESSED] Processed: {sent_count} sent, {failed_count} failed")
        
        return {
            'success': True,
            'processed': sent_count + failed_count,
            'sent': sent_count,
            'failed': failed_count,
            'message': f'Processed {sent_count + failed_count} messages'
        }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات قائمة الانتظار
        
        Returns:
            Dict مع الإحصائيات
        """
        from django.db.models import Count, Q
        
        stats = Message.objects.filter(
            direction='outgoing'
        ).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(delivery_status='pending')),
            sending=Count('id', filter=Q(delivery_status='sending')),
            sent=Count('id', filter=Q(delivery_status='sent')),
            delivered=Count('id', filter=Q(delivery_status='delivered')),
            failed=Count('id', filter=Q(delivery_status='failed'))
        )
        
        return stats
    
    def retry_failed(self, hours: int = 1) -> Dict[str, Any]:
        """
        إعادة محاولة الرسائل الفاشلة في آخر X ساعات
        
        Args:
            hours: عدد الساعات للبحث
        
        Returns:
            Dict مع نتائج المحاولة
        """
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # جلب الرسائل الفاشلة
        failed_messages = Message.objects.filter(
            delivery_status='failed',
            retry_count__lt=self.MAX_RETRY_COUNT,
            created_at__gte=cutoff_time
        )
        
        # إعادة تعيين الحالة إلى pending
        updated_count = failed_messages.update(
            delivery_status='pending',
            error_message=None
        )
        
        logger.info(f"Reset {updated_count} failed messages to pending")
        
        return {
            'success': True,
            'reset_count': updated_count,
            'message': f'{updated_count} messages reset for retry'
        }


# ============================================
# Singleton Instance
# ============================================

_message_queue_instance = None

def get_message_queue() -> MessageQueue:
    """
    الحصول على MessageQueue Singleton Instance
    
    Returns:
        MessageQueue instance
    """
    global _message_queue_instance
    
    if _message_queue_instance is None:
        _message_queue_instance = MessageQueue()
    
    return _message_queue_instance