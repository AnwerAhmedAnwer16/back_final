import os
from django.core.exceptions import ValidationError

def validate_image_file_extension(file):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError('Unsupported image file extension.')

def validate_video_file_extension(file):
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError('Unsupported video file extension.')
