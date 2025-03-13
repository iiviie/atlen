from rest_framework import serializers
from .models import Document, TripDocument
from trip.serializers import TripListSerializer

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'file',
            'file_url', 'expiry_date', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'file_url', 'created_at']
        
    def get_file_url(self, obj):
        from .services import S3Service
        if obj.file:
            s3_service = S3Service()
            return s3_service.generate_presigned_url(str(obj.file))
        return None

class TripDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    associated_trip = TripListSerializer(source='trip', read_only=True)
    
    class Meta:
        model = TripDocument
        fields = [
            'id', 'title', 'document_type', 'file',
            'file_url', 'notes', 'associated_trip',
            'created_at'
        ]
        read_only_fields = ['id', 'file_url', 'created_at']
        
    def get_file_url(self, obj):
        from .services import S3Service
        if obj.file:
            s3_service = S3Service()
            return s3_service.generate_presigned_url(str(obj.file))
        return None 