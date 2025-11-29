"""
WhatsApp Driver Pattern
نمط Driver للتعامل مع مزودي WhatsApp المختلفين

يسمح بالتبديل بين WPPConnect و Cloud API بدون تغيير الكود التجاري
"""

import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class IncomingMessage:
    """رسالة واردة من WhatsApp"""
    id_ext: str              # ID من WhatsApp
    phone: str               # رقم المرسل
    message_text: str        # نص الرسالة
    message_type: str        # text, image, audio, video, document
    sender_name: str         # اسم المرسل
    timestamp: int           # وقت الإرسال
    is_from_me: bool         # هل الرسالة مني؟
    media_url: Optional[str] = None  # رابط الميديا (إن وجد)
    mime_type: Optional[str] = None  # نوع الملف
    raw_data: Optional[Dict[str, Any]] = None  # البيانات الخام


@dataclass
class OutgoingMessage:
    """رسالة صادرة إلى WhatsApp"""
    phone: str               # رقم المستقبل
    message: str             # نص الرسالة
    message_type: str = 'text'  # نوع الرسالة
    media_url: Optional[str] = None  # رابط الميديا (للصور/الفيديو)


class MessageDriver(ABC):
    """
    Interface موحد لجميع مزودي WhatsApp
    
    يجب على كل Driver تطبيق هذه الدوال:
    - send_text_message()
    - send_media_message()
    - get_connection_status()
    - get_qr_code()
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = "base"
    
    @abstractmethod
    def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """إرسال رسالة نصية"""
        pass
    
    @abstractmethod
    def send_media_message(self, phone: str, media_url: str, 
                          media_type: str, caption: str = None) -> Dict[str, Any]:
        """إرسال ميديا (صورة/فيديو/ملف)"""
        pass
    
    @abstractmethod
    def get_connection_status(self) -> Dict[str, Any]:
        """الحصول على حالة الاتصال"""
        pass
    
    @abstractmethod
    def get_qr_code(self) -> Dict[str, Any]:
        """الحصول على QR Code للربط"""
        pass
    
    def normalize_phone(self, phone: str) -> str:
        """توحيد صيغة رقم الهاتف"""
        phone = phone.strip().replace('+', '').replace(' ', '').replace('-', '')
        
        if phone.startswith('0'):
            phone = '20' + phone[1:]
        
        if not phone.startswith('20'):
            phone = '20' + phone
        
        return phone


class WPPConnectDriver(MessageDriver):
    """
    WPPConnect Driver
    
    يتصل بـ WPPConnect Server عبر REST API
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "wppconnect"
        self.base_url = config.get('base_url', 'http://localhost:3000')
        self.api_key = config.get('api_key', '')
        self.timeout = config.get('timeout', 30)
    
    def _get_headers(self) -> Dict[str, str]:
        """الحصول على Headers للـ API"""
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
    
    def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        إرسال رسالة نصية عبر WPPConnect

        Args:
            phone: رقم الهاتف أو chatId (مع @c.us أو @lid)
            message: نص الرسالة

        Returns:
            Dict مع success و message_id
        """
        try:
            # ✅ إذا كان الرقم يحتوي على @ (chatId)، نستخدمه مباشرة
            # وإلا نطبعه
            if '@' in phone:
                # الرقم يحتوي على chatId كامل (مثل 201003648984@c.us)
                phone_to_send = phone
                logger.info(f"Using full chatId: {phone_to_send}")
            else:
                # رقم عادي، نطبعه
                phone_to_send = self.normalize_phone(phone)
                logger.info(f"Normalized phone: {phone_to_send}")

            url = f"{self.base_url}/api/send-message"
            payload = {
                'phone': phone_to_send,
                'message': message
            }

            logger.info(f"Sending message to {phone_to_send} via WPPConnect")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                logger.info(f"Message sent successfully: {data.get('message_id')}")
                return {
                    'success': True,
                    'message_id': data.get('message_id'),
                    'provider': self.provider_name,
                    'phone': data.get('phone', phone_to_send),
                    'chat_id': data.get('chat_id', phone_to_send)  # ✅ حفظ chatId
                }
            else:
                logger.error(f"Failed to send message: {data}")
                return {
                    'success': False,
                    'error': data.get('error', 'Unknown error'),
                    'provider': self.provider_name
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def send_media_message(self, phone: str, media_url: str, 
                          media_type: str, caption: str = None) -> Dict[str, Any]:
        """
        إرسال ميديا عبر WPPConnect
        
        Args:
            phone: رقم الهاتف أو chatId (مع @c.us أو @lid)
            media_url: رابط الصورة/الفيديو (URL كامل)
            media_type: نوع الميديا (image, video, document, audio)
            caption: عنوان الصورة (اختياري)
        
        Returns:
            Dict مع success و message_id
        """
        try:
            # ✅ إذا كان الرقم يحتوي على @ (chatId)، نستخدمه مباشرة
            if '@' in phone:
                phone_to_send = phone
                logger.info(f"Using full chatId for media: {phone_to_send}")
            else:
                phone_to_send = self.normalize_phone(phone)
                logger.info(f"Normalized phone for media: {phone_to_send}")

            url = f"{self.base_url}/api/send-media"
            
            # تحضير البيانات
            payload = {
                'phone': phone_to_send,
                'media_url': media_url,
                'media_type': media_type
            }
            
            # إضافة العنوان إن وجد
            if caption:
                payload['caption'] = caption

            logger.info(f"Sending {media_type} to {phone_to_send} - URL: {media_url}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                logger.info(f"Media sent successfully: {data.get('message_id')}")
                return {
                    'success': True,
                    'message_id': data.get('message_id'),
                    'provider': self.provider_name,
                    'phone': data.get('phone', phone_to_send),
                    'chat_id': data.get('chat_id', phone_to_send)
                }
            else:
                logger.error(f"Failed to send media: {data}")
                return {
                    'success': False,
                    'error': data.get('error', 'Unknown error'),
                    'provider': self.provider_name
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending media: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Unexpected error sending media: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة الاتصال بـ WhatsApp
        
        Returns:
            Dict مع connected و phone و device
        """
        try:
            url = f"{self.base_url}/api/status"
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'connected': data.get('connected', False),
                'phone': data.get('phone'),
                'device': data.get('device'),
                'session': data.get('session'),
                'provider': self.provider_name
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_qr_code(self) -> Dict[str, Any]:
        """
        الحصول على QR Code للربط
        
        Returns:
            Dict مع qr_code (base64) و qr_url
        """
        try:
            url = f"{self.base_url}/api/qr-code"
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return {
                    'success': True,
                    'qr_code': data.get('qr_code'),
                    'qr_url': data.get('qr_url'),
                    'provider': self.provider_name
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message'),
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Error getting QR code: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }


