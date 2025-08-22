from django.utils import timezone
from django.db.models import Q
from accounts.services import PayMobService
from accounts.models import Payment
from .models import PromotionRequest, ActivePromotion, PromotionCommission, PromotionPlan
import logging

logger = logging.getLogger(__name__)


class PromotionPaymentService:
    """خدمة دفع الترويج"""
    
    def __init__(self):
        self.paymob_service = PayMobService()
    
    def process_promotion_payment(self, user, promotion_plan):
        """معالجة دفع الترويج"""
        try:
            # إنشاء payment record
            payment = Payment.objects.create(
                user=user,
                subscription_plan=None,  # لا نستخدم subscription_plan للترويج
                amount=promotion_plan.price,
                currency=promotion_plan.currency,
                status='pending'
            )
            
            # إنشاء order في PayMob
            order = self.paymob_service.create_order(
                amount=promotion_plan.price,
                currency=promotion_plan.currency
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
            payment_token = self.paymob_service.create_payment_key(
                order_id=order.get('id'),
                amount=promotion_plan.price,
                user_data=user_data,
                currency=promotion_plan.currency
            )
            
            payment.payment_token = payment_token
            payment.save()
            
            # إنشاء iframe URL
            iframe_url = self.paymob_service.get_iframe_url(payment_token)
            
            logger.info(f"Promotion payment initiated for user {user.username}")
            
            return {
                'payment_id': payment.id,
                'iframe_url': iframe_url,
                'payment_token': payment_token,
                'order_id': order.get('id')
            }
            
        except Exception as e:
            logger.error(f"Promotion payment processing failed: {str(e)}")
            if 'payment' in locals():
                payment.status = 'failed'
                payment.save()
            raise
    
    def handle_successful_promotion_payment(self, payment_id, transaction_data=None):
        """معالجة الدفع الناجح للترويج"""
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            
            if transaction_data:
                payment.paymob_transaction_id = transaction_data.get('transaction_id', '')
            
            payment.save()
            
            # البحث عن طلب الترويج المرتبط بهذه الدفعة
            try:
                promotion_request = PromotionRequest.objects.get(payment=payment)
                logger.info(f"Promotion payment completed for request {promotion_request.id}")
                
                # إرسال إشعار لصاحب الرحلة (سيتم تطويره لاحقاً)
                # self._send_promotion_request_notification(promotion_request)
                
                return True
                
            except PromotionRequest.DoesNotExist:
                logger.error(f"No promotion request found for payment {payment_id}")
                return False
            
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error handling successful promotion payment: {str(e)}")
            return False


class PromotionManagementService:
    """خدمة إدارة الترويجات"""
    
    @staticmethod
    def check_expired_promotions():
        """فحص الترويجات المنتهية الصلاحية"""
        expired_promotions = PromotionRequest.objects.filter(
            status='active',
            end_date__lt=timezone.now()
        )
        
        count = 0
        for promotion in expired_promotions:
            promotion.status = 'expired'
            promotion.save()
            
            # إزالة من الترويجات النشطة
            if hasattr(promotion, 'active_promotion'):
                promotion.active_promotion.delete()
            
            count += 1
            logger.info(f"Promotion {promotion.id} expired")
        
        return count
    
    @staticmethod
    def get_active_promotions_for_feed():
        """الحصول على الترويجات النشطة للعرض في الـ feed"""
        return ActivePromotion.objects.filter(
            promotion_request__status='active',
            promotion_request__end_date__gt=timezone.now()
        ).select_related(
            'promotion_request__trip',
            'promotion_request__sponsor',
            'promotion_request__promotion_plan'
        ).order_by('-priority_score')
    
    @staticmethod
    def increment_promotion_views(promotion_request_id):
        """زيادة عدد مشاهدات الترويج"""
        try:
            promotion_request = PromotionRequest.objects.get(id=promotion_request_id)
            promotion_request.views_count += 1
            promotion_request.save(update_fields=['views_count'])
            return True
        except PromotionRequest.DoesNotExist:
            return False
    
    @staticmethod
    def increment_promotion_clicks(promotion_request_id):
        """زيادة عدد نقرات الترويج"""
        try:
            promotion_request = PromotionRequest.objects.get(id=promotion_request_id)
            promotion_request.clicks_count += 1
            promotion_request.save(update_fields=['clicks_count'])
            return True
        except PromotionRequest.DoesNotExist:
            return False
    
    @staticmethod
    def can_user_promote_trip(user, trip):
        """فحص إمكانية المستخدم لترويج رحلة معينة"""
        # التحقق من وجود verified badge
        if not user.has_verified_badge:
            return False, "يجب أن يكون لديك اشتراك نشط للقيام بالترويج"
        
        # التحقق من عدم وجود طلب ترويج نشط
        existing_request = PromotionRequest.objects.filter(
            sponsor=user,
            trip=trip,
            status__in=['pending', 'approved', 'active']
        ).exists()
        
        if existing_request:
            return False, "لديك طلب ترويج نشط لهذه الرحلة بالفعل"
        
        return True, ""
    
    @staticmethod
    def get_promotion_analytics(user, as_sponsor=True):
        """الحصول على تحليلات الترويج"""
        if as_sponsor:
            # إحصائيات كراعي
            requests = PromotionRequest.objects.filter(sponsor=user)
        else:
            # إحصائيات كصاحب رحلة
            requests = PromotionRequest.objects.filter(owner=user)
        
        total_requests = requests.count()
        active_requests = requests.filter(status='active').count()
        completed_requests = requests.filter(status='expired').count()
        
        total_views = sum(req.views_count for req in requests)
        total_clicks = sum(req.clicks_count for req in requests)
        
        click_through_rate = (total_clicks / total_views * 100) if total_views > 0 else 0
        
        return {
            'total_requests': total_requests,
            'active_requests': active_requests,
            'completed_requests': completed_requests,
            'total_views': total_views,
            'total_clicks': total_clicks,
            'click_through_rate': round(click_through_rate, 2)
        }


class PromotionCommissionService:
    """خدمة إدارة عمولات الترويج"""
    
    @staticmethod
    def create_commission(promotion_request):
        """إنشاء عمولة لصاحب الرحلة"""
        commission_amount = promotion_request.promotion_plan.owner_commission_amount
        
        commission = PromotionCommission.objects.create(
            promotion_request=promotion_request,
            owner=promotion_request.owner,
            amount=commission_amount,
            currency=promotion_request.promotion_plan.currency,
            status='pending'
        )
        
        logger.info(f"Commission created: {commission.amount} {commission.currency} for {commission.owner.username}")
        return commission
    
    @staticmethod
    def mark_commission_as_paid(commission_id):
        """تحديد العمولة كمدفوعة"""
        try:
            commission = PromotionCommission.objects.get(id=commission_id)
            commission.status = 'paid'
            commission.paid_at = timezone.now()
            commission.save()
            
            logger.info(f"Commission {commission_id} marked as paid")
            return True
        except PromotionCommission.DoesNotExist:
            logger.error(f"Commission {commission_id} not found")
            return False
    
    @staticmethod
    def get_user_total_earnings(user):
        """الحصول على إجمالي أرباح المستخدم"""
        commissions = PromotionCommission.objects.filter(owner=user)
        
        paid_earnings = commissions.filter(status='paid').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        pending_earnings = commissions.filter(status='pending').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        return {
            'paid_earnings': paid_earnings,
            'pending_earnings': pending_earnings,
            'total_earnings': paid_earnings + pending_earnings
        }
