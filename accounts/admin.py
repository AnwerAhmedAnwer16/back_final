from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, SubscriptionPlan, Payment, PaymentTransaction

# Register your models here.

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'username', 'is_verified', 'subscription_plan', 'subscription_end_date', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_verified', 'subscription_plan', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Subscription', {'fields': ('subscription_plan', 'subscription_start_date', 'subscription_end_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('subscription_start_date', 'subscription_end_date')


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'duration', 'price', 'currency', 'is_active', 'created_at')
    list_filter = ('plan_type', 'duration', 'is_active', 'currency')
    search_fields = ('name', 'description')
    ordering = ('plan_type', 'duration', 'price')

    fieldsets = (
        (None, {'fields': ('name', 'plan_type', 'duration')}),
        ('Pricing', {'fields': ('price', 'currency')}),
        ('Details', {'fields': ('description', 'features', 'is_active')}),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription_plan', 'amount', 'currency', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'currency', 'created_at', 'completed_at')
    search_fields = ('user__username', 'user__email', 'paymob_order_id', 'paymob_transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    fieldsets = (
        (None, {'fields': ('user', 'subscription_plan')}),
        ('Payment Details', {'fields': ('amount', 'currency', 'status')}),
        ('PayMob Info', {'fields': ('paymob_order_id', 'paymob_transaction_id', 'payment_token')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'completed_at')}),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'created_at')
    search_fields = ('payment__user__username', 'payment__paymob_order_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, UserAdmin)
