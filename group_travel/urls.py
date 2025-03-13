from django.urls import path, include
from rest_framework_nested import routers
from .views import GroupChatViewSet, BillViewSet
from trip.urls import router as trip_router  

trip_nested_router = routers.NestedDefaultRouter(
    trip_router,
    'trips',
    lookup='trip'
)

trip_nested_router.register(
    r'chat',
    GroupChatViewSet,
    basename='trip-chat'
)
trip_nested_router.register(
    r'bills',
    BillViewSet,
    basename='trip-bills'
)

app_name = 'group_travel'

urlpatterns = [
    path('', include(trip_nested_router.urls)),
] 