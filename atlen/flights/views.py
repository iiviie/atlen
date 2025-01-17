from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import FlightSearchService
from .serializers import FlightSearchSerializer, DestinationSearchSerializer
from drf_spectacular.utils import extend_schema

class FlightViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flight_service = FlightSearchService()

    @extend_schema(
        request=DestinationSearchSerializer,
        description="Search for airports and cities"
    )
    @action(detail=False, methods=['get'])
    def search_destinations(self, request):
        serializer = DestinationSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        results = self.flight_service.search_destinations(
            query=serializer.validated_data['query']
        )
        
        if results is None:
            return Response(
                {"error": "Failed to fetch destinations"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        return Response(results)

    @extend_schema(
        request=FlightSearchSerializer,
        description="Search for flights"
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        serializer = FlightSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        mapped_data = {
            'from_id': serializer.validated_data['fromId'],
            'to_id': serializer.validated_data['toId'],
            'depart_date': serializer.validated_data['departDate'],
            'return_date': serializer.validated_data.get('returnDate'),
            'adults': serializer.validated_data.get('adults', 1),
            'children': serializer.validated_data.get('children', '0,17'),
            'cabin_class': serializer.validated_data.get('cabinClass', 'ECONOMY'),
            'currency_code': serializer.validated_data.get('currency_code', 'AED'),
            'sort': serializer.validated_data.get('sort', 'BEST'),
            'page_no': serializer.validated_data.get('pageNo', 1)
        }

        results = self.flight_service.search_flights(**mapped_data)
        
        if results is None:
            return Response(
                {"error": "Failed to fetch flights"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        return Response(results)
