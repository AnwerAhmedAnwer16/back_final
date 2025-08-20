
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class InteractionsEndpointsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testint@example.com', password='TestPass123', is_active=True, is_verified=True)
        self.client.force_authenticate(user=self.user)
        from trip.models import Trip
        self.trip = Trip.objects.create(user=self.user, caption='Test Trip', location='Test')
        self.other_user = User.objects.create_user(email='otherint@example.com', password='OtherPass123', is_active=True, is_verified=True)

    def test_follow_user(self):
        url = '/api/interactions/follow/'
        response = self.client.post(url, {'user_id': self.user.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_unfollow_user(self):
        # متابعة المستخدم أولاً
        follow_url = '/api/interactions/follow/'
        self.client.post(follow_url, {'user_id': self.other_user.id}, format='json')
        url = '/api/interactions/unfollow/'
        response = self.client.delete(url, {'user_id': self.other_user.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_followers_list(self):
        url = f'/api/interactions/followers/{self.user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_following_list(self):
        url = f'/api/interactions/following/{self.user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_trip(self):
        url = '/api/interactions/like/'
        response = self.client.post(url, {'trip_id': 1}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_unlike_trip(self):
        # عمل لايك أولاً
        like_url = '/api/interactions/like/'
        self.client.post(like_url, {'trip_id': self.trip.id}, format='json')
        url = '/api/interactions/unlike/'
        response = self.client.delete(url, {'trip_id': self.trip.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_trip_likes_list(self):
        url = '/api/interactions/likes/1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment(self):
        url = '/api/interactions/comment/'
        response = self.client.post(url, {'trip_id': 1, 'text': 'test'}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_trip_comments_list(self):
        url = '/api/interactions/comments/1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        url = '/api/interactions/comment/1/'
        response = self.client.put(url, {'text': 'updated'}, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_delete_comment(self):
        url = '/api/interactions/comment/1/delete/'
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_save_trip(self):
        url = '/api/interactions/save/'
        response = self.client.post(url, {'trip_id': 1}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_unsave_trip(self):
        # حفظ الرحلة أولاً
        save_url = '/api/interactions/save/'
        self.client.post(save_url, {'trip_id': self.trip.id}, format='json')
        url = '/api/interactions/unsave/'
        response = self.client.delete(url, {'trip_id': self.trip.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_saved_trips_list(self):
        url = '/api/interactions/saved/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_trip(self):
        url = '/api/interactions/share/'
        response = self.client.post(url, {'trip_id': 1}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_feed(self):
        url = '/api/interactions/feed/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_explore(self):
        url = '/api/interactions/explore/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notifications_list(self):
        url = '/api/interactions/notifications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_read(self):
        url = '/api/interactions/notifications/1/read/'
        response = self.client.post(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_mark_all_notifications_read(self):
        url = '/api/interactions/notifications/read-all/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_stats(self):
        url = f'/api/interactions/stats/user/{self.user.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trip_stats(self):
        url = f'/api/interactions/stats/trip/{self.trip.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # اختبارات الـ endpoints الجديدة للإشعارات
    def test_unread_notifications_count(self):
        url = '/api/interactions/notifications/unread-count/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)

    def test_recent_notifications(self):
        url = '/api/interactions/notifications/recent/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications', response.data)

    def test_notification_settings(self):
        url = '/api/interactions/notifications/settings/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notification_settings(self):
        url = '/api/interactions/notifications/settings/update/'
        response = self.client.post(url, {
            'likes_enabled': True,
            'comments_enabled': False
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_read_realtime(self):
        # إنشاء إشعار للاختبار
        from .models import Notification
        notification = Notification.objects.create(
            recipient=self.user,
            sender=self.other_user,
            notification_type='follow'
        )

        url = f'/api/interactions/notifications/{notification.id}/read-realtime/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_notification(self):
        # إنشاء إشعار للاختبار
        from .models import Notification
        notification = Notification.objects.create(
            recipient=self.user,
            sender=self.other_user,
            notification_type='follow'
        )

        url = f'/api/interactions/notifications/{notification.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationUtilsTest(APITestCase):
    """اختبارات utility functions للإشعارات"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            is_active=True,
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            is_active=True,
            is_verified=True
        )
        from trip.models import Trip
        self.trip = Trip.objects.create(
            user=self.user1,
            caption='Test Trip',
            location='Test Location'
        )

    def test_get_user_unread_count(self):
        """اختبار الحصول على عدد الإشعارات غير المقروءة"""
        from .utils import get_user_unread_count
        from .models import Notification

        # إنشاء إشعارات
        Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='follow'
        )
        Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='like',
            trip=self.trip,
            is_read=True
        )

        unread_count = get_user_unread_count(self.user1.id)
        self.assertEqual(unread_count, 1)

    def test_mark_notification_as_read_and_update(self):
        """اختبار تحديد إشعار كمقروء مع تحديث العدد"""
        from .utils import mark_notification_as_read_and_update
        from .models import Notification

        notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='follow'
        )

        success = mark_notification_as_read_and_update(notification.id, self.user1.id)
        self.assertTrue(success)

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_notifications_as_read_and_update(self):
        """اختبار تحديد جميع الإشعارات كمقروءة"""
        from .utils import mark_all_notifications_as_read_and_update
        from .models import Notification

        # إنشاء عدة إشعارات
        for i in range(3):
            Notification.objects.create(
                recipient=self.user1,
                sender=self.user2,
                notification_type='follow'
            )

        count = mark_all_notifications_as_read_and_update(self.user1.id)
        self.assertEqual(count, 3)


class NotificationSignalsTest(APITestCase):
    """اختبارات signals الإشعارات"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            is_active=True,
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            is_active=True,
            is_verified=True
        )
        from trip.models import Trip
        self.trip = Trip.objects.create(
            user=self.user1,
            caption='Test Trip',
            location='Test Location'
        )

    def test_follow_notification_signal(self):
        """اختبار إنشاء إشعار عند المتابعة"""
        from .models import Follow, Notification

        # إنشاء متابعة
        Follow.objects.create(follower=self.user2, following=self.user1)

        # التحقق من إنشاء الإشعار
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user2,
            notification_type='follow'
        ).first()

        self.assertIsNotNone(notification)

    def test_like_notification_signal(self):
        """اختبار إنشاء إشعار عند الإعجاب"""
        from .models import Like, Notification

        # إنشاء إعجاب
        Like.objects.create(user=self.user2, trip=self.trip)

        # التحقق من إنشاء الإشعار
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user2,
            notification_type='like',
            trip=self.trip
        ).first()

        self.assertIsNotNone(notification)

    def test_comment_notification_signal(self):
        """اختبار إنشاء إشعار عند التعليق"""
        from .models import Comment, Notification

        # إنشاء تعليق
        Comment.objects.create(
            user=self.user2,
            trip=self.trip,
            content='Test comment'
        )

        # التحقق من إنشاء الإشعار
        notification = Notification.objects.filter(
            recipient=self.user1,
            sender=self.user2,
            notification_type='comment',
            trip=self.trip
        ).first()

        self.assertIsNotNone(notification)
