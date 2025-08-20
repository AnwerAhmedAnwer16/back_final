from django.db import models
from django.conf import settings
from django.utils import timezone
from trip.models import Trip
from accounts.models import Payment
from decimal import Decimal

# Create your models here.

class PromotionPlan(models.Model):
    """نموذج خطط الترويج"""
    DURATION_CHOICES = [
        (3, '3 أيام'),
        (7, '7 أيام'),
        (30, '30 يوم'),
    ]

    REACH_MULTIPLIER_CHOICES = [
        ('2x', '2x'),
        ('3x', '3x'),
        ('5x', '5x'),
    ]

    name = models.CharField('اسم الخطة', max_length=100)
    duration_days = models.IntegerField('مدة الترويج بالأيام', choices=DURATION_CHOICES)
    price = models.DecimalField('السعر', max_digits=10, decimal_places=2)
    currency = models.CharField('العملة', max_length=3, default='EGP')
    reach_multiplier = models.CharField('مضاعف الوصول', max_length=10, choices=REACH_MULTIPLIER_CHOICES)
    description = models.TextField('الوصف', blank=True)
    features = models.JSONField('المميزات', default=list, blank=True)
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    class Meta:
        verbose_name = 'خطة ترويج'
        verbose_name_plural = 'خطط الترويج'
        ordering = ['duration_days', 'price']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['duration_days']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.name} - {self.duration_days} أيام"

    @property
    def owner_commission_amount(self):
        """حساب عمولة صاحب الرحلة (10%)"""
        return self.price * Decimal('0.10')

    @property
    def platform_amount(self):
        """حساب مبلغ المنصة (90%)"""
        return self.price * Decimal('0.90')


class PromotionRequest(models.Model):
    """نموذج طلب الترويج"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('active', 'نشط'),
        ('expired', 'منتهي'),
        ('cancelled', 'ملغي'),
    ]

    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sponsored_promotions',
        verbose_name='الراعي'
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='promotion_requests',
        verbose_name='الرحلة'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_promotion_requests',
        verbose_name='صاحب الرحلة'
    )
    promotion_plan = models.ForeignKey(
        PromotionPlan,
        on_delete=models.CASCADE,
        verbose_name='خطة الترويج'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='الدفعة'
    )

    sponsor_message = models.TextField(
        'رسالة الراعي',
        max_length=500,
        blank=True,
        help_text='نبذة عن سبب الترويج (اختياري)'
    )
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # تواريخ مهمة
    created_at = models.DateTimeField('تاريخ الطلب', auto_now_add=True)
    approved_at = models.DateTimeField('تاريخ الموافقة', null=True, blank=True)
    rejected_at = models.DateTimeField('تاريخ الرفض', null=True, blank=True)
    start_date = models.DateTimeField('تاريخ البداية', null=True, blank=True)
    end_date = models.DateTimeField('تاريخ النهاية', null=True, blank=True)

    # إحصائيات
    views_count = models.PositiveIntegerField('عدد المشاهدات', default=0)
    clicks_count = models.PositiveIntegerField('عدد النقرات', default=0)

    class Meta:
        verbose_name = 'طلب ترويج'
        verbose_name_plural = 'طلبات الترويج'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sponsor', 'status']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['trip', 'status']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['status', 'end_date']),
        ]
        constraints = [
            # منع ترويج نفس الرحلة من نفس الراعي في نفس الوقت
            models.UniqueConstraint(
                fields=['sponsor', 'trip'],
                condition=models.Q(status__in=['pending', 'approved', 'active']),
                name='unique_active_promotion_per_sponsor_trip'
            )
        ]

    def __str__(self):
        return f"ترويج {self.trip.id} بواسطة {self.sponsor.username}"

    @property
    def is_active(self):
        """فحص إذا كان الترويج نشط حالياً"""
        if self.status != 'active':
            return False
        if not self.start_date or not self.end_date:
            return False
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def days_remaining(self):
        """الأيام المتبقية في الترويج"""
        if not self.is_active:
            return 0
        remaining = self.end_date - timezone.now()
        return max(0, remaining.days)

    def approve(self):
        """موافقة على طلب الترويج"""
        if self.status == 'pending' and self.payment and self.payment.status == 'completed':
            self.status = 'approved'
            self.approved_at = timezone.now()
            self.save()
            return True
        return False

    def reject(self):
        """رفض طلب الترويج"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.rejected_at = timezone.now()
            self.save()
            return True
        return False

    def activate(self):
        """تفعيل الترويج"""
        if self.status == 'approved':
            self.status = 'active'
            self.start_date = timezone.now()
            self.end_date = self.start_date + timezone.timedelta(days=self.promotion_plan.duration_days)
            self.save()
            return True
        return False


class ActivePromotion(models.Model):
    """نموذج الترويجات النشطة (للاستعلام السريع)"""
    promotion_request = models.OneToOneField(
        PromotionRequest,
        on_delete=models.CASCADE,
        related_name='active_promotion',
        verbose_name='طلب الترويج'
    )
    priority_score = models.IntegerField('نقاط الأولوية', default=0)

    class Meta:
        verbose_name = 'ترويج نشط'
        verbose_name_plural = 'ترويجات نشطة'
        ordering = ['-priority_score']
        indexes = [
            models.Index(fields=['priority_score']),
        ]

    def __str__(self):
        return f"ترويج نشط: {self.promotion_request.trip.id}"

    @property
    def trip(self):
        return self.promotion_request.trip

    @property
    def sponsor(self):
        return self.promotion_request.sponsor

    @property
    def sponsor_message(self):
        return self.promotion_request.sponsor_message


class PromotionCommission(models.Model):
    """نموذج عمولات الترويج لأصحاب الرحلات"""
    promotion_request = models.OneToOneField(
        PromotionRequest,
        on_delete=models.CASCADE,
        related_name='commission',
        verbose_name='طلب الترويج'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='promotion_commissions',
        verbose_name='صاحب الرحلة'
    )
    amount = models.DecimalField('مبلغ العمولة', max_digits=10, decimal_places=2)
    currency = models.CharField('العملة', max_length=3, default='EGP')
    status = models.CharField(
        'حالة العمولة',
        max_length=20,
        choices=[
            ('pending', 'في الانتظار'),
            ('paid', 'مدفوعة'),
            ('cancelled', 'ملغية'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    paid_at = models.DateTimeField('تاريخ الدفع', null=True, blank=True)

    class Meta:
        verbose_name = 'عمولة ترويج'
        verbose_name_plural = 'عمولات الترويج'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"عمولة {self.amount} {self.currency} لـ {self.owner.username}"
