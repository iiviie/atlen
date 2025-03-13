from rest_framework import serializers
from .models import BucketListItem
from trip.serializers import LocationSerializer, TripListSerializer

class BucketListItemSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False)
    associated_trip = TripListSerializer(read_only=True)
    trip_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = BucketListItem
        fields = [
            'id', 'title', 'description', 'location',
            'priority', 'status', 'target_date',
            'completed_at', 'associated_trip', 'trip_id',
            'created_at'
        ]
        read_only_fields = ['id', 'completed_at', 'created_at']

    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        trip_id = validated_data.pop('trip_id', None)
        
        if location_data:
            from trip.models import Location
            from django.contrib.gis.geos import Point
            
            latitude = location_data.pop('latitude')
            longitude = location_data.pop('longitude')
            location_data['point'] = Point(longitude, latitude, srid=4326)
            location = Location.objects.create(**location_data)
            validated_data['location'] = location
            
        if trip_id:
            from trip.models import Trip
            validated_data['associated_trip'] = Trip.objects.get(id=trip_id)
            
        return super().create(validated_data) 