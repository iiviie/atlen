# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re


User = get_user_model()

class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = serializers.DictField(required=False)
    errors = serializers.DictField(required=False)

class AuthenticationResponseSerializer(BaseResponseSerializer):
    class DataSerializer(serializers.Serializer):
        refresh = serializers.CharField(required=False)
        access = serializers.CharField(required=False)
        email = serializers.EmailField(required=False)
        is_verified = serializers.BooleanField(required=False)

    data = DataSerializer(required=False)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password', 
                 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({'confirm_password': 'Passwords do not match.'})
            
        # Check if new username is already taken by another user
        username = data.get('username')
        email = data.get('email')
        if username:
            existing_user = User.objects.filter(username=username).exclude(email=email).first()
            if existing_user:
                raise ValidationError({'username': 'This username is already taken.'})
                
        return data
    
    def validate_password(self, value):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise ValidationError('Password must contain at least 8 characters, including uppercase, lowercase, numbers and special characters.')
        return value

    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password', None)
        
        # Try to get existing user by email
        email = validated_data.get('email')
        existing_user = User.objects.filter(email=email).first()
        
        if existing_user and not existing_user.is_verified:
            # Update username if provided
            new_username = validated_data.get('username')
            if new_username and new_username != existing_user.username:
                existing_user.username = new_username
            
            # Update password if provided
            if 'password' in validated_data:
                existing_user.set_password(validated_data['password'])
            
            # Update other fields
            for attr, value in validated_data.items():
                if attr not in ['password', 'email']:  # Don't update email
                    setattr(existing_user, attr, value)
            
            existing_user.save()
            return existing_user
        
        # Create new user
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user



class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    verification_type = serializers.ChoiceField(
        choices=['registration', 'password_reset']
    )

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError({'confirm_password': 'Passwords do not match.'})
        return data
    
    def validate_password(self, value):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise ValidationError('Password must contain at least 8 characters, including uppercase, lowercase, numbers and special characters.')
        return value
    
    
class GoogleAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    
    class Meta:
        fields = ('auth_token',)