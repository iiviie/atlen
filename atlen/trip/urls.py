from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    TripViewSet, CompanionViewSet, ChecklistViewSet,
    ItineraryViewSet, ItineraryItemViewSet, TripStatsViewSet
)

# Create the main router
router = routers.DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')

# Create router for trip-level nested resources
trip_router = routers.NestedDefaultRouter(router, r'trips', lookup='trip')
trip_router.register(r'companions', CompanionViewSet, basename='trip-companions')
trip_router.register(r'checklist', ChecklistViewSet, basename='trip-checklist')
trip_router.register(r'itineraries', ItineraryViewSet, basename='trip-itineraries')

# Create router for itinerary-level nested resources
itinerary_router = routers.NestedDefaultRouter(trip_router, r'itineraries', lookup='itinerary')
itinerary_router.register(r'items', ItineraryItemViewSet, basename='itinerary-items')

# Create router for trip stats
router.register(r'stats', TripStatsViewSet, basename='trip-stats')

app_name = 'trips'

urlpatterns = [
    path('', include(router.urls)),
    path('', include(trip_router.urls)),
    path('', include(itinerary_router.urls)),
]