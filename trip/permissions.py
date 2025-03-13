from rest_framework import permissions
from trip.models import Trip, ChecklistItem, ItineraryItem
class IsTripParticipant(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user and request.user.is_authenticated
            
        return True  

    def has_object_permission(self, request, view, obj):
        trip = self._get_trip_object(obj)
        if not trip:
            return False

        if trip.creator == request.user:
            return True

        if request.user in trip.companions.all():
            if request.method in permissions.SAFE_METHODS:
                return True
                
            if isinstance(obj, (ChecklistItem, ItineraryItem)):
                return True
                
        return False

    def _get_trip_object(self, obj):
        if hasattr(obj, 'trip'):
            return obj.trip
        elif hasattr(obj, 'itinerary'):
            return obj.itinerary.trip
        elif type(obj).__name__ == 'Trip':
            return obj
        return None

class IsCreatorOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            trip = self._get_trip_object(obj)
            return (
                request.user == trip.creator or 
                request.user in trip.companions.all()
            )

        trip = self._get_trip_object(obj)
        return request.user == trip.creator

    def _get_trip_object(self, obj):
        if hasattr(obj, 'trip'):
            return obj.trip
        elif hasattr(obj, 'itinerary'):
            return obj.itinerary.trip
        elif type(obj).__name__ == 'Trip':
            return obj
        return None

class CanManageCompanions(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if view.action == 'list':
            return True
            
        trip_pk = view.kwargs.get('trip_pk')
        if trip_pk:
            trip = Trip.objects.filter(pk=trip_pk).first()
            if trip:
                return request.user == trip.creator
                
        return False