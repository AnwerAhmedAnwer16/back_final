from django.db import models
from django.conf import settings
from trip.models import Trip


class Follow(models.Model):
    """نموذج المتابعة بين المستخدمين"""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='following'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Like(models.Model):
    """نموذج الإعجابات على الرحلات"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'trip')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
    
    def __str__(self):
        return f"{self.user.username} likes {self.trip.id}"


class Comment(models.Model):
    """نموذج التعليقات على الرحلات"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} commented on {self.trip.id}"
    
    @property
    def is_reply(self):
        return self.parent is not None


class Save(models.Model):
    """نموذج حفظ الرحلات"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='saves'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'trip')
        verbose_name = 'Save'
        verbose_name_plural = 'Saves'
    
    def __str__(self):
        return f"{self.user.username} saved {self.trip.id}"


class Share(models.Model):
    """نموذج مشاركة الرحلات"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='shares'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Share'
        verbose_name_plural = 'Shares'
    
    def __str__(self):
        return f"{self.user.username} shared {self.trip.id}"


class Notification(models.Model):
    """نموذج الإشعارات"""
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('share', 'Share'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} {self.notification_type} to {self.recipient.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
