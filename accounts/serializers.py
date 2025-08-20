from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Profile, SubscriptionPlan, Payment
from .utils import validate_password_strength, calculate_password_strength
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirm', 'date_joined', 'is_verified']
        read_only_fields = ['id', 'date_joined', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True}
        }

    def validate_password(self, value):
        """التحقق من قوة كلمة المرور"""
        # استخدام Django's built-in validators
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        # استخدام custom validator
        errors = validate_password_strength(value)
        if errors:
            error_messages = [error['message'] for error in errors]
            raise serializers.ValidationError(error_messages)

        return value

    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'كلمات المرور غير متطابقة'
            })

        return attrs

    def create(self, validated_data):
        """إنشاء مستخدم جديد"""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'date_joined', 'is_verified',
                 'subscription_plan', 'subscription_start_date', 'subscription_end_date',
                 'subscription_status']
        read_only_fields = ['id', 'date_joined', 'is_verified', 'subscription_plan',
                           'subscription_start_date', 'subscription_end_date']

    def get_subscription_status(self, obj):
        """الحصول على حالة الاشتراك"""
        return {
            'is_active': obj.is_subscription_active,
            'days_remaining': obj.subscription_days_remaining,
            'has_verified_badge': obj.has_verified_badge
        }


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """التحقق من كلمة المرور القديمة"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('كلمة المرور القديمة غير صحيحة')
        return value

    def validate_new_password(self, value):
        """التحقق من قوة كلمة المرور الجديدة"""
        user = self.context['request'].user

        # استخدام Django's built-in validators
        try:
            validate_password(value, user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        # استخدام custom validator
        errors = validate_password_strength(value, user)
        if errors:
            error_messages = [error['message'] for error in errors]
            raise serializers.ValidationError(error_messages)

        return value

    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور الجديدة"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'كلمات المرور الجديدة غير متطابقة'
            })

        return attrs


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate_new_password(self, value):
        """التحقق من قوة كلمة المرور الجديدة"""
        # استخدام Django's built-in validators
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        # استخدام custom validator
        errors = validate_password_strength(value)
        if errors:
            error_messages = [error['message'] for error in errors]
            raise serializers.ValidationError(error_messages)

        return value

    def validate(self, attrs):
        """التحقق من تطابق كلمات المرور"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'كلمات المرور غير متطابقة'
            })

        return attrs


class PasswordStrengthSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        strength_info = calculate_password_strength(password)
        attrs['strength_info'] = strength_info
        return attrs

class ProfileSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']


class PublicUserProfileSerializer(serializers.ModelSerializer):
    """Serializer لعرض البروفايل العام للمستخدمين"""
    profile = ProfileSerialzer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    trips_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'date_joined', 'is_verified',
            'profile', 'followers_count', 'following_count',
            'trips_count', 'is_following'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'is_verified']

    def get_followers_count(self, obj):
        """عدد المتابعين"""
        return obj.followers.count()

    def get_following_count(self, obj):
        """عدد المتابَعين"""
        return obj.following.count()

    def get_trips_count(self, obj):
        """عدد الرحلات"""
        return obj.trips.count()

    def get_is_following(self, obj):
        """هل المستخدم الحالي يتابع هذا المستخدم"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from interactions.models import Follow
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer محسن لنتائج البحث عن المستخدمين"""
    profile = ProfileSerialzer(read_only=True)
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile', 'followers_count']

    def get_followers_count(self, obj):
        return obj.followers.count()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_verified'] = user.is_verified
        token['subscription_plan'] = user.subscription_plan
        token['has_verified_badge'] = user.has_verified_badge
        return token


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer لخطط الاشتراك"""

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'plan_type', 'duration', 'price', 'currency',
                 'description', 'features', 'is_active']
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer للمدفوعات"""
    subscription_plan_details = SubscriptionPlanSerializer(source='subscription_plan', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'currency', 'status', 'subscription_plan_details',
                 'created_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'completed_at']


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer لإنشاء اشتراك جديد"""
    subscription_plan_id = serializers.IntegerField()

    def validate_subscription_plan_id(self, value):
        """التحقق من وجود الخطة"""
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Subscription plan not found or inactive")


class SubscriptionStatusSerializer(serializers.Serializer):
    """Serializer لحالة الاشتراك"""
    plan = serializers.CharField()
    is_active = serializers.BooleanField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    days_remaining = serializers.IntegerField()
    has_verified_badge = serializers.BooleanField()