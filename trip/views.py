# trip/views.py

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from accounts.permissons import IsVerifiedUser, IsOwner
from .models import Trip, TripImage, TripVideo, TripTag
from .serializers import TripSerializer, TripImageSerializer, TripVideoSerializer, TripTagSerializer
from .ai_services import TourismAIService
from django.shortcuts import get_object_or_404
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)

class TripCreateAPIView(generics.CreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def post(self, request, *args, **kwargs):
        user = request.user
        caption = request.data.get('caption')
        location = request.data.get('location')

        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        tags = request.data.getlist('tags')  # Assuming tag names

        if not images and not videos:
            return Response({'detail': 'You must upload at least one image or one video.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # الحصول على معلومات سياحية من AI
        tourism_data = {}
        country = ""
        city = ""

        if location:
            try:
                logger.info(f"Getting tourism info for location: {location}")
                ai_service = TourismAIService()
                tourism_data = ai_service.get_destination_info(location)

                country = tourism_data.get('country', '')
                city = tourism_data.get('city', '')
                tourism_info = tourism_data.get('tourism_info', {})

                logger.info(f"AI service returned data for {location}: country={country}, city={city}")

            except Exception as e:
                logger.error(f"Error getting tourism info for {location}: {str(e)}")
                # في حالة فشل AI، نستمر بدون المعلومات السياحية
                tourism_info = {}

        # إنشاء الرحلة مع المعلومات السياحية
        trip = Trip.objects.create(
            user=user,
            caption=caption,
            location=location,
            country=country,
            city=city,
            tourism_info=tourism_info
        )

        for image in images:
            TripImage.objects.create(trip=trip, image=image)

        for video in videos:
            TripVideo.objects.create(trip=trip, video=video)

        for tag_name in tags:
            tag, _ = TripTag.objects.get_or_create(trip=trip, tripTag=tag_name)

        serializer = self.get_serializer(trip)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TripListAPIView(generics.ListAPIView):
    queryset = Trip.objects.all().order_by('-created_at')
    serializer_class = TripSerializer

class TripDetailAPIView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    lookup_field = 'id'


class TripUpdateAPIView(generics.UpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'id'

    def perform_update(self, serializer):
        serializer.save()

class TripDeleteAPIView(generics.DestroyAPIView):
    queryset = Trip.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'id'

class TripImageUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)

        # Check ownership
        self.check_object_permissions(request, trip)

        images = request.FILES.getlist('images')
        if not images:
            return Response({'detail': 'No images uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = []
        for image in images:
            trip_image = TripImage.objects.create(trip=trip, image=image)
            uploaded.append(TripImageSerializer(trip_image).data)

        return Response(uploaded, status=status.HTTP_201_CREATED)
    
class TripVideoUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        self.check_object_permissions(request, trip)

        videos = request.FILES.getlist('videos')
        if not videos:
            return Response({'detail': 'No videos uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded = []
        for video in videos:
            trip_video = TripVideo.objects.create(trip=trip, video=video)
            uploaded.append(TripVideoSerializer(trip_video).data)

        return Response(uploaded, status=status.HTTP_201_CREATED)
    
class TripImageDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, image_id):
        image = get_object_or_404(TripImage, id=image_id)

        if image.trip.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        image.delete()
        return Response({'detail': 'Image deleted.'}, status=status.HTTP_204_NO_CONTENT)

class TripVideoDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, video_id):
        video = get_object_or_404(TripVideo, id=video_id)

        if video.trip.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        video.delete()
        return Response({'detail': 'Video deleted.'}, status=status.HTTP_204_NO_CONTENT)

class TripTagAddAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        self.check_object_permissions(request, trip)

        tag_names = request.data.get('tags', [])
        # إذا كانت سلسلة نصية مفصولة بفواصل، حولها لقائمة
        if isinstance(tag_names, str):
            tag_names = [t.strip() for t in tag_names.split(',') if t.strip()]
        if not isinstance(tag_names, list) or not tag_names:
            return Response({'detail': 'Provide a non-empty list of tag names.'}, status=400)

        added = []
        for name in tag_names:
            tag, _ = TripTag.objects.get_or_create(trip=trip, tripTag=name)
            added.append({'id': tag.id, 'tripTag': tag.tripTag})

        return Response(added, status=201)

class TripTagRemoveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def delete(self, request, trip_id, tag_id):
        trip = get_object_or_404(Trip, id=trip_id)
        self.check_object_permissions(request, trip)

        tag = get_object_or_404(TripTag, id=tag_id)
        tag.delete()
        return Response({'detail': f'Tag "{tag.tripTag}" removed.'}, status=204)

class TripTagListForTripAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        tags = trip.tags.all()
        serializer = TripTagSerializer(tags, many=True)
        return Response(serializer.data)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TagTripsView(generics.ListAPIView):
    """عرض جميع الرحلات التي تحتوي على تاج معين"""
    serializer_class = TripSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        tag_name = self.kwargs.get('tag_name')

        # البحث عن الرحلات التي تحتوي على التاج
        return Trip.objects.filter(
            tags__tripTag__iexact=tag_name
        ).select_related('user').prefetch_related(
            'images', 'videos', 'tags', 'likes', 'comments', 'saves'
        ).annotate(
            likes_count=Count('likes')
        ).order_by('-created_at').distinct()

    def get(self, request, *args, **kwargs):
        tag_name = self.kwargs.get('tag_name')

        # التحقق من وجود التاج
        if not TripTag.objects.filter(tripTag__iexact=tag_name).exists():
            return Response({
                'error': f'لا توجد رحلات بالتاج "{tag_name}"'
            }, status=status.HTTP_404_NOT_FOUND)

        # إحصائيات التاج
        trips_count = self.get_queryset().count()

        response = super().get(request, *args, **kwargs)

        # إضافة معلومات التاج للاستجابة
        if hasattr(response, 'data') and isinstance(response.data, dict):
            response.data['tag_info'] = {
                'tag_name': tag_name,
                'trips_count': trips_count
            }

        return response

