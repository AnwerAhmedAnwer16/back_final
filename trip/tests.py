
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Trip, TripTag
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class TripAPITests(APITestCase):
    def test_upload_image_no_auth(self):
        self.client.force_authenticate(user=None)
        trip = Trip.objects.create(user=self.user, caption='No Auth', location='Cairo')
        url = f'/api/trip/{trip.id}/images/'
        image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        response = self.client.post(url, {'images': [image]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_image_not_owner(self):
        other_user = User.objects.create_user(email='other2@example.com', password='OtherPass123', is_active=True, is_verified=True)
        trip = Trip.objects.create(user=other_user, caption='Not Owner', location='Cairo')
        image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        img_obj = trip.images.create(image=image)
        url = f'/api/trip/images/{img_obj.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_multiple_images(self):
        trip = Trip.objects.create(user=self.user, caption='Multi Images', location='Cairo')
        url = f'/api/trip/{trip.id}/images/'
        image1 = SimpleUploadedFile('test1.jpg', b'file_content1', content_type='image/jpeg')
        image2 = SimpleUploadedFile('test2.jpg', b'file_content2', content_type='image/jpeg')
        response = self.client.post(url, {'images': [image1, image2]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

    def test_upload_multiple_videos(self):
        trip = Trip.objects.create(user=self.user, caption='Multi Videos', location='Cairo')
        url = f'/api/trip/{trip.id}/videos/'
        video1 = SimpleUploadedFile('test1.mp4', b'file_content1', content_type='video/mp4')
        video2 = SimpleUploadedFile('test2.mp4', b'file_content2', content_type='video/mp4')
        response = self.client.post(url, {'videos': [video1, video2]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

    def test_trip_tag_list_endpoint(self):
        trip = Trip.objects.create(user=self.user, caption='TagList', location='Cairo')
        TripTag.objects.create(trip=trip, tripTag='adventure')
        TripTag.objects.create(trip=trip, tripTag='nature')
        url = f'/api/trip/{trip.id}/tags/list/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(tag['tripTag'] == 'adventure' for tag in response.data))
        self.assertTrue(any(tag['tripTag'] == 'nature' for tag in response.data))

    def test_delete_nonexistent_trip(self):
        url = f'/api/trip/99999/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_upload_image(self):
        trip = Trip.objects.create(user=self.user, caption='Upload Image', location='Cairo')
        url = f'/api/trip/{trip.id}/images/'
        image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        response = self.client.post(url, {'images': [image]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_video(self):
        trip = Trip.objects.create(user=self.user, caption='Upload Video', location='Cairo')
        url = f'/api/trip/{trip.id}/videos/'
        video = SimpleUploadedFile('test.mp4', b'file_content', content_type='video/mp4')
        response = self.client.post(url, {'videos': [video]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_image(self):
        trip = Trip.objects.create(user=self.user, caption='Delete Image', location='Cairo')
        image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        img_obj = trip.images.create(image=image)
        url = f'/api/trip/images/{img_obj.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_video(self):
        trip = Trip.objects.create(user=self.user, caption='Delete Video', location='Cairo')
        video = SimpleUploadedFile('test.mp4', b'file_content', content_type='video/mp4')
        vid_obj = trip.videos.create(video=video)
        url = f'/api/trip/videos/{vid_obj.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_owner_protection_on_delete(self):
        other_user = User.objects.create_user(email='other@example.com', password='OtherPass123', is_active=True, is_verified=True)
        trip = Trip.objects.create(user=other_user, caption='Protected Trip', location='Cairo')
        url = f'/api/trip/{trip.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def setUp(self):
        self.user = User.objects.create_user(email='tripuser@example.com', password='TripPass123', is_active=True, is_verified=True)
        self.client.force_authenticate(user=self.user)
        self.create_url = '/api/trip/create/'
        self.list_url = '/api/trip/'

    def test_create_trip_without_files(self):
        data = {
            'caption': 'My Trip',
            'location': 'Cairo',
            'tags': ['adventure']
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_trip_with_image(self):
        image = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
        data = {
            'caption': 'Trip with image',
            'location': 'Alex',
            'tags': ['nature'],
            'images': [image]
        }
        response = self.client.post(self.create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('caption', response.data)

    def test_trip_delete(self):
        trip = Trip.objects.create(user=self.user, caption='Delete Trip', location='Giza')
        url = f'/api/trip/{trip.id}/delete/'
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])

    def test_trip_tag_add_and_remove(self):
        trip = Trip.objects.create(user=self.user, caption='Tag Trip', location='Giza')
        add_url = f'/api/trip/{trip.id}/tags/'
        data = {'tags': ['fun']}
        response = self.client.post(add_url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        tag = TripTag.objects.filter(trip=trip, tripTag='fun').first()
        remove_url = f'/api/trip/{trip.id}/tags/{tag.id}/'
        response = self.client.delete(remove_url)
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])

    def test_trip_tag_list(self):
        trip = Trip.objects.create(user=self.user, caption='TagList Trip', location='Giza')
        url = f'/api/trip/{trip.id}/tags/list/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_trip(self):
        data = {
            'caption': 'My Trip',
            'location': 'Cairo',
            'tags': ['adventure']
        }
        # يجب رفع صورة أو فيديو، هنا نختبر بدون ملفات للتأكد من ظهور رسالة الخطأ
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_list_trips(self):
        Trip.objects.create(user=self.user, caption='Test Trip', location='Alex')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_trip_detail(self):
        trip = Trip.objects.create(user=self.user, caption='Detail Trip', location='Giza')
        url = f'/api/trip/{trip.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['caption'], 'Detail Trip')
