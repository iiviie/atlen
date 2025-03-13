from rest_framework import serializers
from datetime import date


class HotelSearchSerializer(serializers.Serializer):
    dest_id = serializers.CharField(max_length=50)
    adults = serializers.IntegerField(min_value=1)
    children_age = serializers.CharField(default="0")
    arrival_date = serializers.DateField()
    departure_date = serializers.DateField()

    def validate(self, data):
        """Custom validation for date constraints."""
        arrival_date = data["arrival_date"]
        departure_date = data["departure_date"]

        if arrival_date < date.today():
            raise serializers.ValidationError("Arrival date must be in the future.")

        if departure_date <= arrival_date:
            raise serializers.ValidationError(
                "Departure date must be after arrival date."
            )

        return data
