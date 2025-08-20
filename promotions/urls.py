from django.urls import path
from . import views

urlpatterns = [
    # خطط الترويج
    path('plans/', views.PromotionPlanListView.as_view(), name='promotion_plans'),
    
    # إنشاء ومعالجة طلبات الترويج
    path('create-request/', views.CreatePromotionRequestView.as_view(), name='create_promotion_request'),
    path('my-requests/', views.UserPromotionRequestsView.as_view(), name='user_promotion_requests'),
    path('received-requests/', views.ReceivedPromotionRequestsView.as_view(), name='received_promotion_requests'),
    path('requests/<int:pk>/', views.PromotionRequestDetailView.as_view(), name='promotion_request_detail'),
    
    # الموافقة والرفض
    path('requests/<int:promotion_request_id>/approve/', views.PromotionApprovalView.as_view(), name='promotion_approval'),
    path('requests/<int:promotion_request_id>/cancel/', views.CancelPromotionRequestView.as_view(), name='cancel_promotion_request'),
    
    # الترويجات النشطة
    path('active/', views.ActivePromotionsView.as_view(), name='active_promotions'),
    
    # العمولات والإحصائيات
    path('my-commissions/', views.UserPromotionCommissionsView.as_view(), name='user_promotion_commissions'),
    path('stats/', views.PromotionStatsView.as_view(), name='promotion_stats'),
    
    # معلومات الترويج لرحلة معينة
    path('trip/<int:trip_id>/info/', views.TripPromotionInfoView.as_view(), name='trip_promotion_info'),
]
