# Subscription System Documentation

## Overview
نظام الاشتراكات والدفع المتكامل مع PayMob لمنح المستخدمين verified badge والمميزات المدفوعة.

## Table of Contents
- [System Architecture](#system-architecture)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [PayMob Integration](#paymob-integration)
- [Subscription Management](#subscription-management)
- [Verified Badge Logic](#verified-badge-logic)
- [Management Commands](#management-commands)
- [Testing](#testing)

## System Architecture

### Core Components
1. **User Model Extensions**: إضافة حقول الاشتراك للمستخدم
2. **Subscription Plans**: نماذج خطط الاشتراك المختلفة
3. **Payment Processing**: معالجة المدفوعات عبر PayMob
4. **Webhook Handling**: استقبال إشعارات PayMob
5. **Automatic Expiry**: فحص تلقائي لانتهاء الاشتراكات

### Environment Variables
```env
# PayMob Configuration (Test Environment)
PAYMOB_API_KEY=ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5...
PAYMOB_INTEGRATION_ID=5242071
PAYMOB_IFRAME_ID=951380
PAYMOB_BASE_URL=https://accept.paymob.com/api
```

## Database Models

### User Model Extensions
```python
class User(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...
    
    # Subscription fields
    subscription_plan = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('premium', 'Premium'), ('pro', 'Pro')],
        default='free'
    )
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
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
        """Check if user should have verified badge"""
        return self.is_subscription_active
```

### SubscriptionPlan Model
```python
class SubscriptionPlan(models.Model):
    PLAN_TYPES = [('premium', 'Premium'), ('pro', 'Pro')]
    DURATION_TYPES = [('monthly', 'Monthly'), ('yearly', 'Yearly')]
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    duration = models.CharField(max_length=20, choices=DURATION_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EGP')
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
```

### Payment Model
```python
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # PayMob specific fields
    paymob_order_id = models.CharField(max_length=100, blank=True)
    paymob_transaction_id = models.CharField(max_length=100, blank=True)
    payment_token = models.CharField(max_length=500, blank=True)
```

## API Endpoints

### Authentication Required
جميع endpoints تتطلب JWT authentication ما عدا عرض الخطط والـ webhook.

### 1. Subscription Plans
```http
GET /api/accounts/subscription-plans/
```
**Response:**
```json
[
    {
        "id": 1,
        "name": "Premium Monthly",
        "plan_type": "premium",
        "duration": "monthly",
        "price": "99.00",
        "currency": "EGP",
        "description": "Premium features for one month",
        "features": ["Verified badge", "Priority support"],
        "is_active": true
    }
]
```

### 2. Create Subscription
```http
POST /api/accounts/create-subscription/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "subscription_plan_id": 1
}
```
**Response:**
```json
{
    "message": "Payment initiated successfully",
    "payment_id": 123,
    "iframe_url": "https://accept.paymob.com/api/acceptance/iframes/951380?payment_token=...",
    "order_id": "12345"
}
```

### 3. Subscription Status
```http
GET /api/accounts/subscription-status/
Authorization: Bearer <jwt_token>
```
**Response:**
```json
{
    "plan": "premium",
    "is_active": true,
    "start_date": "2025-08-20T02:00:00Z",
    "end_date": "2025-09-20T02:00:00Z",
    "days_remaining": 30,
    "has_verified_badge": true
}
```

### 4. Payment History
```http
GET /api/accounts/payment-history/
Authorization: Bearer <jwt_token>
```

### 5. Cancel Subscription
```http
POST /api/accounts/cancel-subscription/
Authorization: Bearer <jwt_token>
```

### 6. PayMob Webhook
```http
POST /api/accounts/paymob-webhook/
Content-Type: application/json

{
    "order": {"id": "12345"},
    "id": "transaction_id",
    "success": true
}
```

## PayMob Integration

### Payment Flow
1. **User selects plan** → Frontend calls `create-subscription`
2. **Backend creates order** → PayMob API call
3. **Payment token generated** → PayMob API call
4. **User redirected to iframe** → PayMob payment page
5. **Payment completed** → PayMob sends webhook
6. **Subscription activated** → Backend updates user

### PayMobService Class
```python
class PayMobService:
    def authenticate(self):
        """Get auth token from PayMob"""
    
    def create_order(self, amount, currency='EGP'):
        """Create order in PayMob"""
    
    def create_payment_key(self, order_id, amount, user_data):
        """Create payment key for payment"""
    
    def process_subscription_payment(self, user, subscription_plan):
        """Process complete subscription payment flow"""
    
    def handle_successful_payment(self, payment_id, transaction_data):
        """Handle successful payment and activate subscription"""
```

## Subscription Management

### Automatic Expiry Check
```python
class SubscriptionService:
    @staticmethod
    def check_expired_subscriptions():
        """Check and handle expired subscriptions"""
        expired_users = User.objects.filter(
            subscription_end_date__lt=timezone.now(),
            subscription_plan__in=['premium', 'pro']
        )
        
        for user in expired_users:
            user.subscription_plan = 'free'
            user.subscription_start_date = None
            user.subscription_end_date = None
            user.save()
        
        return expired_users.count()
```

### Subscription Activation
عند نجاح الدفع:
1. تحديث `subscription_plan` للمستخدم
2. تعيين `subscription_start_date` للوقت الحالي
3. حساب `subscription_end_date` حسب نوع الخطة:
   - Monthly: +30 days
   - Yearly: +365 days

## Verified Badge Logic

### How it Works
```python
@property
def has_verified_badge(self):
    """Check if user should have verified badge"""
    return self.is_subscription_active

@property
def is_subscription_active(self):
    """Check if user has an active subscription"""
    if self.subscription_plan == 'free':
        return False
    if not self.subscription_end_date:
        return False
    return timezone.now() <= self.subscription_end_date
```

### Badge Removal Process
1. **Automatic Check**: يتم فحص انتهاء الاشتراكات دورياً
2. **Management Command**: `python manage.py check_expired_subscriptions`
3. **Real-time Check**: كل استدعاء لـ `has_verified_badge` يفحص التاريخ
4. **Immediate Effect**: البادج يختفي فوراً عند انتهاء الاشتراك

### Frontend Integration
```javascript
// Check user's verified badge status
const userStatus = await fetch('/api/accounts/subscription-status/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const data = await userStatus.json();
if (data.has_verified_badge) {
    // Show verified badge
} else {
    // Hide verified badge
}
```

## Management Commands

### 1. Check Expired Subscriptions
```bash
# Production run
python manage.py check_expired_subscriptions

# Dry run (preview only)
python manage.py check_expired_subscriptions --dry-run
```

### 2. Create Default Plans
```bash
python manage.py create_subscription_plans
```

### Cron Job Setup
```bash
# Add to crontab for daily check at 2 AM
0 2 * * * /path/to/python /path/to/manage.py check_expired_subscriptions
```

## Testing

### Run Subscription Tests
```bash
# All subscription tests
python manage.py test accounts.test_subscriptions

# Specific test class
python manage.py test accounts.test_subscriptions.UserSubscriptionModelTest

# With verbose output
python manage.py test accounts.test_subscriptions -v 2
```

### Test Coverage
- User subscription model properties
- Subscription plan creation
- Payment processing
- API endpoints
- Service classes
- Automatic expiry handling

## Available Plans

| Plan | Duration | Price | Features |
|------|----------|-------|----------|
| Premium | Monthly | 99 EGP | Verified badge, Priority support, Advanced filters |
| Premium | Yearly | 999 EGP | All monthly + 2 months free |
| Pro | Monthly | 199 EGP | All Premium + Business tools, Analytics |
| Pro | Yearly | 1999 EGP | All monthly + 2 months free |

## Security Considerations

1. **Webhook Verification**: تحقق من صحة PayMob webhooks
2. **Payment Validation**: تحقق من مطابقة المبالغ
3. **User Authorization**: تحقق من صلاحيات المستخدم
4. **Token Security**: حماية payment tokens
5. **Data Encryption**: تشفير البيانات الحساسة

## Troubleshooting

### Common Issues
1. **Payment not completing**: Check PayMob webhook URL
2. **Badge not showing**: Verify subscription dates
3. **API errors**: Check authentication tokens
4. **Expired subscriptions**: Run management command

### Logs
```python
import logging
logger = logging.getLogger(__name__)

# Check logs for payment processing
logger.info(f"Payment {payment_id} processed successfully")
logger.error(f"PayMob authentication failed: {error}")
```

## Future Enhancements

1. **Promo Codes**: نظام كوبونات الخصم
2. **Subscription Upgrades**: ترقية الخطط
3. **Refund System**: نظام استرداد الأموال
4. **Analytics Dashboard**: لوحة تحكم الإحصائيات
5. **Email Notifications**: إشعارات انتهاء الاشتراك

## Promotion System (NEW)

### Overview
نظام ترويج الرحلات المدفوع للمستخدمين أصحاب verified badge لترويج أي رحلة مع موافقة صاحبها.

### Core Features
- ✅ ترويج مدفوع للرحلات
- ✅ نظام موافقة من صاحب الرحلة
- ✅ عمولة 10% لصاحب الرحلة الأصلي
- ✅ خطط ترويج متعددة (3 أيام، أسبوع، شهر)
- ✅ دفع عبر PayMob
- ✅ عرض "برعاية" مع بيانات الراعي

### Promotion Plans
| الخطة | المدة | السعر | الوصول | العمولة |
|-------|-------|-------|---------|---------|
| ترويج سريع | 3 أيام | 50 جنيه | 2x | 5 جنيه |
| ترويج أسبوعي | 7 أيام | 100 جنيه | 3x | 10 جنيه |
| ترويج شهري | 30 يوم | 300 جنيه | 5x | 30 جنيه |

### API Endpoints
```
GET /api/promotions/plans/ - عرض خطط الترويج
POST /api/promotions/create-request/ - إنشاء طلب ترويج
GET /api/promotions/my-requests/ - طلبات الترويج الخاصة بي
GET /api/promotions/received-requests/ - طلبات الترويج المستلمة
POST /api/promotions/requests/{id}/approve/ - الموافقة/الرفض
GET /api/promotions/active/ - الترويجات النشطة
GET /api/promotions/trip/{id}/info/ - معلومات ترويج رحلة
```

### User Flow
1. مستخدم بـ verified badge يشاهد رحلة
2. يضغط "ترويج هذه الرحلة"
3. يختار خطة الترويج ويكتب رسالة
4. يدفع عبر PayMob
5. يُرسل إشعار لصاحب الرحلة
6. عند الموافقة: الرحلة تظهر كـ "مميزة"
7. صاحب الرحلة يحصل على 10% عمولة

### Management Commands
```bash
# إنشاء خطط الترويج الافتراضية
python manage.py create_promotion_plans

# فحص الترويجات المنتهية
python manage.py check_expired_promotions

# معاينة فقط
python manage.py check_expired_promotions --dry-run
```

---

**Last Updated**: August 20, 2025
**Version**: 2.0.0 (Added Promotion System)
