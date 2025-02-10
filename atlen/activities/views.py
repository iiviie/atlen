from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from typing import List
from .serializers import NearbyPlacesSerializer, PlacePhotoSerializer  
from .services import GooglePlacesService

class PlacesViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.places_service = GooglePlacesService()

    @extend_schema(
        request=NearbyPlacesSerializer,
        description="Search for nearby places based on location"
    )
    @action(detail=False, methods=['get'])
    def nearby_search(self, request):
        serializer = NearbyPlacesSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        types = serializer.validated_data.get('types')
        if isinstance(types, str):
            types = [t.strip() for t in types.split(',')]
        
        results = self.places_service.search_nearby_places(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            radius=serializer.validated_data['radius'],
            types=types
        )
        
        if results is None:
            return Response(
                {"error": "Failed to fetch nearby places"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return Response(results)

    @extend_schema(
        description="Get detailed information about a specific place"
    )
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        if not pk:
            return Response(
                {"error": "Place ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = self.places_service.get_place_details(pk)
        
        if results is None:
            return Response(
                {"error": "Failed to fetch place details"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return Response(results)

    @extend_schema(
        request=PlacePhotoSerializer,
        description="Get photo URL for a place"
    )
    @action(detail=False, methods=['get'])
    def photo(self, request):
        serializer = PlacePhotoSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        photo_url = self.places_service.get_photo_url(
            serializer.validated_data['photo_reference'],
            serializer.validated_data['max_width']
        )
        
        if photo_url is None:
            return Response(
                {"error": "Failed to fetch photo URL"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return Response({"url": photo_url})