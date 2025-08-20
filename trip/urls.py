from django.urls import path
from .views import (TripCreateAPIView, TripListAPIView, TripDetailAPIView, TripDeleteAPIView,
                    TripImageUploadAPIView, TripVideoUploadAPIView, TripImageDeleteAPIView, TripVideoDeleteAPIView,
                    TripTagAddAPIView, TripTagRemoveAPIView, TripTagListForTripAPIView, TagTripsView,
                    )

urlpatterns = [
    path('create/', TripCreateAPIView.as_view(), name='trip-create'),
    path('', TripListAPIView.as_view(), name='trip-list'),  
    path('<int:id>/', TripDetailAPIView.as_view(), name='trip-detail'),  
    path('<int:id>/delete/', TripDeleteAPIView.as_view(), name='trip-delete'),
    path('<int:trip_id>/images/', TripImageUploadAPIView.as_view(), name='trip-image-upload'),
    path('<int:trip_id>/videos/', TripVideoUploadAPIView.as_view(), name='trip-video-upload'),
    path('images/<int:image_id>/', TripImageDeleteAPIView.as_view(), name='trip-image-delete'),
    path('videos/<int:video_id>/', TripVideoDeleteAPIView.as_view(), name='trip-video-delete'),
    path('<int:trip_id>/tags/', TripTagAddAPIView.as_view(), name='trip-tag-add'),
    path('<int:trip_id>/tags/<int:tag_id>/', TripTagRemoveAPIView.as_view(), name='trip-tag-remove'),
    path('<int:trip_id>/tags/list/', TripTagListForTripAPIView.as_view(), name='trip-tag-list'),

    # Tag filtering
    path('tags/<str:tag_name>/trips/', TagTripsView.as_view(), name='tag-trips'),
]
