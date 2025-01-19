from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.transaction import atomic
from trip.models import Trip
from trip.permissions import IsTripParticipant
from .models import GroupChat, Message, Bill, BillSplit
from .serializers import (
    GroupChatSerializer, MessageSerializer,
    BillSerializer, BillSplitSerializer
)

# Create your views here.

class GroupChatViewSet(viewsets.ModelViewSet):
    serializer_class = GroupChatSerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]
    
    def get_queryset(self):
        return GroupChat.objects.filter(
            trip_id=self.kwargs['trip_pk']
        )

    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, id=self.kwargs['trip_pk'])
        serializer.save(trip=trip)

    @action(detail=True, methods=['get'])
    def messages(self, request, trip_pk=None, pk=None):
        chat = self.get_object()
        messages = chat.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]
    
    def get_queryset(self):
        return Bill.objects.filter(
            trip_id=self.kwargs['trip_pk']
        )

    @atomic
    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, id=self.kwargs['trip_pk'])
        split_details = serializer.validated_data.pop('split_details', [])
        
        # Create the bill
        bill = serializer.save(
            trip=trip,
            paid_by=self.request.user
        )
        
        # If no split details provided, split equally among all participants
        if not split_details:
            participants = [trip.creator] + list(trip.companions.all())
            split_amount = bill.amount / len(participants)
            split_details = [
                {'user_id': str(user.id), 'amount': split_amount}
                for user in participants
            ]
        
        # Create the splits
        for split in split_details:
            BillSplit.objects.create(
                bill=bill,
                user_id=split['user_id'],
                amount=split['amount'],
                is_paid=(split['user_id'] == str(self.request.user.id))
            )

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, trip_pk=None, pk=None):
        bill = self.get_object()
        user_id = request.data.get('user_id')
        
        split = get_object_or_404(
            BillSplit, 
            bill=bill, 
            user_id=user_id
        )
        
        split.is_paid = True
        split.paid_at = timezone.now()
        split.save()
        
        serializer = BillSplitSerializer(split)
        return Response(serializer.data)
