from rest_framework.routers import DefaultRouter
from .views import HotelViewSet

app_name = "hotels"

router = DefaultRouter()
router.register(r"hotels", HotelViewSet, basename="hotels")

urlpatterns = router.urls
