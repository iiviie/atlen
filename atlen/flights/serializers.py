from rest_framework import serializers

class FlightSearchSerializer(serializers.Serializer):
    fromId = serializers.CharField(required=True)
    toId = serializers.CharField(required=True)
    departDate = serializers.DateField(required=True)
    returnDate = serializers.DateField(required=False, allow_null=True)
    adults = serializers.IntegerField(required=False, default=1, min_value=1)
    children = serializers.CharField(required=False, default="0,17")
    cabinClass = serializers.ChoiceField(
        choices=['ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST'],
        default='ECONOMY'
    )
    currency_code = serializers.CharField(required=False, default='AED')
    sort = serializers.ChoiceField(
        choices=['BEST', 'CHEAPEST', 'FASTEST'],
        default='BEST'
    )
    pageNo = serializers.IntegerField(required=False, default=1, min_value=1)

class DestinationSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=2)