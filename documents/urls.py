from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, TripDocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(
    r'trips/(?P<trip_pk>[^/.]+)/documents',
    TripDocumentViewSet,
    basename='trip-document'
)

app_name = 'documents'

urlpatterns = [
    path('', include(router.urls)),
] 