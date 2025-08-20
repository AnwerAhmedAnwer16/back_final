
from django.db import models
from django.conf import settings
from .validators import validate_image_file_extension, validate_video_file_extension


def trip_image_path(instance, filename):
    return f'trips/{instance.trip.id}/images/{filename}'

def trip_video_path(instance, filename):
    return f'trips/{instance.trip.id}/videos/{filename}'

class Trip(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trips'
    )
    caption = models.TextField(blank=True)
    location = models.CharField(max_length=255)

    # معلومات سياحية مدعومة بالذكاء الاصطناعي
    country = models.CharField(max_length=100, blank=True, help_text="اسم الدولة")
    city = models.CharField(max_length=100, blank=True, help_text="اسم المدينة")
    tourism_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="معلومات سياحية شاملة من AI"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption or f"رحلة في {self.location}"

class TripImage(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to=trip_image_path,
        validators=[validate_image_file_extension]
    )

class TripVideo(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    video = models.FileField(
        upload_to=trip_video_path,
        validators=[validate_video_file_extension]
    )

class TripTag(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='tags'
    )
    tripTag = models.CharField(max_length=50, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['tripTag']),
            models.Index(fields=['trip', 'tripTag']),
        ]

    def __str__(self):
        return f"{self.tripTag} - {self.trip.id}"
