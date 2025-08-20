from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow, Like, Comment, Save, Share, Notification
from trip.models import Trip
from accounts.serializers import UserSerializer

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ['id', 'user', 'trip', 'created_at', 'is_following']
        read_only_fields = ['id', 'user', 'created_at']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user,
                following=obj.user
            ).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'trip', 'content', 'parent', 
            'created_at', 'updated_at', 'is_reply', 
            'replies', 'replies_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_reply']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class SaveSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Save
        fields = ['id', 'user', 'trip', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Share
        fields = ['id', 'user', 'trip', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    trip_title = serializers.SerializerMethodField()
    trip_image = serializers.SerializerMethodField()
    comment_content = serializers.SerializerMethodField()
    notification_message = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'notification_type',
            'trip', 'comment', 'is_read', 'created_at',
            'trip_title', 'trip_image', 'comment_content',
            'notification_message', 'time_ago'
        ]
        read_only_fields = ['id', 'sender', 'created_at']

    def get_trip_title(self, obj):
        """الحصول على عنوان الرحلة"""
        if obj.trip:
            return obj.trip.title
        return None

    def get_trip_image(self, obj):
        """الحصول على صورة الرحلة"""
        if obj.trip and obj.trip.images.exists():
            first_image = obj.trip.images.first()
            if first_image and first_image.image:
                return first_image.image.url
        return None

    def get_comment_content(self, obj):
        """الحصول على محتوى التعليق"""
        if obj.comment:
            return obj.comment.content[:100] + "..." if len(obj.comment.content) > 100 else obj.comment.content
        return None

    def get_notification_message(self, obj):
        """إنشاء رسالة الإشعار"""
        sender_name = obj.sender.username if obj.sender else "مستخدم"

        messages = {
            'like': f"{sender_name} أعجب برحلتك",
            'comment': f"{sender_name} علق على رحلتك",
            'follow': f"{sender_name} بدأ متابعتك",
            'share': f"{sender_name} شارك رحلتك"
        }

        return messages.get(obj.notification_type, "إشعار جديد")

    def get_time_ago(self, obj):
        """حساب الوقت المنقضي منذ الإشعار"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "الآن"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"منذ {minutes} دقيقة"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"منذ {hours} ساعة"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"منذ {days} يوم"
        else:
            return obj.created_at.strftime("%Y-%m-%d")


# Serializers للإحصائيات
class UserStatsSerializer(serializers.Serializer):
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
    trips_count = serializers.IntegerField()
    is_following = serializers.BooleanField()


class TripStatsSerializer(serializers.Serializer):
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    saves_count = serializers.IntegerField()
    shares_count = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    is_saved = serializers.BooleanField()

