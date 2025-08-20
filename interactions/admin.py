from django.contrib import admin
from .models import Follow, Like, Comment, Save, Share, Notification


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    raw_id_fields = ['follower', 'following']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'trip', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'trip__caption']
    raw_id_fields = ['user', 'trip']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'trip', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'content', 'trip__caption']
    raw_id_fields = ['user', 'trip', 'parent']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    list_display = ['user', 'trip', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'trip__caption']
    raw_id_fields = ['user', 'trip']


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['user', 'trip', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'trip__caption']
    raw_id_fields = ['user', 'trip']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username']
    raw_id_fields = ['recipient', 'sender', 'trip', 'comment']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'
