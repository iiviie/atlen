from django.urls import path, include
from rest_framework_nested import routers
from .views import BudgetViewSet
from trip.urls import router as trip_router

# Create nested router for trip-level budget resources
trip_nested_router = routers.NestedDefaultRouter(
    trip_router,
    'trips',
    lookup='trip'
)

trip_nested_router.register(
    r'budget',
    BudgetViewSet,
    basename='trip-budget'
)

app_name = 'expenses'

urlpatterns = [
    path('', include(trip_nested_router.urls)),
] 