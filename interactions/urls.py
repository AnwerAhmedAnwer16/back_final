from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Follow URLs
    path('follow/', views.follow_user, name='follow_user'),
    path('unfollow/', views.unfollow_user, name='unfollow_user'),
    path('followers/<int:user_id>/', views.FollowersListView.as_view(), name='followers_list'),
    path('following/<int:user_id>/', views.FollowingListView.as_view(), name='following_list'),
    
    # Like URLs
    path('like/', views.like_trip, name='like_trip'),
    path('unlike/', views.unlike_trip, name='unlike_trip'),
    path('likes/<int:trip_id>/', views.TripLikesListView.as_view(), name='trip_likes'),
    
    # Comment URLs
    path('comment/', views.CommentCreateView.as_view(), name='create_comment'),
    path('comments/<int:trip_id>/', views.TripCommentsListView.as_view(), name='trip_comments'),
    path('comment/<int:pk>/', views.CommentUpdateView.as_view(), name='update_comment'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='delete_comment'),
    
    # Save URLs
    path('save/', views.save_trip, name='save_trip'),
    path('unsave/', views.unsave_trip, name='unsave_trip'),
    path('saved/', views.SavedTripsListView.as_view(), name='saved_trips'),
    
    # Share URLs
    path('share/', views.share_trip, name='share_trip'),
    
    # Feed URLs
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('explore/', views.ExploreView.as_view(), name='explore'),
    
    # Notification URLs
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/read-realtime/', views.mark_notification_read_realtime, name='mark_notification_read_realtime'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_notifications_count, name='unread_notifications_count'),
    path('notifications/recent/', views.get_recent_notifications, name='recent_notifications'),
    path('notifications/settings/', views.get_notification_settings, name='notification_settings'),
    path('notifications/settings/update/', views.update_notification_settings, name='update_notification_settings'),
    
    # Stats URLs
    path('stats/user/<int:user_id>/', views.user_stats, name='user_stats'),
    path('stats/trip/<int:trip_id>/', views.trip_stats, name='trip_stats'),
]

