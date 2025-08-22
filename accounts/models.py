from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from .utils import generate_unique_filename, generate_username_from_email 
from django.core.validators import RegexValidator 

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError ('User Must Has an Email')
        email = self.normalize_email(email)
        
        if username is None:
            username = generate_username_from_email(email)
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1

        user = self.model(email = email, username = username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_verified", True) 

            if extra_fields.get("is_staff") is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if extra_fields.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")

            if username is None:
                username = generate_username_from_email(email)
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1

            return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    SUBSCRIPTION_PLANS = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]

    email = models.EmailField('Email', unique = True)
    username = models.CharField(
        'username',
        max_length = 20,
        unique = True,
        db_index=True,  # إضافة index للبحث السريع
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_-]+$',
                message='Username can only contain letters, numbers, underscores, and hyphens.',
                code='invalid_username'
            )
        ]
    )
    date_joined = models.DateTimeField('date joind', default = timezone.now)
    is_active = models.BooleanField('active', default = True)
    is_staff = models.BooleanField('staff', default = False)
    is_verified = models.BooleanField('verified', default = False)

    # Subscription fields
    subscription_plan = models.CharField(
        'subscription plan',
        max_length=20,
        choices=SUBSCRIPTION_PLANS,
        default='free'
    )
    subscription_start_date = models.DateTimeField(
        'subscription start date',
        null=True,
        blank=True
    )
    subscription_end_date = models.DateTimeField(
        'subscription end date',
        null=True,
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['subscription_plan']),
            models.Index(fields=['subscription_end_date']),
        ]

    def __str__(self):
        return self.username

    @property
    def is_subscription_active(self):
        """Check if user has an active subscription"""
        if self.subscription_plan == 'free':
            return False

        if not self.subscription_end_date:
            return False

        return timezone.now() <= self.subscription_end_date

    @property
    def has_verified_badge(self):
        """Check if user should have verified badge (active subscription)"""
        return self.is_subscription_active

    @property
    def subscription_days_remaining(self):
        """Get remaining days in subscription"""
        if not self.is_subscription_active:
            return 0

        remaining = self.subscription_end_date - timezone.now()
        return max(0, remaining.days)

def avatar_upload_path(instance, filename):
    return f'avatars/{instance.user.id}/{generate_unique_filename(instance, filename)}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    first_name = models.CharField('first name', max_length = 15, blank = True, db_index=True)
    last_name = models.CharField('last name', max_length = 15 , blank = True, db_index=True)
    bio = models.TextField('bio', blank = True)
    avatar = models.ImageField('avatar',  upload_to= avatar_upload_path, blank = True)
    country = models.CharField('country', max_length = 20 , blank = True)
    gender = models.CharField('gender', max_length = 20, choices = [('M','male'),('F','female')], blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['first_name']),
            models.Index(fields=['last_name']),
            models.Index(fields=['first_name', 'last_name']),
        ]

    def __str__(self):
        return f"{self.user.username}'s Profile"


class SubscriptionPlan(models.Model):
    """نموذج خطط الاشتراك"""
    PLAN_TYPES = [
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]

    DURATION_TYPES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField('plan name', max_length=50)
    plan_type = models.CharField('plan type', max_length=20, choices=PLAN_TYPES)
    duration = models.CharField('duration', max_length=20, choices=DURATION_TYPES)
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    currency = models.CharField('currency', max_length=3, default='EGP')
    description = models.TextField('description', blank=True)
    features = models.JSONField('features', default=list, blank=True)
    is_active = models.BooleanField('is active', default=True)
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    class Meta:
        unique_together = ('plan_type', 'duration')
        indexes = [
            models.Index(fields=['plan_type', 'duration']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_duration_display()}"


class Payment(models.Model):
    """نموذج المدفوعات"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField('amount', max_digits=10, decimal_places=2)
    currency = models.CharField('currency', max_length=3, default='EGP')
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default='pending')

    # PayMob specific fields
    paymob_order_id = models.CharField('PayMob order ID', max_length=100, blank=True)
    paymob_transaction_id = models.CharField('PayMob transaction ID', max_length=100, blank=True)
    payment_token = models.CharField('payment token', max_length=500, blank=True)

    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    completed_at = models.DateTimeField('completed at', null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['paymob_order_id']),
            models.Index(fields=['paymob_transaction_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.amount} {self.currency}"


class PaymentTransaction(models.Model):
    """نموذج تفاصيل المعاملات مع PayMob"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='transaction')

    # PayMob webhook data
    webhook_data = models.JSONField('webhook data', default=dict, blank=True)
    hmac_signature = models.CharField('HMAC signature', max_length=500, blank=True)

    # Transaction details
    gateway_response = models.JSONField('gateway response', default=dict, blank=True)
    error_message = models.TextField('error message', blank=True)

    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)

    def __str__(self):
        return f"Transaction for Payment {self.payment.id}"
