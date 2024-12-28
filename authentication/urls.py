# urls.py
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    VerifyOTPView,
    ForgotPasswordView,
    ResetPasswordView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

app_name = 'authentication'

# Authentication URL patterns
urlpatterns = [
    # Basic authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # Password management endpoints
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # JWT token management endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    
    # API documentation endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='authentication:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='authentication:schema'), name='redoc'),
]