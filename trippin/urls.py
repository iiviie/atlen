from django.urls import path
from django.urls import include
from django.contrib import admin
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/accounts/", include("accounts.urls")),
    path('', include('social_django.urls', namespace='social')),
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),

    # drf-spectacular URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    
]
