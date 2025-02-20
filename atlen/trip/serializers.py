from rest_framework import serializers
from django.contrib.auth import get_user_model
from trip.models import Location, Trip, ChecklistItem, Itinerary, ItineraryItem, ItineraryDay

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    point_latitude = serializers.FloatField(source='point.y', read_only=True)
    point_longitude = serializers.FloatField(source='point.x', read_only=True)
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'city', 'country', 
                 'latitude', 'longitude', 'point_latitude', 'point_longitude']
        read_only_fields = ['id']

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        from django.contrib.gis.geos import Point
        validated_data['point'] = Point(longitude, latitude, srid=4326)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'latitude' in validated_data and 'longitude' in validated_data:
            latitude = validated_data.pop('latitude')
            longitude = validated_data.pop('longitude')
            from django.contrib.gis.geos import Point
            validated_data['point'] = Point(longitude, latitude, srid=4326)
        return super().update(instance, validated_data)

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']

class TripListSerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField()
    creator = UserBasicSerializer(read_only=True)
    companion_count = serializers.IntegerField(source='companions.count', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'start_date', 'end_date',
            'location', 'status', 'creator', 'companion_count',
            'image', 'image_url'
        ]
        read_only_fields = ['id', 'creator', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

class TripDetailSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    creator = UserBasicSerializer(read_only=True)
    companions = UserBasicSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'start_date', 'end_date',
            'creator', 'location', 'companions', 'status',
            'created_at', 'updated_at', 'image', 'image_url'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at', 'image_url']
        extra_kwargs = {
            'title': {'required': True},
            'start_date': {'required': True},
            'end_date': {'required': True},
            'location': {'required': True},
            'status': {'required': False},
        }

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        latitude = location_data.pop('latitude')
        longitude = location_data.pop('longitude')
        from django.contrib.gis.geos import Point
        location_data['point'] = Point(longitude, latitude, srid=4326)
        location = Location.objects.create(**location_data)
        return Trip.objects.create(location=location, **validated_data)

    def update(self, instance, validated_data):
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            if 'latitude' in location_data and 'longitude' in location_data:
                latitude = location_data.pop('latitude')
                longitude = location_data.pop('longitude')
                from django.contrib.gis.geos import Point
                location_data['point'] = Point(longitude, latitude, srid=4326)
            Location.objects.filter(id=instance.location.id).update(**location_data)
        return super().update(instance, validated_data)

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'item', 'is_checked', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ItineraryItemSerializer(serializers.ModelSerializer):
    activity_details = serializers.SerializerMethodField()

    class Meta:
        model = ItineraryItem
        fields = [
            'id', 'activity', 'custom_activity', 'time',
            'duration', 'notes', 'activity_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_activity_details(self, obj):
        if obj.activity:
            return {
                'name': obj.activity.name,
                'type': obj.activity.get_activity_type_display(),
                'location': obj.activity.location.name,
                'rating': obj.activity.rating
            }
        return None

class ItineraryDaySerializer(serializers.ModelSerializer):
    activities = ItineraryItemSerializer(many=True, read_only=True)

    class Meta:
        model = ItineraryDay
        fields = ['id', 'date', 'notes', 'activities', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ItinerarySerializer(serializers.ModelSerializer):
    days = ItineraryDaySerializer(many=True, read_only=True)

    class Meta:
        model = Itinerary
        fields = ['id', 'title', 'days', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TripStatsSerializer(serializers.Serializer):
    total_trips = serializers.IntegerField()
    completed_trips = serializers.IntegerField()
    planned_trips = serializers.IntegerField()
    ongoing_trips = serializers.IntegerField()
    unique_destinations = serializers.IntegerField()
    total_companions = serializers.IntegerField()
    most_visited_city = serializers.CharField()