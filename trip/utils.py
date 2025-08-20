from django.db.models import Count
from interactions.models import Like, Comment, Save, Share


def get_trip_stats(trip, user=None):
    """الحصول على إحصائيات الرحلة"""
    stats = {
        'likes_count': trip.likes.count(),
        'comments_count': trip.comments.count(),
        'saves_count': trip.saves.count(),
        'shares_count': trip.shares.count(),
        'is_liked': False,
        'is_saved': False,
    }
    
    if user and user.is_authenticated:
        stats['is_liked'] = trip.likes.filter(user=user).exists()
        stats['is_saved'] = trip.saves.filter(user=user).exists()
    
    return stats


def get_user_stats(user, current_user=None):
    """الحصول على إحصائيات المستخدم"""
    from interactions.models import Follow
    
    stats = {
        'followers_count': user.followers.count(),
        'following_count': user.following.count(),
        'trips_count': user.trips.count(),
        'is_following': False,
    }
    
    if current_user and current_user.is_authenticated and current_user != user:
        stats['is_following'] = user.followers.filter(follower=current_user).exists()
    
    return stats

