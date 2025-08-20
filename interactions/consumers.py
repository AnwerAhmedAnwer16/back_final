import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer للإشعارات في الوقت الفعلي
    """
    
    async def connect(self):
        """اتصال WebSocket جديد"""
        # التحقق من المصادقة
        user = await self.get_user_from_token()
        if user is None or user.is_anonymous:
            logger.warning("Unauthorized WebSocket connection attempt")
            await self.close()
            return
        
        self.user = user
        self.user_group_name = f"user_{self.user.id}_notifications"
        
        # الانضمام إلى مجموعة المستخدم
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to notifications WebSocket")
        
        # إرسال الإشعارات غير المقروءة عند الاتصال
        await self.send_unread_notifications()
    
    async def disconnect(self, close_code):
        """قطع اتصال WebSocket"""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.username} disconnected from notifications WebSocket")
    
    async def receive(self, text_data):
        """استقبال رسالة من العميل"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_as_read':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_as_read(notification_id)
            elif message_type == 'mark_all_as_read':
                await self.mark_all_notifications_as_read()
            elif message_type == 'get_unread_count':
                await self.send_unread_count()
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
    
    async def notification_message(self, event):
        """إرسال إشعار جديد للعميل"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
    
    async def unread_count_update(self, event):
        """إرسال تحديث عدد الإشعارات غير المقروءة"""
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'unread_count': event['unread_count']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self):
        """استخراج المستخدم من JWT token"""
        try:
            # البحث عن التوكن في query parameters أو headers
            token = None
            
            # محاولة الحصول على التوكن من query parameters
            query_string = self.scope.get('query_string', b'').decode()
            if 'token=' in query_string:
                token = query_string.split('token=')[1].split('&')[0]
            
            # محاولة الحصول على التوكن من headers
            if not token:
                headers = dict(self.scope.get('headers', []))
                auth_header = headers.get(b'authorization', b'').decode()
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            
            if not token:
                return None
            
            # التحقق من صحة التوكن
            UntypedToken(token)
            
            # فك تشفير التوكن للحصول على user_id
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            return User.objects.get(id=user_id)
            
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in token validation: {str(e)}")
            return None
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """الحصول على الإشعارات غير المقروءة"""
        notifications = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).select_related('sender', 'trip', 'comment').order_by('-created_at')[:10]
        
        serializer = NotificationSerializer(notifications, many=True)
        return serializer.data
    
    @database_sync_to_async
    def get_unread_count(self):
        """الحصول على عدد الإشعارات غير المقروءة"""
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()
    
    async def send_unread_notifications(self):
        """إرسال الإشعارات غير المقروءة"""
        notifications = await self.get_unread_notifications()
        unread_count = await self.get_unread_count()
        
        await self.send(text_data=json.dumps({
            'type': 'initial_notifications',
            'notifications': notifications,
            'unread_count': unread_count
        }))
    
    async def send_unread_count(self):
        """إرسال عدد الإشعارات غير المقروءة"""
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'unread_count': unread_count
        }))
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """تحديد إشعار كمقروء"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_notifications_as_read(self):
        """تحديد جميع الإشعارات كمقروءة"""
        count = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True)
        return count
