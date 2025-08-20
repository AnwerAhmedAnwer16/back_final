from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import SubscriptionPlan, Payment, User
from .services import PayMobService, SubscriptionService

User = get_user_model()


class UserSubscriptionModelTest(TestCase):
    """اختبار نموذج المستخدم والاشتراكات"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_user_default_subscription(self):
        """اختبار الاشتراك الافتراضي"""
        self.assertEqual(self.user.subscription_plan, 'free')
        self.assertFalse(self.user.is_subscription_active)
        self.assertFalse(self.user.has_verified_badge)
        self.assertEqual(self.user.subscription_days_remaining, 0)
    
    def test_active_subscription(self):
        """اختبار الاشتراك النشط"""
        self.user.subscription_plan = 'premium'
        self.user.subscription_start_date = timezone.now()
        self.user.subscription_end_date = timezone.now() + timedelta(days=30)
        self.user.save()
        
        self.assertTrue(self.user.is_subscription_active)
        self.assertTrue(self.user.has_verified_badge)
        self.assertGreater(self.user.subscription_days_remaining, 0)
    
    def test_expired_subscription(self):
        """اختبار الاشتراك المنتهي"""
        self.user.subscription_plan = 'premium'
        self.user.subscription_start_date = timezone.now() - timedelta(days=60)
        self.user.subscription_end_date = timezone.now() - timedelta(days=30)
        self.user.save()
        
        self.assertFalse(self.user.is_subscription_active)
        self.assertFalse(self.user.has_verified_badge)
        self.assertEqual(self.user.subscription_days_remaining, 0)


class SubscriptionPlanModelTest(TestCase):
    """اختبار نموذج خطط الاشتراك"""
    
    def test_create_subscription_plan(self):
        """اختبار إنشاء خطة اشتراك"""
        plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            plan_type='premium',
            duration='monthly',
            price=99.00,
            currency='EGP',
            description='Premium features for one month',
            features=['Verified badge', 'Priority support']
        )
        
        self.assertEqual(plan.name, 'Premium Monthly')
        self.assertEqual(plan.plan_type, 'premium')
        self.assertEqual(plan.duration, 'monthly')
        self.assertEqual(plan.price, 99.00)
        self.assertTrue(plan.is_active)


class PaymentModelTest(TestCase):
    """اختبار نموذج المدفوعات"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            plan_type='premium',
            duration='monthly',
            price=99.00
        )
    
    def test_create_payment(self):
        """اختبار إنشاء دفعة"""
        payment = Payment.objects.create(
            user=self.user,
            subscription_plan=self.plan,
            amount=self.plan.price,
            currency='EGP'
        )
        
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.subscription_plan, self.plan)
        self.assertEqual(payment.amount, 99.00)
        self.assertEqual(payment.status, 'pending')


class SubscriptionServiceTest(TestCase):
    """اختبار خدمة الاشتراكات"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            plan_type='premium',
            duration='monthly',
            price=99.00
        )
    
    def test_get_active_plans(self):
        """اختبار الحصول على الخطط النشطة"""
        plans = SubscriptionService.get_active_plans()
        self.assertIn(self.plan, plans)
    
    def test_get_user_subscription_status(self):
        """اختبار الحصول على حالة اشتراك المستخدم"""
        status = SubscriptionService.get_user_subscription_status(self.user)
        
        self.assertEqual(status['plan'], 'free')
        self.assertFalse(status['is_active'])
        self.assertFalse(status['has_verified_badge'])
    
    def test_check_expired_subscriptions(self):
        """اختبار فحص الاشتراكات المنتهية"""
        # إنشاء مستخدم باشتراك منتهي
        expired_user = User.objects.create_user(
            email='expired@example.com',
            username='expireduser',
            password='testpass123'
        )
        expired_user.subscription_plan = 'premium'
        expired_user.subscription_start_date = timezone.now() - timedelta(days=60)
        expired_user.subscription_end_date = timezone.now() - timedelta(days=30)
        expired_user.save()
        
        expired_count = SubscriptionService.check_expired_subscriptions()
        
        # تحديث البيانات من قاعدة البيانات
        expired_user.refresh_from_db()
        
        self.assertEqual(expired_count, 1)
        self.assertEqual(expired_user.subscription_plan, 'free')


class SubscriptionAPITest(APITestCase):
    """اختبار APIs الاشتراكات"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            plan_type='premium',
            duration='monthly',
            price=99.00
        )
    
    def test_subscription_plans_list(self):
        """اختبار عرض قائمة خطط الاشتراك"""
        url = '/api/accounts/subscription-plans/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Premium Monthly')
    
    def test_subscription_status_authenticated(self):
        """اختبار عرض حالة الاشتراك للمستخدم المسجل"""
        self.client.force_authenticate(user=self.user)
        url = '/api/accounts/subscription-status/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan'], 'free')
        self.assertFalse(response.data['is_active'])
    
    def test_subscription_status_unauthenticated(self):
        """اختبار عرض حالة الاشتراك للمستخدم غير المسجل"""
        url = '/api/accounts/subscription-status/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('accounts.services.PayMobService.process_subscription_payment')
    def test_create_subscription_success(self, mock_payment):
        """اختبار إنشاء اشتراك بنجاح"""
        mock_payment.return_value = {
            'payment_id': 1,
            'iframe_url': 'https://test.com/iframe',
            'order_id': '12345'
        }
        
        self.client.force_authenticate(user=self.user)
        url = '/api/accounts/create-subscription/'
        data = {'subscription_plan_id': self.plan.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('iframe_url', response.data)
    
    def test_create_subscription_with_active_subscription(self):
        """اختبار إنشاء اشتراك مع وجود اشتراك نشط"""
        # تفعيل اشتراك للمستخدم
        self.user.subscription_plan = 'premium'
        self.user.subscription_start_date = timezone.now()
        self.user.subscription_end_date = timezone.now() + timedelta(days=30)
        self.user.save()
        
        self.client.force_authenticate(user=self.user)
        url = '/api/accounts/create-subscription/'
        data = {'subscription_plan_id': self.plan.id}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already have an active subscription', response.data['error'])