class CloudAPIDriver(MessageDriver):
    """
    WhatsApp Business Cloud API Driver
    
    يتصل بـ WhatsApp Business API عبر Graph API من Meta
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "cloud_api"
        self.access_token = config.get('access_token', '')
        self.phone_number_id = config.get('phone_number_id', '')
        self.business_account_id = config.get('business_account_id', '')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        
        if not self.access_token or not self.phone_number_id:
            logger.error("CloudAPIDriver: Missing access_token or phone_number_id")
    
    def _get_headers(self) -> Dict[str, str]:
        """الحصول على Headers للـ API"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        إرسال رسالة نصية عبر WhatsApp Business API
        
        Args:
            phone: رقم الهاتف (مع كود الدولة، بدون +)
            message: نص الرسالة
        
        Returns:
            Dict مع success و message_id
        """
        try:
            phone = self.normalize_phone(phone)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            logger.info(f"Sending text message to {phone} via Cloud API")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            message_id = data.get('messages', [{}])[0].get('id')
            
            if message_id:
                logger.info(f"Message sent successfully via Cloud API: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': self.provider_name,
                    'phone': phone,
                    'wa_id': data.get('contacts', [{}])[0].get('wa_id')
                }
            else:
                logger.error(f"Cloud API response missing message_id: {data}")
                return {
                    'success': False,
                    'error': 'No message_id in response',
                    'provider': self.provider_name
                }
                
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            logger.error(f"Cloud API HTTP error: {error_message}")
            return {
                'success': False,
                'error': error_message,
                'error_code': error_data.get('error', {}).get('code'),
                'provider': self.provider_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud API request error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Cloud API unexpected error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def send_media_message(self, phone: str, media_url: str, 
                          media_type: str, caption: str = None) -> Dict[str, Any]:
        """
        إرسال ميديا عبر WhatsApp Business API
        
        Args:
            phone: رقم الهاتف (مع كود الدولة، بدون +)
            media_url: رابط الصورة/الفيديو (يجب أن يكون HTTPS)
            media_type: نوع الميديا (image, video, document, audio)
            caption: عنوان الصورة (اختياري)
        
        Returns:
            Dict مع success و message_id
        """
        try:
            phone = self.normalize_phone(phone)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            # تحويل media_type للصيغة المتوافقة مع Cloud API
            type_mapping = {
                'image': 'image',
                'video': 'video',
                'audio': 'audio',
                'document': 'document',
                'file': 'document'
            }
            
            cloud_type = type_mapping.get(media_type, 'document')
            
            # بناء payload حسب نوع الميديا
            media_object = {
                "link": media_url
            }
            
            # إضافة caption للصور والفيديو فقط
            if caption and cloud_type in ['image', 'video']:
                media_object['caption'] = caption
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone,
                "type": cloud_type,
                cloud_type: media_object
            }
            
            logger.info(f"Sending {cloud_type} to {phone} via Cloud API - URL: {media_url}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            message_id = data.get('messages', [{}])[0].get('id')
            
            if message_id:
                logger.info(f"Media sent successfully via Cloud API: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': self.provider_name,
                    'phone': phone,
                    'wa_id': data.get('contacts', [{}])[0].get('wa_id')
                }
            else:
                logger.error(f"Cloud API response missing message_id: {data}")
                return {
                    'success': False,
                    'error': 'No message_id in response',
                    'provider': self.provider_name
                }
                
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            logger.error(f"Cloud API HTTP error sending media: {error_message}")
            return {
                'success': False,
                'error': error_message,
                'error_code': error_data.get('error', {}).get('code'),
                'provider': self.provider_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud API request error sending media: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Cloud API unexpected error sending media: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة الاتصال بـ WhatsApp Business API
        
        Returns:
            Dict مع connected و phone و account info
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'connected': True,
                'phone': data.get('display_phone_number'),
                'verified_name': data.get('verified_name'),
                'quality_rating': data.get('quality_rating'),
                'id': data.get('id'),
                'provider': self.provider_name
            }
            
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            logger.error(f"Cloud API status check error: {error_message}")
            return {
                'success': False,
                'connected': False,
                'error': error_message,
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Error getting Cloud API status: {str(e)}")
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_qr_code(self) -> Dict[str, Any]:
        """
        QR Code غير متوفر في Cloud API
        Cloud API يستخدم التحقق عبر رقم الهاتف مباشرة
        
        Returns:
            Dict مع success=False و رسالة توضيحية
        """
        return {
            'success': False,
            'message': 'QR Code not available in WhatsApp Business Cloud API. Phone verification is used instead.',
            'provider': self.provider_name
        }


class ElmujibCloudAPIDriver(MessageDriver):
    """
    Elmujib Cloud Business API Driver
    
    يتصل بـ Elmujib Cloud Business API عبر REST API
    
    Supports two authentication methods:
    1. Bearer Token in Authorization header (default)
    2. Token as query parameter (?token=...)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "elmujib_cloud"
        self.base_url = config.get('base_url', 'https://elmujib.com/api')
        self.vendor_uid = config.get('vendor_uid', '')
        self.bearer_token = config.get('bearer_token', '')
        self.from_phone_number_id = config.get('from_phone_number_id', '')
        self.timeout = config.get('timeout', 30)
        self.auth_method = config.get('auth_method', 'header')
        
        if not self.vendor_uid or not self.bearer_token:
            logger.error("ElmujibCloudAPIDriver: Missing vendor_uid or bearer_token")
    
    def _get_headers(self) -> Dict[str, str]:
        """الحصول على Headers للـ API"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.auth_method == 'header':
            headers['Authorization'] = f'Bearer {self.bearer_token}'
        
        return headers
    
    def _add_token_to_url(self, url: str) -> str:
        """إضافة Token كـ query parameter إذا كانت الطريقة 'query'"""
        if self.auth_method == 'query':
            separator = '&' if '?' in url else '?'
            return f"{url}{separator}token={self.bearer_token}"
        return url
    
    def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        إرسال رسالة نصية عبر Elmujib Cloud API
        
        Args:
            phone: رقم الهاتف
            message: نص الرسالة
        
        Returns:
            Dict مع success و message_id
        """
        try:
            phone = self.normalize_phone(phone)
            
            url = f"{self.base_url}/{self.vendor_uid}/contact/send-message"
            url = self._add_token_to_url(url)
            
            payload = {
                "phone_number": phone,
                "message_body": message
            }
            
            if self.from_phone_number_id:
                payload["from_phone_number_id"] = self.from_phone_number_id
            
            logger.info(f"Sending text message to {phone} via Elmujib Cloud API (auth: {self.auth_method})")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') in ['success', 'processed'] or str(data.get('message', '')).lower() in ['message processed', 'processed', 'ok']:
                message_id = data.get('message_id') or data.get('id')
                logger.info(f"Message sent successfully via Elmujib: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': self.provider_name,
                    'phone': phone
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error') or error_data.get('message', str(e))
            logger.error(f"Elmujib API HTTP error: {error_message}")
            return {
                'success': False,
                'error': error_message,
                'provider': self.provider_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Elmujib API request error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Elmujib API unexpected error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def send_media_message(self, phone: str, media_url: str, 
                          media_type: str, caption: str = None) -> Dict[str, Any]:
        """
        إرسال ميديا عبر Elmujib Cloud API
        
        Args:
            phone: رقم الهاتف
            media_url: رابط الصورة/الفيديو/الملف
            media_type: نوع الميديا (image, video, document, audio)
            caption: عنوان الصورة (اختياري)
        
        Returns:
            Dict مع success و message_id
        """
        try:
            phone = self.normalize_phone(phone)
            
            url = f"{self.base_url}/{self.vendor_uid}/contact/send-media-message"
            url = self._add_token_to_url(url)
            
            payload = {
                "phone_number": phone,
                "media_type": media_type,
                "media_url": media_url
            }
            
            if self.from_phone_number_id:
                payload["from_phone_number_id"] = self.from_phone_number_id
            
            if caption and media_type in ['image', 'video']:
                payload['caption'] = caption
            
            if media_type == 'document':
                payload['file_name'] = caption or 'document'
            
            logger.info(f"Sending {media_type} to {phone} via Elmujib Cloud API - URL: {media_url}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') in ['success', 'processed'] or str(data.get('message', '')).lower() in ['message processed', 'processed', 'ok']:
                message_id = data.get('message_id') or data.get('id')
                logger.info(f"Media sent successfully via Elmujib: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': self.provider_name,
                    'phone': phone
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API media error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error') or error_data.get('message', str(e))
            logger.error(f"Elmujib API HTTP error sending media: {error_message}")
            return {
                'success': False,
                'error': error_message,
                'provider': self.provider_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Elmujib API request error sending media: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
        except Exception as e:
            logger.error(f"Elmujib API unexpected error sending media: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def send_template_message(self, phone: str, template_name: str, 
                             template_language: str = 'en', 
                             template_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        إرسال رسالة Template عبر Elmujib Cloud API
        
        Args:
            phone: رقم الهاتف
            template_name: اسم الـ Template
            template_language: لغة الـ Template
            template_params: معاملات الـ Template
        
        Returns:
            Dict مع success و message_id
        """
        try:
            phone = self.normalize_phone(phone)
            
            url = f"{self.base_url}/{self.vendor_uid}/contact/send-template-message"
            url = self._add_token_to_url(url)
            
            payload = {
                "phone_number": phone,
                "template_name": template_name,
                "template_language": template_language
            }
            
            if self.from_phone_number_id:
                payload["from_phone_number_id"] = self.from_phone_number_id
            
            if template_params:
                payload.update(template_params)
            
            logger.info(f"Sending template '{template_name}' to {phone} via Elmujib Cloud API")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') in ['success', 'processed'] or str(data.get('message', '')).lower() in ['message processed', 'processed', 'ok']:
                message_id = data.get('message_id') or data.get('id')
                logger.info(f"Template sent successfully via Elmujib: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': self.provider_name,
                    'phone': phone
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API template error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Elmujib API error sending template: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def send_interactive_message(self, phone: str, interactive_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        إرسال رسالة Interactive عبر Elmujib Cloud API
        
        Args:
            phone: رقم الهاتف
            interactive_data: بيانات الرسالة Interactive
        
        Returns:
            Dict مع success و message_id
        """
        try:
            phone = self.normalize_phone(phone)
            
            url = f"{self.base_url}/{self.vendor_uid}/contact/send-interactive-message"
            url = self._add_token_to_url(url)
            
            payload = {
                "phone_number": phone,
                **interactive_data
            }
            
            if self.from_phone_number_id:
                payload["from_phone_number_id"] = self.from_phone_number_id
            
            logger.info(f"Sending interactive message to {phone} via Elmujib Cloud API")
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') in ['success', 'processed'] or str(data.get('message', '')).lower() in ['message processed', 'processed', 'ok']:
                message_id = data.get('message_id') or data.get('id')
                logger.info(f"Interactive message sent successfully via Elmujib: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'provider': self.provider_name,
                    'phone': phone
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API interactive error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Elmujib API error sending interactive: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        إنشاء جهة اتصال عبر Elmujib Cloud API
        
        Args:
            contact_data: بيانات جهة الاتصال
        
        Returns:
            Dict مع success و contact_id
        """
        try:
            url = f"{self.base_url}/{self.vendor_uid}/contact/create"
            url = self._add_token_to_url(url)
            
            logger.info(f"Creating contact via Elmujib Cloud API")
            
            response = requests.post(
                url,
                json=contact_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') in ['success', 'processed']:
                logger.info(f"Contact created successfully via Elmujib")
                return {
                    'success': True,
                    'data': data,
                    'provider': self.provider_name
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API contact creation error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Elmujib API error creating contact: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def update_contact(self, phone: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تحديث جهة اتصال عبر Elmujib Cloud API
        
        Args:
            phone: رقم الهاتف
            contact_data: بيانات التحديث
        
        Returns:
            Dict مع success
        """
        try:
            phone = self.normalize_phone(phone)
            url = f"{self.base_url}/{self.vendor_uid}/contact/update/{phone}"
            url = self._add_token_to_url(url)
            
            logger.info(f"Updating contact {phone} via Elmujib Cloud API")
            
            response = requests.post(
                url,
                json=contact_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') in ['success', 'processed']:
                logger.info(f"Contact updated successfully via Elmujib")
                return {
                    'success': True,
                    'data': data,
                    'provider': self.provider_name
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API contact update error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Elmujib API error updating contact: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_contact(self, phone_or_email: str) -> Dict[str, Any]:
        """
        الحصول على جهة اتصال عبر Elmujib Cloud API
        
        Args:
            phone_or_email: رقم الهاتف أو البريد الإلكتروني
        
        Returns:
            Dict مع success و contact data
        """
        try:
            url = f"{self.base_url}/{self.vendor_uid}/contact"
            url = self._add_token_to_url(url)
            
            params = {'phone_number_or_email': phone_or_email}
            
            logger.info(f"Getting contact {phone_or_email} via Elmujib Cloud API")
            
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') or data.get('status') == 'success':
                logger.info(f"Contact retrieved successfully via Elmujib")
                return {
                    'success': True,
                    'data': data,
                    'provider': self.provider_name
                }
            else:
                error_msg = data.get('error') or data.get('message', 'Unknown error')
                logger.error(f"Elmujib API get contact error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Elmujib API error getting contact: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        الحصول على حالة الاتصال
        
        Returns:
            Dict مع connected
        """
        try:
            # Check if credentials are properly configured
            if self.vendor_uid and self.bearer_token and self.bearer_token != 'your_bearer_token_here':
                logger.info(f"Elmujib API credentials configured - Vendor UID: {self.vendor_uid}")
                return {
                    'success': True,
                    'connected': True,
                    'provider': self.provider_name,
                    'vendor_uid': self.vendor_uid
                }
            else:
                logger.error("Elmujib API credentials not properly configured")
                return {
                    'success': False,
                    'connected': False,
                    'error': 'Missing or invalid credentials',
                    'provider': self.provider_name
                }
                
        except Exception as e:
            logger.error(f"Elmujib API connection check error: {str(e)}")
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'provider': self.provider_name
            }
    
    def get_qr_code(self) -> Dict[str, Any]:
        """
        QR Code غير متوفر في Elmujib Cloud API
        
        Returns:
            Dict مع success=False و رسالة توضيحية
        """
        return {
            'success': False,
            'message': 'QR Code not available in Elmujib Cloud Business API. Bearer token authentication is used.',
            'provider': self.provider_name
        }


# ============================================
# Driver Factory
# ============================================

def get_whatsapp_driver() -> MessageDriver:
    """
    الحصول على WhatsApp Driver المناسب
    
    يقرأ من settings.py:
    WHATSAPP_DRIVER = 'wppconnect'  # أو 'cloud_api' أو 'elmujib_cloud'
    
    Returns:
        MessageDriver instance
    """
    driver_type = getattr(settings, 'WHATSAPP_DRIVER', 'wppconnect')
    
    if driver_type == 'wppconnect':
        config = {
            'base_url': getattr(settings, 'WPPCONNECT_BASE_URL', 'http://localhost:3000'),
            'api_key': getattr(settings, 'WPPCONNECT_API_KEY', 'your-secret-api-key'),
            'timeout': getattr(settings, 'WPPCONNECT_TIMEOUT', 30)
        }
        return WPPConnectDriver(config)
    
    elif driver_type == 'cloud_api':
        config = {
            'access_token': getattr(settings, 'WHATSAPP_CLOUD_ACCESS_TOKEN', ''),
            'phone_number_id': getattr(settings, 'WHATSAPP_CLOUD_PHONE_NUMBER_ID', ''),
            'business_account_id': getattr(settings, 'WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID', '')
        }
        return CloudAPIDriver(config)
    
    elif driver_type == 'elmujib_cloud':
        config = {
            'base_url': getattr(settings, 'ELMUJIB_API_BASE_URL', 'https://elmujib.com/api'),
            'vendor_uid': getattr(settings, 'ELMUJIB_VENDOR_UID', ''),
            'bearer_token': getattr(settings, 'ELMUJIB_BEARER_TOKEN', ''),
            'from_phone_number_id': getattr(settings, 'ELMUJIB_FROM_PHONE_NUMBER_ID', ''),
            'auth_method': getattr(settings, 'ELMUJIB_AUTH_METHOD', 'header'),
            'timeout': getattr(settings, 'ELMUJIB_TIMEOUT', 30)
        }
        return ElmujibCloudAPIDriver(config)
    
    else:
        raise ValueError(f"Unknown WhatsApp driver: {driver_type}")
