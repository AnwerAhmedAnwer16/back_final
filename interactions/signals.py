from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Follow, Like, Comment, Save, Share, Notification
from .utils import create_and_send_notification

User = get_user_model()


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند المتابعة وإرساله فوراً"""
    if created:
        # التحقق من عدم وجود إشعار مماثل
        existing_notification = Notification.objects.filter(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow'
        ).first()

        if not existing_notification:
            create_and_send_notification(
                recipient=instance.following,
                sender=instance.follower,
                notification_type='follow'
            )


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند الإعجاب وإرساله فوراً"""
    if created and instance.trip.user != instance.user:
        # التحقق من عدم وجود إشعار مماثل
        existing_notification = Notification.objects.filter(
            recipient=instance.trip.user,
            sender=instance.user,
            notification_type='like',
            trip=instance.trip
        ).first()

        if not existing_notification:
            create_and_send_notification(
                recipient=instance.trip.user,
                sender=instance.user,
                notification_type='like',
                trip=instance.trip
            )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند التعليق وإرساله فوراً"""
    if created and instance.trip.user != instance.user:
        create_and_send_notification(
            recipient=instance.trip.user,
            sender=instance.user,
            notification_type='comment',
            trip=instance.trip,
            comment=instance
        )


@receiver(post_save, sender=Share)
def create_share_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند المشاركة وإرساله فوراً"""
    if created and instance.trip.user != instance.user:
        create_and_send_notification(
            recipient=instance.trip.user,
            sender=instance.user,
            notification_type='share',
            trip=instance.trip
        )


@receiver(post_save, sender=Share)
def create_share_notification(sender, instance, created, **kwargs):
    """إنشاء إشعار عند المشاركة"""
    if created and instance.trip.user != instance.user:
        Notification.objects.get_or_create(
            recipient=instance.trip.user,
            sender=instance.user,
            notification_type='share',
            trip=instance.trip
        )


@receiver(post_delete, sender=Follow)
def delete_follow_notification(sender, instance, **kwargs):
    """حذف إشعار المتابعة عند إلغاء المتابعة"""
    Notification.objects.filter(
        recipient=instance.following,
        sender=instance.follower,
        notification_type='follow'
    ).delete()


@receiver(post_delete, sender=Like)
def delete_like_notification(sender, instance, **kwargs):
    """حذف إشعار الإعجاب عند إلغاء الإعجاب"""
    Notification.objects.filter(
        recipient=instance.trip.user,
        sender=instance.user,
        notification_type='like',
        trip=instance.trip
    ).delete()


@receiver(post_delete, sender=Comment)
def delete_comment_notification(sender, instance, **kwargs):
    """حذف إشعار التعليق عند حذف التعليق"""
    Notification.objects.filter(
        recipient=instance.trip.user,
        sender=instance.user,
        notification_type='comment',
        trip=instance.trip,
        comment=instance
    ).delete()

