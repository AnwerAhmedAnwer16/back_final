from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from unittest.mock import patch, MagicMock
from accounts.models import User, Profile, SubscriptionPlan, Payment
from accounts.services import PayMobService
import json

User = get_user_model()


class ComprehensiveAccountsEndpointsTest(APITestCase):
    """تيست شامل لجميع endpoints في موديول accounts"""
    
    def setUp(self):
        """إعداد البيانات الأساسية للتيست"""
        self.client = APIClient()
        
        # إنشاء مستخدم للتيست
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            is_verified=True
        )
        
        # إنشاء مستخدم غير مفعل
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified',
            password='TestPass123!',
            is_verified=False
        )
        
        # إنشاء خطة اشتراك
        self.subscription_plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            plan_type='premium',
            duration='monthly',
            price=99.00,
            currency='EGP',
            description='Premium features',
            features=['Verified badge', 'Priority support'],
            is_active=True
        )
        
        # إنشاء دفعة للتيست
        self.payment = Payment.objects.create(
            user=self.user,
            subscription_plan=self.subscription_plan,
            amount=99.00,
            currency='EGP',
            status='pending',
            paymob_order_id='12345'
        )

    def test_01_register_endpoint(self):
        """تيست endpoint التسجيل"""
        url = reverse('accounts:register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_02_login_endpoint(self):
        """تيست endpoint تسجيل الدخول"""
        url = reverse('accounts:login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_03_logout_endpoint(self):
        """تيست endpoint تسجيل الخروج"""
        # تسجيل الدخول أولاً
        login_url = reverse('accounts:login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # تسجيل الخروج
        url = reverse('accounts:logout')
        data = {'refresh_token': refresh_token}
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_04_token_refresh_endpoint(self):
        """تيست endpoint تحديث التوكن"""
        # تسجيل الدخول أولاً
        login_url = reverse('accounts:login')
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # تحديث التوكن
        url = reverse('accounts:token_refresh')
        data = {'refresh': refresh_token}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_05_verify_email_endpoint(self):
        """تيست endpoint تفعيل الإيميل"""
        # إنشاء توكن تفعيل
        token = default_token_generator.make_token(self.unverified_user)
        uid = urlsafe_base64_encode(force_bytes(self.unverified_user.pk))
        
        url = reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # التحقق من تفعيل المستخدم
        self.unverified_user.refresh_from_db()
        self.assertTrue(self.unverified_user.is_verified)

    def test_06_check_verification_endpoint(self):
        """تيست endpoint فحص توكن التفعيل"""
        # إنشاء توكن تفعيل
        token = default_token_generator.make_token(self.unverified_user)
        uid = urlsafe_base64_encode(force_bytes(self.unverified_user.pk))
        
        url = reverse('accounts:check_verification', kwargs={'uidb64': uid, 'token': token})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_valid', response.data)
        self.assertTrue(response.data['is_valid'])

    def test_07_generate_verification_link_endpoint(self):
        """تيست endpoint إنشاء رابط التفعيل"""
        url = reverse('accounts:generate_verification_link')
        data = {'email': 'unverified@example.com'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('verification_link', response.data)
        self.assertIn('token_info', response.data)

    def test_08_resend_verification_endpoint(self):
        """تيست endpoint إعادة إرسال رابط التفعيل"""
        url = reverse('accounts:resend_verification')
        data = {'email': 'unverified@example.com'}
        
        with patch('accounts.views.send_mail') as mock_send_mail:
            mock_send_mail.return_value = True
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_09_password_reset_endpoint(self):
        """تيست endpoint طلب إعادة تعيين كلمة المرور"""
        url = reverse('accounts:password_reset')
        data = {'email': 'test@example.com'}
        
        with patch('accounts.views.send_mail') as mock_send_mail:
            mock_send_mail.return_value = True
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_10_password_reset_confirm_endpoint(self):
        """تيست endpoint تأكيد إعادة تعيين كلمة المرور"""
        # إنشاء توكن إعادة تعيين
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        data = {
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_11_change_password_endpoint(self):
        """تيست endpoint تغيير كلمة المرور"""
        url = reverse('accounts:change_password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_12_password_strength_check_endpoint(self):
        """تيست endpoint فحص قوة كلمة المرور"""
        url = reverse('accounts:password_strength_check')
        data = {'password': 'TestPassword123!'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('strength', response.data)
        self.assertIn('is_valid', response.data)

    def test_13_password_requirements_endpoint(self):
        """تيست endpoint متطلبات كلمة المرور"""
        url = reverse('accounts:password_requirements')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('requirements', response.data)
        self.assertIn('description', response.data)

    def test_14_validate_password_endpoint(self):
        """تيست endpoint التحقق من كلمة المرور"""
        url = reverse('accounts:validate_password')
        data = {'password': 'ValidPassword123!'}
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_valid', response.data)
        self.assertIn('strength', response.data)

    def test_15_user_profile_endpoint(self):
        """تيست endpoint بروفايل المستخدم"""
        url = reverse('accounts:user_profile')
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['username'], self.user.username)

    def test_16_profile_details_endpoint(self):
        """تيست endpoint تفاصيل البروفايل"""
        url = reverse('accounts:profile_details')
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)

    def test_17_public_user_profile_endpoint(self):
        """تيست endpoint البروفايل العام للمستخدم"""
        url = reverse('accounts:public_user_profile', kwargs={'id': self.user.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertIn('profile', response.data)

    def test_18_subscription_plans_endpoint(self):
        """تيست endpoint قائمة خطط الاشتراك"""
        url = reverse('accounts:subscription_plans')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Premium Monthly')
        self.assertEqual(response.data[0]['price'], '99.00')

    @patch('accounts.services.PayMobService.process_subscription_payment')
    def test_19_create_subscription_endpoint(self, mock_payment):
        """تيست endpoint إنشاء اشتراك"""
        mock_payment.return_value = {
            'payment_id': 1,
            'iframe_url': 'https://test.com/iframe',
            'order_id': '12345'
        }

        url = reverse('accounts:create_subscription')
        data = {'subscription_plan_id': self.subscription_plan.id}

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('iframe_url', response.data)
        self.assertIn('payment_id', response.data)
        self.assertIn('order_id', response.data)

    def test_20_subscription_status_endpoint(self):
        """تيست endpoint حالة الاشتراك"""
        url = reverse('accounts:subscription_status')

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_active', response.data)
        self.assertIn('plan', response.data)

    def test_21_payment_history_endpoint(self):
        """تيست endpoint تاريخ المدفوعات"""
        url = reverse('accounts:payment_history')

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '99.00')

    def test_22_cancel_subscription_endpoint(self):
        """تيست endpoint إلغاء الاشتراك"""
        # تعيين اشتراك نشط للمستخدم
        from django.utils import timezone
        from datetime import timedelta

        self.user.subscription_plan = 'premium'
        self.user.subscription_start_date = timezone.now()
        self.user.subscription_end_date = timezone.now() + timedelta(days=30)
        self.user.save()

        url = reverse('accounts:cancel_subscription')

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # التحقق من إلغاء الاشتراك
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscription_plan, 'free')

    def test_23_payment_status_endpoint(self):
        """تيست endpoint حالة الدفع"""
        url = reverse('accounts:payment_status', kwargs={'payment_id': self.payment.id})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.payment.id)
        self.assertEqual(response.data['status'], 'pending')

    def test_24_paymob_webhook_endpoint(self):
        """تيست endpoint PayMob webhook"""
        url = reverse('accounts:paymob_webhook')
        webhook_data = {
            'id': 'transaction_123',
            'success': True,
            'order': {
                'id': '12345'
            }
        }

        with patch('accounts.services.PayMobService.handle_successful_payment') as mock_handle:
            mock_handle.return_value = True
            response = self.client.post(url, webhook_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_25_invalid_endpoints_error_handling(self):
        """تيست معالجة الأخطاء للـ endpoints"""

        # تيست تسجيل دخول بكلمة مرور خاطئة
        login_url = reverse('accounts:login')
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # تيست الوصول لـ endpoint محمي بدون authentication
        profile_url = reverse('accounts:user_profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # تيست إنشاء اشتراك بدون plan_id
        subscription_url = reverse('accounts:create_subscription')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(subscription_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_26_edge_cases(self):
        """تيست الحالات الاستثنائية"""

        # تيست تفعيل إيميل بتوكن خاطئ
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        verify_url = reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': 'invalid_token'})
        response = self.client.post(verify_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # تيست إعادة تعيين كلمة مرور لمستخدم غير موجود
        reset_url = reverse('accounts:password_reset')
        data = {'email': 'nonexistent@example.com'}
        with patch('accounts.views.send_mail'):
            response = self.client.post(reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # تيست الوصول لبروفايل مستخدم غير موجود
        public_profile_url = reverse('accounts:public_user_profile', kwargs={'id': 99999})
        response = self.client.get(public_profile_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_27_data_validation(self):
        """تيست التحقق من صحة البيانات"""

        # تيست تسجيل مستخدم بإيميل مكرر
        register_url = reverse('accounts:register')
        data = {
            'email': 'test@example.com',  # إيميل موجود بالفعل
            'username': 'newuser2',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!'
        }
        response = self.client.post(register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # تيست تغيير كلمة مرور بكلمة مرور قديمة خاطئة
        change_password_url = reverse('accounts:change_password')
        data = {
            'old_password': 'WrongOldPassword',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_28_permissions_and_authentication(self):
        """تيست الصلاحيات والمصادقة"""

        # تيست الوصول لحالة الاشتراك بدون مصادقة
        subscription_status_url = reverse('accounts:subscription_status')
        response = self.client.get(subscription_status_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # تيست الوصول لتاريخ المدفوعات بدون مصادقة
        payment_history_url = reverse('accounts:payment_history')
        response = self.client.get(payment_history_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # تيست الوصول لدفعة مستخدم آخر
        other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='TestPass123!'
        )
        other_payment = Payment.objects.create(
            user=other_user,
            subscription_plan=self.subscription_plan,
            amount=99.00,
            currency='EGP',
            status='pending'
        )

        payment_status_url = reverse('accounts:payment_status', kwargs={'payment_id': other_payment.id})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(payment_status_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        """تنظيف البيانات بعد كل تيست"""
        User.objects.all().delete()
        SubscriptionPlan.objects.all().delete()
        Payment.objects.all().delete()
