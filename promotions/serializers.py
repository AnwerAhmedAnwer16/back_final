from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PromotionPlan, PromotionRequest, ActivePromotion, PromotionCommission
from trip.models import Trip
from accounts.serializers import UserSerializer
from trip.serializers import TripSerializer

User = get_user_model()


class PromotionPlanSerializer(serializers.ModelSerializer):
    """Serializer لخطط الترويج"""
    owner_commission_amount = serializers.ReadOnlyField()
    platform_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = PromotionPlan
        fields = [
            'id', 'name', 'duration_days', 'price', 'currency',
            'reach_multiplier', 'description', 'features', 'is_active',
            'owner_commission_amount', 'platform_amount'
        ]
        read_only_fields = ['id']


class CreatePromotionRequestSerializer(serializers.Serializer):
    """Serializer لإنشاء طلب ترويج جديد"""
    trip_id = serializers.IntegerField()
    promotion_plan_id = serializers.IntegerField()
    sponsor_message = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="نبذة عن سبب الترويج (اختياري)"
    )
    
    def validate_trip_id(self, value):
        """التحقق من وجود الرحلة"""
        try:
            trip = Trip.objects.get(id=value)
            return value
        except Trip.DoesNotExist:
            raise serializers.ValidationError("الرحلة غير موجودة")
    
    def validate_promotion_plan_id(self, value):
        """التحقق من وجود خطة الترويج"""
        try:
            plan = PromotionPlan.objects.get(id=value, is_active=True)
            return value
        except PromotionPlan.DoesNotExist:
            raise serializers.ValidationError("خطة الترويج غير موجودة أو غير نشطة")
    
    def validate(self, attrs):
        """التحقق من صحة البيانات"""
        user = self.context['request'].user
        trip_id = attrs['trip_id']
        
        # التحقق من أن المستخدم لديه verified badge
        if not user.has_verified_badge:
            raise serializers.ValidationError(
                "يجب أن يكون لديك اشتراك نشط للقيام بالترويج"
            )
        
        # التحقق من عدم وجود طلب ترويج نشط لنفس الرحلة من نفس المستخدم
        existing_request = PromotionRequest.objects.filter(
            sponsor=user,
            trip_id=trip_id,
            status__in=['pending', 'approved', 'active']
        ).exists()
        
        if existing_request:
            raise serializers.ValidationError(
                "لديك طلب ترويج نشط لهذه الرحلة بالفعل"
            )
        
        return attrs


class PromotionRequestSerializer(serializers.ModelSerializer):
    """Serializer لعرض طلبات الترويج"""
    sponsor = UserSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    trip = TripSerializer(read_only=True)
    promotion_plan = PromotionPlanSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = PromotionRequest
        fields = [
            'id', 'sponsor', 'trip', 'owner', 'promotion_plan',
            'sponsor_message', 'status', 'created_at', 'approved_at',
            'rejected_at', 'start_date', 'end_date', 'views_count',
            'clicks_count', 'is_active', 'days_remaining'
        ]
        read_only_fields = [
            'id', 'sponsor', 'trip', 'owner', 'promotion_plan',
            'status', 'created_at', 'approved_at', 'rejected_at',
            'start_date', 'end_date', 'views_count', 'clicks_count'
        ]


class PromotionRequestListSerializer(serializers.ModelSerializer):
    """Serializer مبسط لقائمة طلبات الترويج"""
    sponsor_username = serializers.CharField(source='sponsor.username', read_only=True)
    trip_caption = serializers.CharField(source='trip.caption', read_only=True)
    trip_location = serializers.CharField(source='trip.location', read_only=True)
    plan_name = serializers.CharField(source='promotion_plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='promotion_plan.price', max_digits=10, decimal_places=2, read_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = PromotionRequest
        fields = [
            'id', 'sponsor_username', 'trip_caption', 'trip_location',
            'plan_name', 'plan_price', 'sponsor_message', 'status',
            'created_at', 'start_date', 'end_date', 'is_active', 'days_remaining'
        ]


class PromotionApprovalSerializer(serializers.Serializer):
    """Serializer للموافقة على طلب الترويج أو رفضه"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    
    def validate_action(self, value):
        """التحقق من صحة الإجراء"""
        if value not in ['approve', 'reject']:
            raise serializers.ValidationError("الإجراء يجب أن يكون 'approve' أو 'reject'")
        return value


class ActivePromotionSerializer(serializers.ModelSerializer):
    """Serializer للترويجات النشطة"""
    trip = TripSerializer(read_only=True)
    sponsor = UserSerializer(read_only=True)
    sponsor_message = serializers.ReadOnlyField()
    promotion_plan = PromotionPlanSerializer(source='promotion_request.promotion_plan', read_only=True)
    start_date = serializers.DateTimeField(source='promotion_request.start_date', read_only=True)
    end_date = serializers.DateTimeField(source='promotion_request.end_date', read_only=True)
    views_count = serializers.IntegerField(source='promotion_request.views_count', read_only=True)
    clicks_count = serializers.IntegerField(source='promotion_request.clicks_count', read_only=True)
    
    class Meta:
        model = ActivePromotion
        fields = [
            'id', 'trip', 'sponsor', 'sponsor_message', 'promotion_plan',
            'priority_score', 'start_date', 'end_date', 'views_count', 'clicks_count'
        ]


class PromotionCommissionSerializer(serializers.ModelSerializer):
    """Serializer لعمولات الترويج"""
    owner = UserSerializer(read_only=True)
    promotion_request = PromotionRequestListSerializer(read_only=True)
    
    class Meta:
        model = PromotionCommission
        fields = [
            'id', 'promotion_request', 'owner', 'amount', 'currency',
            'status', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at']


class PromotionStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات الترويج"""
    total_promotions = serializers.IntegerField()
    active_promotions = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_earned = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_views = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    click_through_rate = serializers.FloatField()


class TripPromotionInfoSerializer(serializers.Serializer):
    """Serializer لمعلومات الترويج الخاصة برحلة معينة"""
    can_promote = serializers.BooleanField()
    has_active_promotion = serializers.BooleanField()
    active_promotion = ActivePromotionSerializer(required=False, allow_null=True)
    available_plans = PromotionPlanSerializer(many=True)
    reason = serializers.CharField(required=False, allow_blank=True)
