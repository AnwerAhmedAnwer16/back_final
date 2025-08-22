from rest_framework import generics, status, serializers, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist
from accounts.serializers import UserSearchSerializer
from trip.models import TripTag
from trip.serializers import TripTagSerializer
from .models import SearchHistory, PopularSearch
from django.core.cache import cache
from django.utils.encoding import force_str
import hashlib
import logging

logger = logging.getLogger(__name__)


def generate_cache_key(prefix, query, search_type='unified', user_id=None):
    """إنشاء cache key فريد للبحث"""
    key_parts = [prefix, search_type, query.lower().strip()]
    if user_id:
        key_parts.append(str(user_id))

    key_string = ':'.join(key_parts)
    # استخدام hash للـ keys الطويلة
    if len(key_string) > 200:
        key_hash = hashlib.md5(force_str(key_string).encode('utf-8')).hexdigest()
        return f"{prefix}:{key_hash}"

    return key_string


def get_cached_search_results(cache_key):
    """الحصول على نتائج البحث من الـ cache"""
    try:
        return cache.get(cache_key)
    except Exception as e:
        logger.error(f"Cache get error: {str(e)}")
        return None


def set_cached_search_results(cache_key, data, timeout=300):
    """حفظ نتائج البحث في الـ cache (5 دقائق افتراضي)"""
    try:
        cache.set(cache_key, data, timeout)
    except Exception as e:
        logger.error(f"Cache set error: {str(e)}")


def check_rate_limit(request, limit_type='search', max_requests=60, window_seconds=60):
    """فحص rate limiting للبحث"""
    try:
        client_ip = get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else None

        # إنشاء key للـ rate limiting
        if user_id:
            rate_key = f"rate_limit:{limit_type}:user:{user_id}"
        else:
            rate_key = f"rate_limit:{limit_type}:ip:{client_ip}"

        # الحصول على عدد الطلبات الحالية
        current_requests = cache.get(rate_key, 0)

        if current_requests >= max_requests:
            return False, max_requests, window_seconds

        # زيادة العداد
        cache.set(rate_key, current_requests + 1, window_seconds)

        return True, max_requests - current_requests - 1, window_seconds

    except Exception as e:
        logger.error(f"Rate limit check error: {str(e)}")
        return True, max_requests, window_seconds  # السماح في حالة الخطأ


