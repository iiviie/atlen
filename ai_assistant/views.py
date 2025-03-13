from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .services import GeminiService
from .serializers import ChatMessageSerializer, GenerateItineraryRequestSerializer, ChatRequestSerializer
from trip.models import Trip, Itinerary, ItineraryItem
from trip.permissions import IsTripParticipant
from django.utils.timezone import make_aware
from datetime import datetime
from .models import ChatMessage
import asyncio

class AIAssistantViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsTripParticipant]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_service = GeminiService()

    @action(detail=False, methods=['post'])
    def generate_itinerary(self, request, trip_pk=None):
        try:
            trip = get_object_or_404(Trip, id=trip_pk)
            
            trip_data = {
                'location': str(trip.location),
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'companions': list(trip.companions.all()),
            }
            
            itinerary_data = asyncio.run(self.ai_service.generate_itinerary(trip_data))
            
            if not itinerary_data or 'days' not in itinerary_data:
                return Response(
                    {"error": "Failed to generate valid itinerary format"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            itinerary = Itinerary.objects.create(
                trip=trip,
                title=f"AI Generated Itinerary - {trip.start_date}"
            )
            
            try:
                for day in itinerary_data['days']:
                    for activity in day['activities']:
                        time = datetime.strptime(activity['time'], '%H:%M').time()
                        ItineraryItem.objects.create(
                            itinerary=itinerary,
                            time=time,
                            activity=f"{activity['activity']} at {activity['location']}"
                        )
            except (KeyError, ValueError) as e:
                itinerary.delete()
                return Response(
                    {"error": f"Invalid activity data format: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({"message": "Itinerary generated successfully"})
            
        except Exception as e:
            return Response(
                {"error": f"Error generating itinerary: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def chat(self, request, trip_pk=None):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        trip = get_object_or_404(Trip, id=trip_pk)
        message = serializer.validated_data['message']
        
        chat_history = list(ChatMessage.objects.filter(
            trip=trip
        ).order_by('-created_at')[:5])
        
        history = [
            {'user': msg.message, 'assistant': msg.response}
            for msg in reversed(chat_history)
        ]
        
        # Run async code in sync context
        response = asyncio.run(self.ai_service.chat_with_assistant(message, history))
        
        chat_message = ChatMessage.objects.create(
            user=request.user,
            trip=trip,
            message=message,
            response=response
        )
        
        serialized_data = ChatMessageSerializer(chat_message).data
        return Response(serialized_data)
