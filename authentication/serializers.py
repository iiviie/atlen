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

class AuthDataSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)
    access = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_verified = serializers.BooleanField(required=False)
    is_registered = serializers.BooleanField(required=False)

class AuthenticationResponseSerializer(BaseResponseSerializer):
    data = AuthDataSerializer(required=False)

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        password_pattern = (
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)'
            r'(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )
        if not re.match(password_pattern, value):
            raise serializers.ValidationError(
                'Password must contain at least 8 characters, including uppercase, '
                'lowercase, numbers and special characters.'
            )
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return attrs
    
    def validate_email(self, value):
        return value.lower()

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        email = validated_data.get('email')
        validated_data['email'] = validated_data['email'].lower()
        password = validated_data.get('password')

        try:
            existing_user = User.objects.filter(email=email).first()
            
            if existing_user:
                if existing_user.is_registered:
                    raise serializers.ValidationError({
                        'email': 'User with this email already exists and is registered.'
                    })
                
                # Update existing unregistered user
                for key, value in validated_data.items():
                    if key != 'password':
                        setattr(existing_user, key, value)
                
                if password:
                    existing_user.set_password(password)
                
                existing_user.save()
                return existing_user
            
            # Create new user
            return User.objects.create_user(
                email=email,
                password=password,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                is_active=True,
                is_verified=False,
                is_registered=False
            )
            
        except Exception as e:
            raise serializers.ValidationError({
                'detail': f'Failed to create user: {str(e)}'
            })

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
    reset_token = serializers.CharField(required=True)  

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def validate_password(self, value):
        password_pattern = (
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)'
            r'(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )
        if not re.match(password_pattern, value):
            raise ValidationError(
                'Password must contain at least 8 characters, including uppercase, '
                'lowercase, numbers and special characters.'
            )
        return value