def get_client_ip(request):
    """الحصول على IP address للمستخدم"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def save_search_history(request, query, search_type, results_count):
    """حفظ تاريخ البحث"""
    try:
        if query and len(query.strip()) >= 2:  # حفظ البحثات المفيدة فقط
            SearchHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                query=query.strip(),
                search_type=search_type,
                results_count=results_count,
                ip_address=get_client_ip(request)
            )

            # تحديث الكلمات الشائعة
            popular, created = PopularSearch.objects.get_or_create(
                query=query.strip().lower(),
                defaults={'search_count': 1}
            )
            if not created:
                popular.search_count += 1
                popular.save()

    except Exception as e:
        logger.error(f"Error saving search history: {str(e)}")

User = get_user_model()


class SearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class UserSearchView(generics.ListAPIView):
    """البحث السريع عن المستخدمين"""
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]
    pagination_class = SearchPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()

        if not query or len(query) < 2:
            return User.objects.none()

        # البحث في username, first_name, last_name
        return User.objects.select_related('profile').prefetch_related(
            'followers'
        ).filter(
            Q(username__icontains=query) |
            Q(profile__first_name__icontains=query) |
            Q(profile__last_name__icontains=query)
        ).annotate(
            followers_count=Count('followers')
        ).order_by('-followers_count', 'username')

    def list(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({
                'error': 'يرجى إدخال كلمة البحث'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(query) < 2:
            return Response({
                'error': 'يجب أن تكون كلمة البحث أكثر من حرف واحد'
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().list(request, *args, **kwargs)


class TagSearchSerializer(TripTagSerializer):
    """Serializer محسن لنتائج البحث عن التاجز"""
    trips_count = serializers.SerializerMethodField()
    trips_url = serializers.SerializerMethodField()

    class Meta:
        model = TripTag
        fields = ['tripTag', 'trips_count', 'trips_url']

    def get_trips_count(self, obj):
        return TripTag.objects.filter(tripTag__iexact=obj.tripTag).count()

    def get_trips_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/trip/tags/{obj.tripTag}/trips/')
        return f'/api/trip/tags/{obj.tripTag}/trips/'


class TagSearchView(generics.ListAPIView):
    """البحث السريع عن التاجز"""
    serializer_class = TagSearchSerializer
    permission_classes = [AllowAny]
    pagination_class = SearchPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()

        if not query or len(query) < 2:
            return TripTag.objects.none()

        # البحث في أسماء التاجز مع تجميع النتائج المتشابهة
        return TripTag.objects.filter(
            tripTag__icontains=query
        ).values('tripTag').annotate(
            trips_count=Count('id')
        ).order_by('-trips_count', 'tripTag')

    def list(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({
                'error': 'يرجى إدخال كلمة البحث'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(query) < 2:
            return Response({
                'error': 'يجب أن تكون كلمة البحث أكثر من حرف واحد'
            }, status=status.HTTP_400_BAD_REQUEST)

        # تخصيص الاستجابة للتاجز
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            # تحويل النتائج لصيغة مناسبة للـ serializer
            tags_data = []
            for item in page:
                tag_obj = TripTag(tripTag=item['tripTag'])
                tags_data.append(tag_obj)

            serializer = self.get_serializer(tags_data, many=True)
            return self.get_paginated_response(serializer.data)

        # بدون pagination
        tags_data = []
        for item in queryset:
            tag_obj = TripTag(tripTag=item['tripTag'])
            tags_data.append(tag_obj)

        serializer = self.get_serializer(tags_data, many=True)
        return Response(serializer.data)


class UnifiedSearchView(APIView):
    """البحث الموحد في المستخدمين والتاجز"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()

            if not query:
                return Response({
                    'error': 'يرجى إدخال كلمة البحث',
                    'error_code': 'MISSING_QUERY'
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(query) < 2:
                return Response({
                    'error': 'يجب أن تكون كلمة البحث أكثر من حرف واحد',
                    'error_code': 'QUERY_TOO_SHORT'
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(query) > 100:
                return Response({
                    'error': 'كلمة البحث طويلة جداً',
                    'error_code': 'QUERY_TOO_LONG'
                }, status=status.HTTP_400_BAD_REQUEST)

                # البحث عن المستخدمين
            users = User.objects.select_related('profile').prefetch_related(
                'followers'
            ).filter(
                Q(username__icontains=query) |
                Q(profile__first_name__icontains=query) |
                Q(profile__last_name__icontains=query)
            ).annotate(
                followers_count=Count('followers')
            ).order_by('-followers_count')[:10]  # أول 10 نتائج

            # البحث عن التاجز
            tags = TripTag.objects.filter(
                tripTag__icontains=query
            ).values('tripTag').annotate(
                trips_count=Count('id')
            ).order_by('-trips_count')[:10]  # أول 10 نتائج

            # تحضير النتائج
            results = []

            # إضافة المستخدمين
            for user in users:
                user_data = {
                    'type': 'user',
                    'id': user.id,
                    'username': user.username,
                    'profile_url': request.build_absolute_uri(f'/api/accounts/users/{user.id}/profile/'),
                    'followers_count': user.followers_count,
                    'avatar': None
                }

                # إضافة الصورة الشخصية إذا وجدت
                if hasattr(user, 'profile') and user.profile and user.profile.avatar:
                    user_data['avatar'] = request.build_absolute_uri(user.profile.avatar.url)

                # إضافة الاسم الكامل إذا وجد
                if hasattr(user, 'profile') and user.profile:
                    if user.profile.first_name or user.profile.last_name:
                        user_data['full_name'] = f"{user.profile.first_name} {user.profile.last_name}".strip()

                results.append(user_data)

            # إضافة التاجز
            for tag in tags:
                tag_data = {
                    'type': 'tag',
                    'name': tag['tripTag'],
                    'trips_url': request.build_absolute_uri(f'/api/trip/tags/{tag["tripTag"]}/trips/'),
                    'trips_count': tag['trips_count']
                }
                results.append(tag_data)

            # ترتيب النتائج حسب الشعبية
            results.sort(key=lambda x: (
                x.get('followers_count', 0) if x['type'] == 'user'
                else x.get('trips_count', 0)
            ), reverse=True)

            response_data = {
                'query': query,
                'results': results,
                'total_results': len(results),
                'users_count': len([r for r in results if r['type'] == 'user']),
                'tags_count': len([r for r in results if r['type'] == 'tag'])
            }

            # حفظ تاريخ البحث
            save_search_history(request, query, 'unified', len(results))

            return Response(response_data)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return Response({
                'error': 'حدث خطأ أثناء البحث',
                'error_code': 'SEARCH_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickSearchView(APIView):
    """البحث السريع للكتابة المباشرة (Type as you type)"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # فحص rate limiting (120 طلب في الدقيقة للبحث السريع)
            is_allowed, remaining, window = check_rate_limit(
                request, 'quick_search', max_requests=120, window_seconds=60
            )

            if not is_allowed:
                return Response({
                    'error': 'تم تجاوز الحد المسموح للبحث',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': window
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            query = request.query_params.get('q', '').strip()

            # للبحث السريع، نقبل حرف واحد على الأقل
            if not query:
                return Response({
                    'query': '',
                    'suggestions': [],
                    'quick_results': []
                })

            if len(query) > 50:
                return Response({
                    'error': 'كلمة البحث طويلة جداً',
                    'error_code': 'QUERY_TOO_LONG'
                }, status=status.HTTP_400_BAD_REQUEST)

            # التحقق من الـ cache أولاً
            cache_key = generate_cache_key('quick_search', query, 'quick')
            cached_results = get_cached_search_results(cache_key)

            if cached_results:
                return Response(cached_results)

            # نتائج سريعة محدودة (5 من كل نوع)
            users = User.objects.select_related('profile').filter(
                Q(username__istartswith=query) |  # istartswith أسرع من icontains
                Q(profile__first_name__istartswith=query) |
                Q(profile__last_name__istartswith=query)
            ).annotate(
                followers_count=Count('followers')
            ).order_by('-followers_count')[:5]

            tags = TripTag.objects.filter(
                tripTag__istartswith=query
            ).values('tripTag').annotate(
                trips_count=Count('id')
            ).order_by('-trips_count')[:5]

            # تحضير النتائج السريعة
            quick_results = []

            # إضافة المستخدمين
            for user in users:
                user_data = {
                    'type': 'user',
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.username,
                    'avatar': None,
                    'followers_count': user.followers_count
                }

                # إضافة الاسم الكامل كـ display_name
                if hasattr(user, 'profile') and user.profile:
                    if user.profile.first_name or user.profile.last_name:
                        user_data['display_name'] = f"{user.profile.first_name} {user.profile.last_name}".strip()

                    if user.profile.avatar:
                        user_data['avatar'] = request.build_absolute_uri(user.profile.avatar.url)

                quick_results.append(user_data)

            # إضافة التاجز
            for tag in tags:
                tag_data = {
                    'type': 'tag',
                    'name': tag['tripTag'],
                    'display_name': f"#{tag['tripTag']}",
                    'trips_count': tag['trips_count']
                }
                quick_results.append(tag_data)

            response_data = {
                'query': query,
                'quick_results': quick_results,
                'total_results': len(quick_results),
                'has_more': len(users) == 5 or len(tags) == 5
            }

            # حفظ النتائج في الـ cache (دقيقتين للبحث السريع)
            set_cached_search_results(cache_key, response_data, timeout=120)

            return Response(response_data)

        except Exception as e:
            logger.error(f"Quick search error: {str(e)}")
            return Response({
                'error': 'حدث خطأ أثناء البحث السريع',
                'error_code': 'QUICK_SEARCH_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchSuggestionsView(APIView):
    """اقتراحات البحث المبنية على الشعبية"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()
            limit = min(int(request.query_params.get('limit', 10)), 20)

            suggestions = []

            if query:
                # اقتراحات المستخدمين (أشهر المستخدمين الذين يبدأ اسمهم بالحروف المكتوبة)
                user_suggestions = User.objects.select_related('profile').filter(
                    Q(username__istartswith=query) |
                    Q(profile__first_name__istartswith=query) |
                    Q(profile__last_name__istartswith=query)
                ).annotate(
                    followers_count=Count('followers')
                ).order_by('-followers_count')[:limit//2]

                for user in user_suggestions:
                    display_name = user.username
                    if hasattr(user, 'profile') and user.profile:
                        if user.profile.first_name or user.profile.last_name:
                            display_name = f"{user.profile.first_name} {user.profile.last_name}".strip()

                    suggestions.append({
                        'text': user.username,
                        'display_text': display_name,
                        'type': 'user',
                        'user_id': user.id,
                        'popularity': user.followers_count
                    })

                # اقتراحات التاجز (أشهر التاجز)
                tag_suggestions = TripTag.objects.filter(
                    tripTag__istartswith=query
                ).values('tripTag').annotate(
                    trips_count=Count('id')
                ).order_by('-trips_count')[:limit//2]

                for tag in tag_suggestions:
                    suggestions.append({
                        'text': tag['tripTag'],
                        'display_text': f"#{tag['tripTag']}",
                        'type': 'tag',
                        'popularity': tag['trips_count']
                    })

            else:
                # اقتراحات عامة (أشهر المستخدمين والتاجز)
                popular_users = User.objects.select_related('profile').annotate(
                    followers_count=Count('followers')
                ).order_by('-followers_count')[:limit//2]

                for user in popular_users:
                    display_name = user.username
                    if hasattr(user, 'profile') and user.profile:
                        if user.profile.first_name or user.profile.last_name:
                            display_name = f"{user.profile.first_name} {user.profile.last_name}".strip()

                    suggestions.append({
                        'text': user.username,
                        'display_text': display_name,
                        'type': 'user',
                        'user_id': user.id,
                        'popularity': user.followers_count
                    })

                popular_tags = TripTag.objects.values('tripTag').annotate(
                    trips_count=Count('id')
                ).order_by('-trips_count')[:limit//2]

                for tag in popular_tags:
                    suggestions.append({
                        'text': tag['tripTag'],
                        'display_text': f"#{tag['tripTag']}",
                        'type': 'tag',
                        'popularity': tag['trips_count']
                    })

            # ترتيب الاقتراحات حسب الشعبية
            suggestions.sort(key=lambda x: x['popularity'], reverse=True)

            return Response({
                'query': query,
                'suggestions': suggestions[:limit]
            })

        except Exception as e:
            logger.error(f"Suggestions error: {str(e)}")
            return Response({
                'error': 'حدث خطأ في الاقتراحات',
                'error_code': 'SUGGESTIONS_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchHistoryView(generics.ListAPIView):
    """تاريخ البحث للمستخدم المسجل"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SearchPagination

    def get_queryset(self):
        return SearchHistory.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:
                history_data = []
                for item in page:
                    history_data.append({
                        'query': item.query,
                        'search_type': item.search_type,
                        'results_count': item.results_count,
                        'created_at': item.created_at
                    })

                return self.get_paginated_response(history_data)

            # بدون pagination
            history_data = []
            for item in queryset:
                history_data.append({
                    'query': item.query,
                    'search_type': item.search_type,
                    'results_count': item.results_count,
                    'created_at': item.created_at
                })

            return Response(history_data)

        except Exception as e:
            logger.error(f"Search history error: {str(e)}")
            return Response({
                'error': 'حدث خطأ في تاريخ البحث',
                'error_code': 'HISTORY_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClearSearchHistoryView(APIView):
    """مسح تاريخ البحث"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        try:
            deleted_count = SearchHistory.objects.filter(
                user=request.user
            ).delete()[0]

            return Response({
                'message': f'تم مسح {deleted_count} عنصر من تاريخ البحث',
                'deleted_count': deleted_count
            })

        except Exception as e:
            logger.error(f"Clear history error: {str(e)}")
            return Response({
                'error': 'حدث خطأ أثناء مسح التاريخ',
                'error_code': 'CLEAR_HISTORY_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PopularSearchesView(APIView):
    """الكلمات الشائعة في البحث"""
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = min(int(request.query_params.get('limit', 10)), 50)

            popular_searches = PopularSearch.objects.order_by(
                '-search_count', '-last_searched'
            )[:limit]

            popular_data = []
            for search in popular_searches:
                popular_data.append({
                    'query': search.query,
                    'search_count': search.search_count,
                    'last_searched': search.last_searched
                })

            return Response({
                'popular_searches': popular_data,
                'total_count': len(popular_data)
            })

        except Exception as e:
            logger.error(f"Popular searches error: {str(e)}")
            return Response({
                'error': 'حدث خطأ في البحثات الشائعة',
                'error_code': 'POPULAR_SEARCHES_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



