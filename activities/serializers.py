from rest_framework import serializers

class NearbyPlacesSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius = serializers.IntegerField(required=False, default=5000, min_value=1, max_value=50000)
    types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=["restaurant"]
    )

class PlacePhotoSerializer(serializers.Serializer):
    photo_reference = serializers.CharField()
    max_width = serializers.IntegerField(required=False, default=800, min_value=1, max_value=4000)
