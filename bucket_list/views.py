from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count
from .models import BucketListItem
from .serializers import BucketListItemSerializer
from django.db import models

class BucketListViewSet(viewsets.ModelViewSet):
    serializer_class = BucketListItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BucketListItem.objects.filter(
            user=self.request.user
        ).select_related('location', 'associated_trip')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        item = self.get_object()
        item.status = 'COMPLETED'
        item.completed_at = timezone.now()
        item.save()
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = BucketListItem.objects.filter(user=request.user).aggregate(
            total_items=Count('id'),
            completed_items=Count('id', filter=models.Q(status='COMPLETED')),
            in_progress_items=Count('id', filter=models.Q(status='IN_PROGRESS')),
            pending_items=Count('id', filter=models.Q(status='PENDING')),
            high_priority=Count('id', filter=models.Q(priority='HIGH')),
        )
        return Response(stats)
