from rest_framework.routers import DefaultRouter
from .views import PlacesViewSet

app_name = 'activities'

router = DefaultRouter()
router.register(r'activities', PlacesViewSet, basename='activities')

urlpatterns = router.urls