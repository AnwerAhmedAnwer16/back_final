import requests
import json
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Payment, SubscriptionPlan, User
import logging

logger = logging.getLogger(__name__)


class PayMobService:
    """خدمة التعامل مع PayMob API"""
    
    def __init__(self):
        self.api_key = settings.PAYMOB_API_KEY
        self.integration_id = settings.PAYMOB_INTEGRATION_ID
        self.iframe_id = settings.PAYMOB_IFRAME_ID
        self.base_url = settings.PAYMOB_BASE_URL
        self.auth_token = None
    
    def authenticate(self):
        """الحصول على auth token من PayMob"""
        url = f"{self.base_url}/auth/tokens"
        data = {"api_key": self.api_key}
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.auth_token = result.get('token')
            logger.info("PayMob authentication successful")
            return self.auth_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PayMob authentication failed: {str(e)}")
            raise Exception(f"PayMob authentication failed: {str(e)}")
    
    def create_order(self, amount, currency='EGP'):
        """إنشاء order في PayMob"""
        if not self.auth_token:
            self.authenticate()
        
        url = f"{self.base_url}/ecommerce/orders"
        data = {
            "auth_token": self.auth_token,
            "delivery_needed": "false",
            "amount_cents": int(amount * 100),  # تحويل إلى قروش
            "currency": currency,
            "items": []
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"PayMob order created: {result.get('id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PayMob order creation failed: {str(e)}")
            raise Exception(f"PayMob order creation failed: {str(e)}")
    
    def create_payment_key(self, order_id, amount, user_data, currency='EGP'):
        """إنشاء payment key للدفع"""
        if not self.auth_token:
            self.authenticate()
        
        url = f"{self.base_url}/acceptance/payment_keys"
        data = {
            "auth_token": self.auth_token,
            "amount_cents": int(amount * 100),
            "expiration": 3600,  # ساعة واحدة
            "order_id": order_id,
            "billing_data": {
                "apartment": "NA",
                "email": user_data.get('email', ''),
                "floor": "NA",
                "first_name": user_data.get('first_name', ''),
                "street": "NA",
                "building": "NA",
                "phone_number": user_data.get('phone', ''),
                "shipping_method": "NA",
                "postal_code": "NA",
                "city": "NA",
                "country": "EG",
                "last_name": user_data.get('last_name', ''),
                "state": "NA"
            },
            "currency": currency,
            "integration_id": self.integration_id
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            payment_token = result.get('token')
            logger.info(f"PayMob payment key created for order: {order_id}")
            return payment_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PayMob payment key creation failed: {str(e)}")
            raise Exception(f"PayMob payment key creation failed: {str(e)}")
    
    def get_iframe_url(self, payment_token):
        """الحصول على رابط iframe للدفع"""
        return f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_token}"
    
    def verify_webhook_signature(self, data, signature):
        """التحقق من صحة webhook signature"""
        try:
            # PayMob HMAC verification
            # The HMAC key should be stored in settings
            hmac_secret = getattr(settings, 'PAYMOB_HMAC_SECRET', '')

            if not hmac_secret:
                logger.error("PAYMOB_HMAC_SECRET not configured")
                return False

            # Create the string to be hashed according to PayMob documentation
            # Format: amount_cents.currency.delivery_needed.email.first_name.id.integration_id.last_name.order.phone_number
            webhook_data = data

            # Extract required fields for HMAC calculation
            amount_cents = str(webhook_data.get('amount_cents', ''))
            currency = webhook_data.get('currency', '')
            delivery_needed = str(webhook_data.get('delivery_needed', 'false')).lower()
            email = webhook_data.get('email', '')
            first_name = webhook_data.get('first_name', '')
            transaction_id = str(webhook_data.get('id', ''))
            integration_id = str(webhook_data.get('integration_id', ''))
            last_name = webhook_data.get('last_name', '')
            order_id = str(webhook_data.get('order', {}).get('id', ''))
            phone_number = webhook_data.get('phone_number', '')

            # Construct the string according to PayMob specification
            concatenated_string = f"{amount_cents}.{currency}.{delivery_needed}.{email}.{first_name}.{transaction_id}.{integration_id}.{last_name}.{order_id}.{phone_number}"

            # Calculate HMAC
            calculated_hmac = hmac.new(
                hmac_secret.encode('utf-8'),
                concatenated_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()

            # Compare signatures
            is_valid = hmac.compare_digest(calculated_hmac, signature)

            if not is_valid:
                logger.error(f"HMAC verification failed. Expected: {calculated_hmac}, Received: {signature}")
                logger.error(f"Concatenated string: {concatenated_string}")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False

    def inquiry_transaction(self, transaction_id):
        """استعلام عن حالة المعاملة من PayMob"""
        try:
            if not self.auth_token:
                self.authenticate()

            url = f"{self.base_url}/acceptance/transactions/{transaction_id}"
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Transaction inquiry successful for ID: {transaction_id}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Transaction inquiry failed: {str(e)}")
            return None

    def verify_payment_with_paymob(self, payment_id):
        """التحقق من حالة الدفع مع PayMob API"""
        try:
            payment = Payment.objects.get(id=payment_id)

            if not payment.paymob_transaction_id:
                logger.error(f"No PayMob transaction ID for payment {payment_id}")
                return False

            transaction_data = self.inquiry_transaction(payment.paymob_transaction_id)

            if not transaction_data:
                return False

            # Check if transaction is successful
            is_success = transaction_data.get('success', False)
            transaction_status = transaction_data.get('status', '')

            logger.info(f"PayMob verification - Payment {payment_id}: success={is_success}, status={transaction_status}")

            return is_success and transaction_status.lower() == 'success'

        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error verifying payment with PayMob: {str(e)}")
            return False
    
    def process_subscription_payment(self, user, subscription_plan):
        """معالجة دفع الاشتراك"""
        try:
            # إنشاء payment record
            payment = Payment.objects.create(
                user=user,
                subscription_plan=subscription_plan,
                amount=subscription_plan.price,
                currency=subscription_plan.currency,
                status='pending'
            )
            
            # إنشاء order في PayMob
            order = self.create_order(
                amount=subscription_plan.price,
                currency=subscription_plan.currency
            )
            
            payment.paymob_order_id = str(order.get('id'))
            
            # إعداد بيانات المستخدم
            user_data = {
                'email': user.email,
                'first_name': getattr(user.profile, 'first_name', '') or 'User',
                'last_name': getattr(user.profile, 'last_name', '') or 'Name',
                'phone': '+201234567890'  # Default phone number for PayMob
            }
            
            # إنشاء payment key
            payment_token = self.create_payment_key(
                order_id=order.get('id'),
                amount=subscription_plan.price,
                user_data=user_data,
                currency=subscription_plan.currency
            )
            
            payment.payment_token = payment_token
            payment.save()
            
            # إنشاء iframe URL
            iframe_url = self.get_iframe_url(payment_token)
            
            logger.info(f"Subscription payment initiated for user {user.username}")
            
            return {
                'payment_id': payment.id,
                'iframe_url': iframe_url,
                'payment_token': payment_token,
                'order_id': order.get('id')
            }
            
        except Exception as e:
            logger.error(f"Subscription payment processing failed: {str(e)}")
            if 'payment' in locals():
                payment.status = 'failed'
                payment.save()
            raise
    
    def handle_successful_payment(self, payment_id, transaction_data=None):
        """معالجة الدفع الناجح"""
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            
            if transaction_data:
                payment.paymob_transaction_id = transaction_data.get('transaction_id', '')
            
            payment.save()
            
            # تفعيل الاشتراك للمستخدم
            user = payment.user
            subscription_plan = payment.subscription_plan
            
            # حساب تاريخ انتهاء الاشتراك
            start_date = timezone.now()
            if subscription_plan.duration == 'monthly':
                end_date = start_date + timedelta(days=30)
            elif subscription_plan.duration == 'yearly':
                end_date = start_date + timedelta(days=365)
            else:
                end_date = start_date + timedelta(days=30)  # افتراضي
            
            # تحديث بيانات المستخدم
            user.subscription_plan = subscription_plan.plan_type
            user.subscription_start_date = start_date
            user.subscription_end_date = end_date
            user.save()
            
            logger.info(f"Subscription activated for user {user.username}")
            
            return True
            
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error handling successful payment: {str(e)}")
            return False


class SubscriptionService:
    """خدمة إدارة الاشتراكات"""
    
    @staticmethod
    def get_active_plans():
        """الحصول على الخطط النشطة"""
        return SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    @staticmethod
    def check_expired_subscriptions():
        """فحص الاشتراكات المنتهية الصلاحية"""
        expired_users = User.objects.filter(
            subscription_end_date__lt=timezone.now(),
            subscription_plan__in=['premium', 'pro']
        )
        
        for user in expired_users:
            user.subscription_plan = 'free'
            user.subscription_start_date = None
            user.subscription_end_date = None
            user.save()
            logger.info(f"Subscription expired for user {user.username}")
        
        return expired_users.count()

    @staticmethod
    def reconcile_payments():
        """مطابقة المدفوعات مع PayMob"""
        paymob_service = PayMobService()
        pending_payments = Payment.objects.filter(status='pending')

        reconciled_count = 0
        for payment in pending_payments:
            if payment.paymob_transaction_id:
                is_verified = paymob_service.verify_payment_with_paymob(payment.id)
                if is_verified:
                    paymob_service.handle_successful_payment(
                        payment_id=payment.id,
                        transaction_data={'transaction_id': payment.paymob_transaction_id}
                    )
                    reconciled_count += 1
                    logger.info(f"Payment {payment.id} reconciled successfully")

        return reconciled_count

    @staticmethod
    def get_user_subscription_status(user):
        """الحصول على حالة اشتراك المستخدم"""
        return {
            'plan': user.subscription_plan,
            'is_active': user.is_subscription_active,
            'start_date': user.subscription_start_date,
            'end_date': user.subscription_end_date,
            'days_remaining': user.subscription_days_remaining,
            'has_verified_badge': user.has_verified_badge
        }
