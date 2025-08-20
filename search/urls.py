from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Search endpoints
    path('users/', views.UserSearchView.as_view(), name='user_search'),
    path('tags/', views.TagSearchView.as_view(), name='tag_search'),
    path('', views.UnifiedSearchView.as_view(), name='unified_search'),

    # Real-time search
    path('quick/', views.QuickSearchView.as_view(), name='quick_search'),
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),

    # Search history
    path('history/', views.SearchHistoryView.as_view(), name='search_history'),
    path('history/clear/', views.ClearSearchHistoryView.as_view(), name='clear_search_history'),

    # Popular searches
    path('popular/', views.PopularSearchesView.as_view(), name='popular_searches'),
]
