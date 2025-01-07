from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 
            'first_name', 
            'last_name', 
            'is_verified', 
            'is_registered',
            'last_login',
            'date_joined'
        )
        read_only_fields = fields
