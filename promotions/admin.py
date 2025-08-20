from django.contrib import admin
from .models import PromotionPlan, PromotionRequest, ActivePromotion, PromotionCommission

# Register your models here.

@admin.register(PromotionPlan)
class PromotionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price', 'currency', 'reach_multiplier', 'is_active', 'created_at')
    list_filter = ('duration_days', 'is_active', 'currency', 'reach_multiplier')
    search_fields = ('name', 'description')
    ordering = ('duration_days', 'price')

    fieldsets = (
        (None, {'fields': ('name', 'duration_days', 'price', 'currency', 'reach_multiplier')}),
        ('Details', {'fields': ('description', 'features', 'is_active')}),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(PromotionRequest)
class PromotionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sponsor', 'trip_caption', 'owner', 'promotion_plan', 'status', 'created_at', 'start_date', 'end_date')
    list_filter = ('status', 'created_at', 'start_date', 'promotion_plan__duration_days')
    search_fields = ('sponsor__username', 'owner__username', 'trip__caption', 'sponsor_message')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('sponsor', 'trip', 'owner', 'promotion_plan')}),
        ('Request Details', {'fields': ('sponsor_message', 'status', 'payment')}),
        ('Dates', {'fields': ('created_at', 'approved_at', 'rejected_at', 'start_date', 'end_date')}),
        ('Statistics', {'fields': ('views_count', 'clicks_count')}),
    )

    readonly_fields = ('created_at', 'approved_at', 'rejected_at', 'start_date', 'end_date')

    def trip_caption(self, obj):
        return obj.trip.caption[:50] + '...' if len(obj.trip.caption) > 50 else obj.trip.caption
    trip_caption.short_description = 'Trip Caption'


@admin.register(ActivePromotion)
class ActivePromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip_caption', 'sponsor', 'priority_score', 'start_date', 'end_date', 'days_remaining')
    list_filter = ('priority_score', 'promotion_request__start_date')
    search_fields = ('promotion_request__sponsor__username', 'promotion_request__trip__caption')
    ordering = ('-priority_score', '-promotion_request__start_date')

    def trip_caption(self, obj):
        return obj.promotion_request.trip.caption[:50] + '...' if len(obj.promotion_request.trip.caption) > 50 else obj.promotion_request.trip.caption
    trip_caption.short_description = 'Trip Caption'

    def sponsor(self, obj):
        return obj.promotion_request.sponsor.username
    sponsor.short_description = 'Sponsor'

    def start_date(self, obj):
        return obj.promotion_request.start_date
    start_date.short_description = 'Start Date'

    def end_date(self, obj):
        return obj.promotion_request.end_date
    end_date.short_description = 'End Date'

    def days_remaining(self, obj):
        return obj.promotion_request.days_remaining
    days_remaining.short_description = 'Days Remaining'


@admin.register(PromotionCommission)
class PromotionCommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'amount', 'currency', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'currency', 'created_at', 'paid_at')
    search_fields = ('owner__username', 'promotion_request__trip__caption')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('promotion_request', 'owner')}),
        ('Commission Details', {'fields': ('amount', 'currency', 'status')}),
        ('Dates', {'fields': ('created_at', 'paid_at')}),
    )

    readonly_fields = ('created_at', 'paid_at')

    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='paid',
            paid_at=timezone.now()
        )
        self.message_user(request, f'{updated} commissions marked as paid.')
    mark_as_paid.short_description = 'Mark selected commissions as paid'
