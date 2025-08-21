from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Rahala Tourism API",
        default_version='v1',
        description="API Documentation for Rahala Tourism Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="anwerahmedanwer16@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # API routes
    path("api/accounts/", include("accounts.urls")),
    path("api/trip/", include("trip.urls")),
    path("api/interactions/", include("interactions.urls")),
    path("api/search/", include("search.urls")),
    path("api/promotions/", include("promotions.urls")),

    # social auth
    path("auth/", include("social_django.urls", namespace="social")),

    # Swagger + Redoc
    re_path(r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0),
         name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0),
         name="schema-redoc"),
]

# static/media in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
