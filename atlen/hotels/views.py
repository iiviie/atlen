from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .services import HotelServices
from .serializers import HotelSearchSerializer


class HotelViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hotel_service = HotelServices()

    @extend_schema(description="Search for Hotels in a specific location")
    @action(detail=False, methods=["get"])
    def search_all_hotels(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response(
                {"error": "Query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            results = self.hotel_service.search_hotels(query)
        except Exception as e:
            return Response(
                {"error": f"str({e})"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if results is None:
            return Response(
                {"error": "Failed to fetch destinations"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(results)

    @extend_schema(description="Get detailed information about a specific hotel")
    @action(detail=True, methods=["get"])
    def hotel_details(self, request, pk=None):
        arrival_date = request.query_params.get("arrival_date")
        departure_date = request.query_params.get("departure_date")

        if not all([arrival_date, departure_date]):
            return Response(
                {"error": "Both arrival_date and departure_date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = self.hotel_service.get_hotel_details(
            hotel_id=pk, arrival_date=arrival_date, departure_date=departure_date
        )

        if results is None:
            return Response(
                {"error": "Failed to fetch hotel details"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(results)

    @extend_schema(
        request=HotelSearchSerializer,
        description="Search for hotels based on location and dates",
    )
    @action(detail=False, methods=["get"])
    def search(self, request):
        serializer = HotelSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        children_age = None
        if serializer.validated_data.get("children_age"):
            try:
                children_age = [
                    int(age)
                    for age in serializer.validated_data["children_age"].split(",")
                    if age.strip()
                ]
            except ValueError:
                return Response(
                    {"error": "Invalid children_age format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        results = self.hotel_service.search_available_hotels(
            serializer.validated_data["dest_id"],
            serializer.validated_data["adults"],
            children_age,
            serializer.validated_data["arrival_date"].isoformat(),
            serializer.validated_data["departure_date"].isoformat(),
        )

        if results is None:
            return Response(
                {"error": "Failed to fetch hotels"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(results)
