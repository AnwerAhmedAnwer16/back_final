from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import SubscriptionPlan, Payment, User
from .serializers import (
    SubscriptionPlanSerializer,
    PaymentSerializer,
    CreateSubscriptionSerializer,
    SubscriptionStatusSerializer
)
from .services import PayMobService, SubscriptionService
import logging

logger = logging.getLogger(__name__)


class SubscriptionPlanListView(generics.ListAPIView):
    """عرض قائمة خطط الاشتراك المتاحة"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class CreateSubscriptionView(APIView):
    """إنشاء اشتراك جديد"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CreateSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                subscription_plan_id = serializer.validated_data['subscription_plan_id']
                subscription_plan = get_object_or_404(SubscriptionPlan, id=subscription_plan_id, is_active=True)
                
                # التحقق من أن المستخدم لا يملك اشتراك نشط
                if request.user.is_subscription_active:
                    return Response({
                        'error': 'You already have an active subscription'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # إنشاء عملية الدفع
                paymob_service = PayMobService()
                payment_data = paymob_service.process_subscription_payment(
                    user=request.user,
                    subscription_plan=subscription_plan
                )
                
                return Response({
                    'message': 'Payment initiated successfully',
                    'payment_id': payment_data['payment_id'],
                    'iframe_url': payment_data['iframe_url'],
                    'order_id': payment_data['order_id']
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error creating subscription: {str(e)}")
                return Response({
                    'error': 'Failed to create subscription',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionStatusView(APIView):
    """عرض حالة اشتراك المستخدم"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        subscription_status = SubscriptionService.get_user_subscription_status(request.user)
        serializer = SubscriptionStatusSerializer(subscription_status)
        return Response(serializer.data)


class UserPaymentHistoryView(generics.ListAPIView):
    """عرض تاريخ المدفوعات للمستخدم"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


class PayMobWebhookView(APIView):
    """استقبال إشعارات PayMob"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            webhook_data = request.data
            logger.info(f"PayMob webhook received: {webhook_data}")

            # Verify webhook signature first
            signature = request.META.get('HTTP_X_PAYMOB_SIGNATURE', '')
            if not signature:
                # Try alternative header names
                signature = request.META.get('HTTP_HMAC', '') or request.META.get('HTTP_SIGNATURE', '')

            paymob_service = PayMobService()
            if not paymob_service.verify_webhook_signature(webhook_data, signature):
                logger.error("Webhook signature verification failed")
                return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

            # استخراج معرف الطلب
            order_id = webhook_data.get('order', {}).get('id')
            transaction_id = webhook_data.get('id')
            success = webhook_data.get('success', False)
            transaction_status = webhook_data.get('status', '')

            if not order_id:
                logger.error("Missing order ID in webhook")
                return Response({'error': 'Missing order ID'}, status=status.HTTP_400_BAD_REQUEST)

            # البحث عن الدفعة
            try:
                payment = Payment.objects.get(paymob_order_id=str(order_id))
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for order ID: {order_id}")
                return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

            # Store webhook data for audit
            from .models import PaymentTransaction
            PaymentTransaction.objects.update_or_create(
                payment=payment,
                defaults={
                    'webhook_data': webhook_data,
                    'hmac_signature': signature
                }
            )

            # تحديث حالة الدفعة
            if success and transaction_status.lower() == 'success':
                # تحديد نوع الدفع (اشتراك أم ترويج)
                if payment.subscription_plan:
                    # دفع اشتراك
                    success_result = paymob_service.handle_successful_payment(
                        payment_id=payment.id,
                        transaction_data={'transaction_id': transaction_id}
                    )
                else:
                    # دفع ترويج
                    from promotions.services import PromotionPaymentService
                    promotion_service = PromotionPaymentService()
                    success_result = promotion_service.handle_successful_promotion_payment(
                        payment_id=payment.id,
                        transaction_data={'transaction_id': transaction_id}
                    )

                if success_result:
                    logger.info(f"Payment {payment.id} processed successfully")
                    return Response({'status': 'success'}, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Failed to process payment {payment.id}")
                    return Response({'error': 'Failed to process payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # فشل الدفع أو حالة أخرى
                if transaction_status.lower() in ['failed', 'cancelled', 'declined']:
                    payment.status = 'failed'
                elif transaction_status.lower() == 'pending':
                    payment.status = 'pending'
                else:
                    payment.status = 'failed'  # Default to failed for unknown statuses

                payment.save()
                logger.info(f"Payment {payment.id} status updated to {payment.status}")
                return Response({'status': payment.status}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing PayMob webhook: {str(e)}")
            return Response({'error': 'Webhook processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelSubscriptionView(APIView):
    """إلغاء الاشتراك"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if not user.is_subscription_active:
            return Response({
                'error': 'No active subscription to cancel'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # إلغاء الاشتراك (تحويل إلى free)
            user.subscription_plan = 'free'
            user.subscription_start_date = None
            user.subscription_end_date = None
            user.save()
            
            logger.info(f"Subscription cancelled for user {user.username}")
            
            return Response({
                'message': 'Subscription cancelled successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return Response({
                'error': 'Failed to cancel subscription'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckPaymentStatusView(APIView):
    """فحص حالة الدفع"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_id):
        try:
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")
            return Response({
                'error': 'Failed to check payment status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
