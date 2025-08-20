# trip/serializers.py

from rest_framework import serializers
from .models import Trip, TripImage, TripVideo, TripTag

class TripImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripImage
        fields = ['id', 'image']

class TripVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripVideo
        fields = ['id', 'video']

class TripTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripTag
        fields = ['id', 'tripTag']

class TripSerializer(serializers.ModelSerializer):
    images = TripImageSerializer(many=True, read_only=True)
    videos = TripVideoSerializer(many=True, read_only=True)
    tags = TripTagSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'user', 'caption', 'location',
            'country', 'city', 'tourism_info',  # الحقول الجديدة للمعلومات السياحية
            'created_at', 'updated_at',
            'images', 'videos', 'tags',
        ]
