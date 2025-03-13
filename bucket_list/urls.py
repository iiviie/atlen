from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BucketListViewSet

router = DefaultRouter()
router.register(r'bucket-list', BucketListViewSet, basename='bucket-list')

app_name = 'bucket_list'

urlpatterns = [
    path('', include(router.urls)),
] 