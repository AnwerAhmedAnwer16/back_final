from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import PromotionPlan, PromotionRequest, ActivePromotion, PromotionCommission
from .serializers import (
    PromotionPlanSerializer,
    CreatePromotionRequestSerializer,
    PromotionRequestSerializer,
    PromotionRequestListSerializer,
    PromotionApprovalSerializer,
    ActivePromotionSerializer,
    PromotionCommissionSerializer,
    PromotionStatsSerializer,
    TripPromotionInfoSerializer
)
from trip.models import Trip
from accounts.services import PayMobService
from accounts.models import Payment
from .services import PromotionPaymentService, PromotionManagementService
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class PromotionPlanListView(generics.ListAPIView):
    """عرض قائمة خطط الترويج المتاحة"""
    queryset = PromotionPlan.objects.filter(is_active=True)
    serializer_class = PromotionPlanSerializer
    permission_classes = [permissions.AllowAny]


class CreatePromotionRequestView(APIView):
    """إنشاء طلب ترويج جديد"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreatePromotionRequestSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                trip_id = serializer.validated_data['trip_id']
                promotion_plan_id = serializer.validated_data['promotion_plan_id']
                sponsor_message = serializer.validated_data.get('sponsor_message', '')

                trip = get_object_or_404(Trip, id=trip_id)
                promotion_plan = get_object_or_404(PromotionPlan, id=promotion_plan_id, is_active=True)

                # إنشاء طلب الترويج
                promotion_request = PromotionRequest.objects.create(
                    sponsor=request.user,
                    trip=trip,
                    owner=trip.user,
                    promotion_plan=promotion_plan,
                    sponsor_message=sponsor_message,
                    status='pending'
                )

                # إنشاء عملية الدفع
                payment_service = PromotionPaymentService()
                payment_data = payment_service.process_promotion_payment(
                    user=request.user,
                    promotion_plan=promotion_plan
                )

                # ربط الدفعة بطلب الترويج
                payment = Payment.objects.get(id=payment_data['payment_id'])
                promotion_request.payment = payment
                promotion_request.save()

                logger.info(f"Promotion request created: {promotion_request.id}")

                return Response({
                    'message': 'تم إنشاء طلب الترويج بنجاح',
                    'promotion_request_id': promotion_request.id,
                    'payment_id': payment_data['payment_id'],
                    'iframe_url': payment_data['iframe_url'],
                    'order_id': payment_data['order_id']
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error creating promotion request: {str(e)}")
                return Response({
                    'error': 'فشل في إنشاء طلب الترويج',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPromotionRequestsView(generics.ListAPIView):
    """عرض طلبات الترويج الخاصة بالمستخدم (كراعي)"""
    serializer_class = PromotionRequestListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PromotionRequest.objects.filter(
            sponsor=self.request.user
        ).select_related(
            'sponsor', 'trip', 'owner', 'promotion_plan'
        ).order_by('-created_at')


class ReceivedPromotionRequestsView(generics.ListAPIView):
    """عرض طلبات الترويج المستلمة (كصاحب رحلة)"""
    serializer_class = PromotionRequestListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PromotionRequest.objects.filter(
            owner=self.request.user
        ).select_related(
            'sponsor', 'trip', 'owner', 'promotion_plan'
        ).order_by('-created_at')


class PromotionRequestDetailView(generics.RetrieveAPIView):
    """عرض تفاصيل طلب ترويج"""
    serializer_class = PromotionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # المستخدم يمكنه رؤية طلبات الترويج التي هو راعيها أو مالك الرحلة فيها
        return PromotionRequest.objects.filter(
            Q(sponsor=self.request.user) | Q(owner=self.request.user)
        ).select_related('sponsor', 'trip', 'owner', 'promotion_plan')


class PromotionApprovalView(APIView):
    """الموافقة على طلب الترويج أو رفضه"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, promotion_request_id):
        promotion_request = get_object_or_404(
            PromotionRequest,
            id=promotion_request_id,
            owner=request.user,  # فقط صاحب الرحلة يمكنه الموافقة/الرفض
            status='pending'
        )

        serializer = PromotionApprovalSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']

            try:
                if action == 'approve':
                    # التحقق من أن الدفعة تمت بنجاح
                    if not promotion_request.payment or promotion_request.payment.status != 'completed':
                        return Response({
                            'error': 'لم يتم الدفع بعد أو فشل الدفع'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # الموافقة على الطلب
                    if promotion_request.approve():
                        # تفعيل الترويج
                        promotion_request.activate()

                        # إنشاء ترويج نشط
                        ActivePromotion.objects.create(
                            promotion_request=promotion_request,
                            priority_score=self._calculate_priority_score(promotion_request)
                        )

                        # إنشاء عمولة لصاحب الرحلة
                        PromotionCommission.objects.create(
                            promotion_request=promotion_request,
                            owner=promotion_request.owner,
                            amount=promotion_request.promotion_plan.owner_commission_amount,
                            currency=promotion_request.promotion_plan.currency
                        )

                        logger.info(f"Promotion request {promotion_request.id} approved and activated")

                        return Response({
                            'message': 'تم قبول طلب الترويج وتفعيله بنجاح'
                        }, status=status.HTTP_200_OK)

                elif action == 'reject':
                    if promotion_request.reject():
                        logger.info(f"Promotion request {promotion_request.id} rejected")

                        return Response({
                            'message': 'تم رفض طلب الترويج'
                        }, status=status.HTTP_200_OK)

                return Response({
                    'error': 'فشل في تنفيذ الإجراء'
                }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                logger.error(f"Error processing promotion approval: {str(e)}")
                return Response({
                    'error': 'حدث خطأ أثناء معالجة الطلب',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _calculate_priority_score(self, promotion_request):
        """حساب نقاط الأولوية للترويج"""
        base_score = 100

        # إضافة نقاط حسب خطة الترويج
        if promotion_request.promotion_plan.duration_days == 30:
            base_score += 50
        elif promotion_request.promotion_plan.duration_days == 7:
            base_score += 20

        # إضافة نقاط حسب السعر
        price_bonus = int(promotion_request.promotion_plan.price / 10)
        base_score += price_bonus

        return base_score


class ActivePromotionsView(generics.ListAPIView):
    """عرض الترويجات النشطة"""
    serializer_class = ActivePromotionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ActivePromotion.objects.filter(
            promotion_request__status='active',
            promotion_request__end_date__gt=timezone.now()
        ).select_related(
            'promotion_request__trip',
            'promotion_request__sponsor',
            'promotion_request__promotion_plan'
        ).order_by('-priority_score', '-promotion_request__start_date')


class UserPromotionCommissionsView(generics.ListAPIView):
    """عرض عمولات الترويج للمستخدم"""
    serializer_class = PromotionCommissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PromotionCommission.objects.filter(
            owner=self.request.user
        ).select_related(
            'promotion_request__trip',
            'promotion_request__sponsor',
            'promotion_request__promotion_plan'
        ).order_by('-created_at')


class PromotionStatsView(APIView):
    """إحصائيات الترويج للمستخدم"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # إحصائيات كراعي
        sponsor_stats = self._get_sponsor_stats(user)

        # إحصائيات كصاحب رحلة
        owner_stats = self._get_owner_stats(user)

        return Response({
            'sponsor_stats': sponsor_stats,
            'owner_stats': owner_stats
        })

    def _get_sponsor_stats(self, user):
        """إحصائيات المستخدم كراعي"""
        requests = PromotionRequest.objects.filter(sponsor=user)

        total_promotions = requests.count()
        active_promotions = requests.filter(status='active').count()
        total_spent = requests.filter(
            payment__status='completed'
        ).aggregate(
            total=Sum('promotion_plan__price')
        )['total'] or 0

        total_views = requests.aggregate(total=Sum('views_count'))['total'] or 0
        total_clicks = requests.aggregate(total=Sum('clicks_count'))['total'] or 0

        click_through_rate = (total_clicks / total_views * 100) if total_views > 0 else 0

        return {
            'total_promotions': total_promotions,
            'active_promotions': active_promotions,
            'total_spent': total_spent,
            'total_views': total_views,
            'total_clicks': total_clicks,
            'click_through_rate': round(click_through_rate, 2)
        }

    def _get_owner_stats(self, user):
        """إحصائيات المستخدم كصاحب رحلة"""
        commissions = PromotionCommission.objects.filter(owner=user)

        total_earned = commissions.filter(
            status='paid'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        pending_earnings = commissions.filter(
            status='pending'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_requests = PromotionRequest.objects.filter(owner=user).count()
        approved_requests = PromotionRequest.objects.filter(
            owner=user,
            status__in=['approved', 'active', 'expired']
        ).count()

        return {
            'total_earned': total_earned,
            'pending_earnings': pending_earnings,
            'total_requests': total_requests,
            'approved_requests': approved_requests,
            'approval_rate': round((approved_requests / total_requests * 100) if total_requests > 0 else 0, 2)
        }


class TripPromotionInfoView(APIView):
    """معلومات الترويج لرحلة معينة"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        user = request.user

        # التحقق من إمكانية الترويج
        can_promote = user.has_verified_badge
        reason = ""

        if not can_promote:
            reason = "يجب أن يكون لديك اشتراك نشط للقيام بالترويج"

        # فحص وجود ترويج نشط
        active_promotion = ActivePromotion.objects.filter(
            promotion_request__trip=trip,
            promotion_request__status='active',
            promotion_request__end_date__gt=timezone.now()
        ).first()

        has_active_promotion = active_promotion is not None

        # فحص وجود طلب ترويج من نفس المستخدم
        if can_promote:
            existing_request = PromotionRequest.objects.filter(
                sponsor=user,
                trip=trip,
                status__in=['pending', 'approved', 'active']
            ).exists()

            if existing_request:
                can_promote = False
                reason = "لديك طلب ترويج نشط لهذه الرحلة بالفعل"

        # الخطط المتاحة
        available_plans = PromotionPlan.objects.filter(is_active=True)

        data = {
            'can_promote': can_promote,
            'has_active_promotion': has_active_promotion,
            'active_promotion': ActivePromotionSerializer(active_promotion).data if active_promotion else None,
            'available_plans': PromotionPlanSerializer(available_plans, many=True).data,
            'reason': reason
        }

        serializer = TripPromotionInfoSerializer(data)
        return Response(serializer.data)


class CancelPromotionRequestView(APIView):
    """إلغاء طلب ترويج"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, promotion_request_id):
        promotion_request = get_object_or_404(
            PromotionRequest,
            id=promotion_request_id,
            sponsor=request.user,  # فقط الراعي يمكنه الإلغاء
            status__in=['pending', 'approved']  # لا يمكن إلغاء الترويج النشط
        )

        try:
            promotion_request.status = 'cancelled'
            promotion_request.save()

            # إلغاء الترويج النشط إذا كان موجود
            if hasattr(promotion_request, 'active_promotion'):
                promotion_request.active_promotion.delete()

            logger.info(f"Promotion request {promotion_request.id} cancelled")

            return Response({
                'message': 'تم إلغاء طلب الترويج بنجاح'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error cancelling promotion request: {str(e)}")
            return Response({
                'error': 'فشل في إلغاء طلب الترويج'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
