from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.db import transaction

from .models import Follow, Like, Comment, Save, Share, Notification
from .serializers import (
    FollowSerializer, LikeSerializer, CommentSerializer, 
    SaveSerializer, ShareSerializer, NotificationSerializer,
    UserStatsSerializer, TripStatsSerializer
)
from trip.models import Trip
from trip.serializers import TripSerializer

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Follow Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request):
    """متابعة مستخدم"""
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_to_follow = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if user_to_follow == request.user:
        return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        # إنشاء إشعار
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type='follow'
        )
        return Response({'message': 'User followed successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already following this user'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request):
    """إلغاء متابعة مستخدم"""
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_to_unfollow = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        follow = Follow.objects.get(follower=request.user, following=user_to_unfollow)
        follow.delete()
        return Response({'message': 'User unfollowed successfully'}, status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        return Response({'error': 'Not following this user'}, status=status.HTTP_400_BAD_REQUEST)


class FollowersListView(generics.ListAPIView):
    """قائمة المتابعين"""
    serializer_class = FollowSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Follow.objects.filter(following_id=user_id).select_related('follower', 'following')


class FollowingListView(generics.ListAPIView):
    """قائمة المتابَعين"""
    serializer_class = FollowSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Follow.objects.filter(follower_id=user_id).select_related('follower', 'following')


# Like Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_trip(request):
    """إعجاب برحلة"""
    trip_id = request.data.get('trip_id')
    if not trip_id:
        return Response({'error': 'trip_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    like, created = Like.objects.get_or_create(user=request.user, trip=trip)
    
    if created:
        # إنشاء إشعار إذا لم يكن المستخدم يعجب بمنشوره الخاص
        if trip.user != request.user:
            Notification.objects.create(
                recipient=trip.user,
                sender=request.user,
                notification_type='like',
                trip=trip
            )
        return Response({'message': 'Trip liked successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already liked this trip'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unlike_trip(request):
    """إلغاء الإعجاب برحلة"""
    trip_id = request.data.get('trip_id')
    if not trip_id:
        return Response({'error': 'trip_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        like = Like.objects.get(user=request.user, trip=trip)
        like.delete()
        return Response({'message': 'Trip unliked successfully'}, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({'error': 'Not liked this trip'}, status=status.HTTP_400_BAD_REQUEST)


class TripLikesListView(generics.ListAPIView):
    """قائمة المعجبين برحلة"""
    serializer_class = LikeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        trip_id = self.kwargs['trip_id']
        return Like.objects.filter(trip_id=trip_id).select_related('user')

    def get_serializer_context(self):
        # Pass the request to the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
# Comment Views
class CommentCreateView(generics.CreateAPIView):
    """إضافة تعليق"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        trip_id = self.request.data.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        comment = serializer.save(user=self.request.user, trip=trip)
        
        # إنشاء إشعار
        if trip.user != self.request.user:
            Notification.objects.create(
                recipient=trip.user,
                sender=self.request.user,
                notification_type='comment',
                trip=trip,
                comment=comment
            )


class TripCommentsListView(generics.ListAPIView):
    """قائمة تعليقات رحلة"""
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        trip_id = self.kwargs['trip_id']
        return Comment.objects.filter(
            trip_id=trip_id, 
            parent__isnull=True
        ).select_related('user').prefetch_related('replies')


class CommentUpdateView(generics.UpdateAPIView):
    """تعديل تعليق"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)


class CommentDeleteView(generics.DestroyAPIView):
    """حذف تعليق"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)


# Save Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_trip(request):
    """حفظ رحلة"""
    trip_id = request.data.get('trip_id')
    if not trip_id:
        return Response({'error': 'trip_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    save, created = Save.objects.get_or_create(user=request.user, trip=trip)
    
    if created:
        return Response({'message': 'Trip saved successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already saved this trip'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unsave_trip(request):
    """إلغاء حفظ رحلة"""
    trip_id = request.data.get('trip_id')
    if not trip_id:
        return Response({'error': 'trip_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        save = Save.objects.get(user=request.user, trip=trip)
        save.delete()
        return Response({'message': 'Trip unsaved successfully'}, status=status.HTTP_200_OK)
    except Save.DoesNotExist:
        return Response({'error': 'Not saved this trip'}, status=status.HTTP_400_BAD_REQUEST)


class SavedTripsListView(generics.ListAPIView):
    """قائمة الرحلات المحفوظة"""
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        saved_trips = Save.objects.filter(user=self.request.user).values_list('trip_id', flat=True)
        return Trip.objects.filter(id__in=saved_trips).select_related('user').prefetch_related('images', 'videos')


# Share Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_trip(request):
    """مشاركة رحلة"""
    trip_id = request.data.get('trip_id')
    if not trip_id:
        return Response({'error': 'trip_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    share = Share.objects.create(user=request.user, trip=trip)
    
    # إنشاء إشعار
    if trip.user != request.user:
        Notification.objects.create(
            recipient=trip.user,
            sender=request.user,
            notification_type='share',
            trip=trip
        )
    
    return Response({'message': 'Trip shared successfully'}, status=status.HTTP_201_CREATED)


# Feed Views
class FeedView(generics.ListAPIView):
    """الخلاصة الرئيسية - منشورات المتابَعين"""
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # الحصول على المستخدمين المتابَعين
        following_users = Follow.objects.filter(
            follower=self.request.user
        ).values_list('following_id', flat=True)
        
        # إضافة منشورات المستخدم نفسه
        user_ids = list(following_users) + [self.request.user.id]
        
        return Trip.objects.filter(
            user_id__in=user_ids
        ).select_related('user').prefetch_related(
            'images', 'videos', 'likes', 'comments', 'saves'
        ).order_by('-created_at')


class ExploreView(generics.ListAPIView):
    """استكشاف المنشورات"""
    serializer_class = TripSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Trip.objects.all().select_related('user').prefetch_related(
            'images', 'videos', 'likes', 'comments', 'saves'
        ).annotate(
            likes_count=Count('likes')
        ).order_by('-likes_count', '-created_at')


# Notification Views
class NotificationListView(generics.ListAPIView):
    """قائمة الإشعارات"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'trip', 'comment')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """تحديد إشعار كمقروء"""
    try:
        notification = Notification.objects.get(
            id=notification_id, 
            recipient=request.user
        )
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    from .utils import mark_all_notifications_as_read_and_update

    count = mark_all_notifications_as_read_and_update(request.user.id)
    return Response({
        'message': f'{count} notifications marked as read',
        'count': count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_unread_notifications_count(request):
    """الحصول على عدد الإشعارات غير المقروءة"""
    from .utils import get_user_unread_count

    unread_count = get_user_unread_count(request.user.id)
    return Response({
        'unread_count': unread_count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_recent_notifications(request):
    """الحصول على أحدث الإشعارات (مقروءة وغير مقروءة)"""
    limit = int(request.GET.get('limit', 20))

    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'trip', 'comment').order_by('-created_at')[:limit]

    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'notifications': serializer.data,
        'count': notifications.count()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read_realtime(request, notification_id):
    """تحديد إشعار كمقروء مع تحديث real-time"""
    from .utils import mark_notification_as_read_and_update

    success = mark_notification_as_read_and_update(notification_id, request.user.id)

    if success:
        return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, notification_id):
    """حذف إشعار"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.delete()

        # إرسال تحديث العدد
        from .utils import get_user_unread_count, send_unread_count_update
        unread_count = get_user_unread_count(request.user.id)
        send_unread_count_update(request.user.id, unread_count)

        return Response({'message': 'Notification deleted'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_notification_settings(request):
    """الحصول على إعدادات الإشعارات للمستخدم"""
    # يمكن إضافة نموذج NotificationSettings لاحقاً
    # حالياً سنرجع إعدادات افتراضية
    settings = {
        'likes_enabled': True,
        'comments_enabled': True,
        'follows_enabled': True,
        'shares_enabled': True,
        'email_notifications': False,
        'push_notifications': True
    }
    return Response(settings, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_notification_settings(request):
    """تحديث إعدادات الإشعارات"""
    # يمكن تطوير هذا لاحقاً مع نموذج NotificationSettings
    return Response({'message': 'Settings updated successfully'}, status=status.HTTP_200_OK)


# Stats Views
@api_view(['GET'])
def user_stats(request, user_id):
    """إحصائيات المستخدم"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    trips_count = Trip.objects.filter(user=user).count()
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=user
        ).exists()
    
    stats = {
        'followers_count': followers_count,
        'following_count': following_count,
        'trips_count': trips_count,
        'is_following': is_following
    }
    
    serializer = UserStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
def trip_stats(request, trip_id):
    """إحصائيات الرحلة"""
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    likes_count = Like.objects.filter(trip=trip).count()
    comments_count = Comment.objects.filter(trip=trip).count()
    saves_count = Save.objects.filter(trip=trip).count()
    shares_count = Share.objects.filter(trip=trip).count()
    
    is_liked = False
    is_saved = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, trip=trip).exists()
        is_saved = Save.objects.filter(user=request.user, trip=trip).exists()
    
    stats = {
        'likes_count': likes_count,
        'comments_count': comments_count,
        'saves_count': saves_count,
        'shares_count': shares_count,
        'is_liked': is_liked,
        'is_saved': is_saved
    }
    
    serializer = TripStatsSerializer(stats)
    return Response(serializer.data)
