from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from .services import PayMobService
import logging

logger = logging.getLogger(__name__)


@shared_task
def retry_failed_payments():
    """إعادة محاولة المدفوعات الفاشلة"""
    # Get payments that are pending for more than 30 minutes
    cutoff_time = timezone.now() - timedelta(minutes=30)
    stale_payments = Payment.objects.filter(
        status='pending',
        created_at__lt=cutoff_time
    )
    
    paymob_service = PayMobService()
    processed_count = 0
    
    for payment in stale_payments:
        if payment.paymob_transaction_id:
            is_verified = paymob_service.verify_payment_with_paymob(payment.id)
            if is_verified:
                paymob_service.handle_successful_payment(
                    payment_id=payment.id,
                    transaction_data={'transaction_id': payment.paymob_transaction_id}
                )
                processed_count += 1
                logger.info(f"Stale payment {payment.id} processed successfully")
            else:
                # Mark as failed if verification fails
                payment.status = 'failed'
                payment.save()
                logger.info(f"Stale payment {payment.id} marked as failed")
    
    return processed_count


@shared_task
def check_expired_subscriptions():
    """فحص الاشتراكات المنتهية الصلاحية"""
    from .services import SubscriptionService
    expired_count = SubscriptionService.check_expired_subscriptions()
    logger.info(f"Processed {expired_count} expired subscriptions")
    return expired_count
