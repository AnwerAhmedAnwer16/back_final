
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAPITests(APITestCase):
    def test_google_oauth2_login_url(self):
        url = '/api/accounts/google-oauth2-login-url/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_url', response.data)

    def test_google_login_missing_token(self):
        url = '/api/accounts/google-login/'
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.profile_url = reverse('accounts:user_profile')
        self.email = 'testuser@example.com'
        self.password = 'TestPass123'
        # لا تنشئ مستخدم مسبقاً بنفس بيانات المستخدم الذي سيتم تسجيله في اختبار التسجيل
        self.user = User.objects.create_user(email=self.email, password=self.password, is_active=True)

    def test_register(self):
        # استخدم بيانات مستخدم غير موجود مسبقاً
        data = {
            'email': 'uniqueuser@example.com',
            'password': 'UniquePass123',
            'username': 'uniqueuser'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data['user'])

    def test_login(self):
        data = {
            'email': self.email,
            'password': self.password
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.email)

    def test_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordValidationTests(APITestCase):
    """اختبارات validation كلمة المرور"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='OldPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_password_strength_check_endpoint(self):
        """اختبار endpoint فحص قوة كلمة المرور"""
        url = reverse('accounts:password_strength_check')

        # كلمة مرور ضعيفة
        response = self.client.post(url, {'password': '123456'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])

        # كلمة مرور قوية
        response = self.client.post(url, {'password': 'MyPass123!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])

    def test_password_requirements_endpoint(self):
        """اختبار endpoint متطلبات كلمة المرور"""
        url = reverse('accounts:password_requirements')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('requirements', response.data)
        self.assertIn('description', response.data)

    def test_change_password_with_validation(self):
        """اختبار تغيير كلمة المرور مع validation"""
        url = reverse('accounts:change_password')

        # كلمة مرور جديدة ضعيفة
        response = self.client.post(url, {
            'old_password': 'OldPass123!',
            'new_password': '123',
            'new_password_confirm': '123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # كلمة مرور جديدة قوية
        response = self.client.post(url, {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_with_password_validation(self):
        """اختبار التسجيل مع validation كلمة المرور"""
        url = reverse('accounts:register')

        # إلغاء المصادقة للتسجيل
        self.client.force_authenticate(user=None)

        # كلمة مرور ضعيفة
        response = self.client.post(url, {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': '123',
            'password_confirm': '123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # كلمة مرور قوية
        response = self.client.post(url, {
            'email': 'newuser2@example.com',
            'username': 'newuser2',
            'password': 'MyPass123!',
            'password_confirm': 'MyPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
