from rest_framework import serializers
from .models import ChatMessage
from trip.serializers import TripListSerializer

class ChatMessageSerializer(serializers.ModelSerializer):
    trip = TripListSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message', 'response',
            'trip', 'created_at'
        ]
        read_only_fields = ['id', 'response', 'created_at']

class GenerateItineraryRequestSerializer(serializers.Serializer):
    preferences = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    budget_level = serializers.ChoiceField(
        choices=['BUDGET', 'MODERATE', 'LUXURY'],
        required=False
    )
    pace = serializers.ChoiceField(
        choices=['RELAXED', 'MODERATE', 'INTENSE'],
        required=False
    )

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True) 