from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from trip.models import Trip, ChecklistItem, Itinerary, ItineraryItem, ItineraryDay
from group_travel.models import GroupChat
from trip.serializers import (
    TripListSerializer, TripDetailSerializer, ChecklistItemSerializer,
    ItinerarySerializer, ItineraryItemSerializer, TripStatsSerializer,
    UserBasicSerializer, ItineraryDaySerializer
)
from trip.permissions import *

User = get_user_model()

class TripViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTripParticipant, IsCreatorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location__name', 'location__city']
    ordering_fields = ['start_date', 'created_at', 'status']
    ordering = ['-start_date']

    def get_queryset(self):
        return Trip.objects.filter(
            Q(creator=self.request.user) | Q(companions=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return TripListSerializer
        return TripDetailSerializer

    def perform_create(self, serializer):
        trip = serializer.save(creator=self.request.user)
        GroupChat.objects.create(trip=trip)

class CompanionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsTripParticipant]

    def get_trip(self, trip_pk):
        return get_object_or_404(Trip, pk=trip_pk)

    def list(self, request, trip_pk=None):
        trip = self.get_trip(trip_pk)
        self.check_object_permissions(request, trip)
        serializer = UserBasicSerializer(trip.companions.all(), many=True)
        return Response(serializer.data)

    def create(self, request, trip_pk=None):
        trip = self.get_trip(trip_pk)
        self.check_object_permissions(request, trip)
        
        email = request.data.get('email', '').lower()
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            if user == request.user:
                return Response(
                    {'error': 'Cannot add yourself as a companion'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user in trip.companions.all():
                return Response(
                    {'error': 'User is already a companion'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            trip.companions.add(user)
            serializer = UserBasicSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, trip_pk=None, pk=None):
        trip = self.get_trip(trip_pk)
        self.check_object_permissions(request, trip)
        
        companion = get_object_or_404(User, pk=pk)
        if companion == trip.creator:
            return Response(
                {'error': 'Cannot remove the trip creator'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        trip.companions.remove(companion)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChecklistViewSet(viewsets.ModelViewSet):
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]

    def get_queryset(self):
        return ChecklistItem.objects.filter(
            trip_id=self.kwargs['trip_pk']
        ).order_by('created_at')

    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, id=self.kwargs['trip_pk'])
        serializer.save(trip=trip)

class ItineraryViewSet(viewsets.ModelViewSet):
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]

    def get_queryset(self):
        return Itinerary.objects.filter(
            trip_id=self.kwargs['trip_pk']
        ).order_by('created_at')

    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, id=self.kwargs['trip_pk'])
        serializer.save(trip=trip)

class ItineraryDayViewSet(viewsets.ModelViewSet):
    serializer_class = ItineraryDaySerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]

    def get_queryset(self):
        return ItineraryDay.objects.filter(
            itinerary_id=self.kwargs['itinerary_pk'],
            itinerary__trip_id=self.kwargs['trip_pk']
        ).order_by('date')

    def perform_create(self, serializer):
        itinerary = get_object_or_404(
            Itinerary,
            id=self.kwargs['itinerary_pk'],
            trip_id=self.kwargs['trip_pk']
        )
        serializer.save(itinerary=itinerary)

class ItineraryItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItineraryItemSerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]

    def get_queryset(self):
        return ItineraryItem.objects.filter(
            day_id=self.kwargs['day_pk'],
            day__itinerary_id=self.kwargs['itinerary_pk'],
            day__itinerary__trip_id=self.kwargs['trip_pk']
        ).order_by('time')

    def perform_create(self, serializer):
        day = get_object_or_404(
            ItineraryDay,
            id=self.kwargs['day_pk'],
            itinerary_id=self.kwargs['itinerary_pk'],
            itinerary__trip_id=self.kwargs['trip_pk']
        )
        serializer.save(day=day)

class TripStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        trips = Trip.objects.filter(
            Q(creator=request.user) | Q(companions=request.user)
        ).distinct()

        most_visited = trips.values('location__city')\
            .annotate(count=Count('id'))\
            .order_by('-count')\
            .first()

        stats = {
            'total_trips': trips.count(),
            'completed_trips': trips.filter(status='COMPLETED').count(),
            'planned_trips': trips.filter(status='PLANNED').count(),
            'ongoing_trips': trips.filter(status='ONGOING').count(),
            'unique_destinations': trips.values('location__city').distinct().count(),
            'total_companions': trips.aggregate(
                total=Count('companions', distinct=True)
            )['total'],
            'most_visited_city': most_visited['location__city'] if most_visited else None
        }

        serializer = TripStatsSerializer(stats)
        return Response(serializer.data)