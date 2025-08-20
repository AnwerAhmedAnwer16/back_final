"""
Utility functions for real-time notifications
"""

import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


def send_notification_to_user(user_id, notification_data):
    """
    إرسال إشعار لمستخدم معين عبر WebSocket
    
    Args:
        user_id (int): معرف المستخدم
        notification_data (dict): بيانات الإشعار
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.error("Channel layer not configured")
        return
    
    group_name = f"user_{user_id}_notifications"
    
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        logger.info(f"Notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {str(e)}")


def send_unread_count_update(user_id, unread_count):
    """
    إرسال تحديث عدد الإشعارات غير المقروءة
    
    Args:
        user_id (int): معرف المستخدم
        unread_count (int): عدد الإشعارات غير المقروءة
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.error("Channel layer not configured")
        return
    
    group_name = f"user_{user_id}_notifications"
    
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'unread_count_update',
                'unread_count': unread_count
            }
        )
        logger.info(f"Unread count update sent to user {user_id}: {unread_count}")
    except Exception as e:
        logger.error(f"Failed to send unread count update to user {user_id}: {str(e)}")


def create_and_send_notification(recipient, sender, notification_type, trip=None, comment=None):
    """
    إنشاء إشعار جديد وإرساله فوراً عبر WebSocket
    
    Args:
        recipient (User): المستخدم المستقبل للإشعار
        sender (User): المستخدم المرسل للإشعار
        notification_type (str): نوع الإشعار
        trip (Trip, optional): الرحلة المرتبطة بالإشعار
        comment (Comment, optional): التعليق المرتبط بالإشعار
    
    Returns:
        Notification: الإشعار المنشأ
    """
    try:
        # إنشاء الإشعار
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            trip=trip,
            comment=comment
        )
        
        # تسلسل الإشعار
        serializer = NotificationSerializer(notification)
        notification_data = serializer.data
        
        # إرسال الإشعار عبر WebSocket
        send_notification_to_user(recipient.id, notification_data)
        
        # إرسال تحديث عدد الإشعارات غير المقروءة
        unread_count = Notification.objects.filter(
            recipient=recipient,
            is_read=False
        ).count()
        send_unread_count_update(recipient.id, unread_count)
        
        logger.info(f"Notification created and sent: {notification.id}")
        return notification
        
    except Exception as e:
        logger.error(f"Failed to create and send notification: {str(e)}")
        return None


def broadcast_notification_to_followers(sender, notification_type, trip=None, comment=None):
    """
    إرسال إشعار لجميع متابعي المستخدم
    
    Args:
        sender (User): المستخدم المرسل
        notification_type (str): نوع الإشعار
        trip (Trip, optional): الرحلة المرتبطة
        comment (Comment, optional): التعليق المرتبط
    """
    try:
        from .models import Follow
        
        # الحصول على جميع المتابعين
        followers = Follow.objects.filter(following=sender).select_related('follower')
        
        for follow in followers:
            create_and_send_notification(
                recipient=follow.follower,
                sender=sender,
                notification_type=notification_type,
                trip=trip,
                comment=comment
            )
        
        logger.info(f"Notification broadcasted to {followers.count()} followers")
        
    except Exception as e:
        logger.error(f"Failed to broadcast notification: {str(e)}")


def get_user_unread_count(user_id):
    """
    الحصول على عدد الإشعارات غير المقروءة لمستخدم
    
    Args:
        user_id (int): معرف المستخدم
    
    Returns:
        int: عدد الإشعارات غير المقروءة
    """
    try:
        return Notification.objects.filter(
            recipient_id=user_id,
            is_read=False
        ).count()
    except Exception as e:
        logger.error(f"Failed to get unread count for user {user_id}: {str(e)}")
        return 0


def mark_notification_as_read_and_update(notification_id, user_id):
    """
    تحديد إشعار كمقروء وإرسال تحديث العدد
    
    Args:
        notification_id (int): معرف الإشعار
        user_id (int): معرف المستخدم
    
    Returns:
        bool: True إذا تم التحديث بنجاح
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient_id=user_id
        )
        notification.mark_as_read()
        
        # إرسال تحديث العدد
        unread_count = get_user_unread_count(user_id)
        send_unread_count_update(user_id, unread_count)
        
        return True
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found for user {user_id}")
        return False
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {str(e)}")
        return False


def mark_all_notifications_as_read_and_update(user_id):
    """
    تحديد جميع الإشعارات كمقروءة وإرسال تحديث العدد
    
    Args:
        user_id (int): معرف المستخدم
    
    Returns:
        int: عدد الإشعارات التي تم تحديثها
    """
    try:
        count = Notification.objects.filter(
            recipient_id=user_id,
            is_read=False
        ).update(is_read=True)
        
        # إرسال تحديث العدد (سيكون 0)
        send_unread_count_update(user_id, 0)
        
        return count
        
    except Exception as e:
        logger.error(f"Failed to mark all notifications as read for user {user_id}: {str(e)}")
        return 0
