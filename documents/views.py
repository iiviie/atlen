from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Document, TripDocument
from .serializers import DocumentSerializer, TripDocumentSerializer
from .services import S3Service
from trip.permissions import IsTripParticipant
from trip.models import Trip

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def upload_url(self, request):
        """Generate a pre-signed URL for direct S3 upload"""
        file_name = request.query_params.get('file_name')
        if not file_name:
            return Response(
                {'error': 'file_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        s3_service = S3Service()
        upload_url = s3_service.generate_presigned_post(f"documents/user/{file_name}")
        return Response(upload_url)

    @action(detail=False, methods=['get'])
    def expiring_documents(self, request):
        """Get documents expiring in the next 30 days"""
        from django.utils import timezone
        from datetime import timedelta
        
        thirty_days = timezone.now().date() + timedelta(days=30)
        documents = self.get_queryset().filter(
            expiry_date__lte=thirty_days,
            expiry_date__gte=timezone.now().date()
        )
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

class TripDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = TripDocumentSerializer
    permission_classes = [IsAuthenticated, IsTripParticipant]
    
    def get_queryset(self):
        return TripDocument.objects.filter(
            trip_id=self.kwargs['trip_pk']
        )

    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, id=self.kwargs['trip_pk'])
        serializer.save(trip=trip)

    @action(detail=False, methods=['get'])
    def upload_url(self, request, trip_pk=None):
        """Generate a pre-signed URL for direct S3 upload"""
        file_name = request.query_params.get('file_name')
        if not file_name:
            return Response(
                {'error': 'file_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        s3_service = S3Service()
        upload_url = s3_service.generate_presigned_post(
            f"documents/trips/{trip_pk}/{file_name}"
        )
        return Response(upload_url)
