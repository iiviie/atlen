from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightViewSet

router = DefaultRouter()
router.register(r'flights', FlightViewSet, basename='flight')

app_name = 'flights'

urlpatterns = [
    path('', include(router.urls)),
] 