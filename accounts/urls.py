
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import subscription_views
from .views import google_oauth2_login_url, google_login

app_name = 'accounts'

urlpatterns = [
    # authentication 
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('verify-email/<str:uidb64>/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('check-verification/<str:uidb64>/<str:token>/', views.CheckVerificationTokenView.as_view(), name='check_verification'),
    path('generate-verification-link/', views.GenerateVerificationLinkView.as_view(), name='generate_verification_link'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    
    # Password reset
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Password validation
    path('password-strength-check/', views.PasswordStrengthCheckView.as_view(), name='password_strength_check'),
    path('password-requirements/', views.PasswordRequirementsView.as_view(), name='password_requirements'),
    path('validate-password/', views.ValidatePasswordView.as_view(), name='validate_password'),
    
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/details/', views.ProfileDetailView.as_view(), name='profile_details'),

    # Public profile
    path('users/<int:id>/profile/', views.PublicUserProfileView.as_view(), name='public_user_profile'),

    # Subscription endpoints
    path('subscription-plans/', subscription_views.SubscriptionPlanListView.as_view(), name='subscription_plans'),
    path('create-subscription/', subscription_views.CreateSubscriptionView.as_view(), name='create_subscription'),
    path('subscription-status/', subscription_views.UserSubscriptionStatusView.as_view(), name='subscription_status'),
    path('payment-history/', subscription_views.UserPaymentHistoryView.as_view(), name='payment_history'),
    path('cancel-subscription/', subscription_views.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('payment-status/<int:payment_id>/', subscription_views.CheckPaymentStatusView.as_view(), name='payment_status'),

    # PayMob webhook
    path('paymob-webhook/', subscription_views.PayMobWebhookView.as_view(), name='paymob_webhook'),
]

