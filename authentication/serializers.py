# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = serializers.DictField(required=False)
    errors = serializers.DictField(required=False)

class UserRegistrationResponseSerializer(BaseResponseSerializer):
    class DataSerializer(serializers.Serializer):
        email = serializers.EmailField()
        is_verified = serializers.BooleanField()

    data = DataSerializer(required=False)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password', 
                 'first_name', 'last_name', 'is_verified')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user and user.is_verified:
            raise ValidationError("User with this email already exists and is verified.")
        return value

    def validate_username(self, value):
        user = User.objects.filter(username=value).first()
        if user and user.is_verified:
            raise ValidationError("User with this username already exists.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return data

    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password', None)
        email = validated_data.get('email')
        
        # Check for existing unverified user
        existing_user = User.objects.filter(email=email, is_verified=False).first()
        if existing_user:
            # Update existing user's details
            for attr, value in validated_data.items():
                if attr == 'password':
                    existing_user.set_password(value)
                else:
                    setattr(existing_user, attr, value)
            existing_user.save()
            return existing_user
        
        # Create new user
        return User.objects.create_user(**validated_data)

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    verification_type = serializers.ChoiceField(
        choices=['registration', 'password_reset']
    )

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise ValidationError("No user found with this email.")
        if not user.otp or not user.otp_created_at:
            raise ValidationError("No active OTP found. Please request a new one.")
        return value

    def validate_otp(self, value):
        if not value.isdigit():
            raise ValidationError("OTP must contain only numbers.")
        return value

class OTPVerificationResponseSerializer(BaseResponseSerializer):
    class DataSerializer(serializers.Serializer):
        refresh = serializers.CharField(required=False)
        access = serializers.CharField(required=False)
        is_verified = serializers.BooleanField(required=False)
        email = serializers.EmailField(required=False)

    data = DataSerializer(required=False)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise ValidationError("No user found with this email.")
        return value

class UserLoginResponseSerializer(BaseResponseSerializer):
    class DataSerializer(serializers.Serializer):
        refresh = serializers.CharField(required=False)
        access = serializers.CharField(required=False)
        email = serializers.EmailField(required=False)
        is_verified = serializers.BooleanField(required=False)

    data = DataSerializer(required=False)
    
    
class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for handling forgot password requests.
    Only requires email field to identify the user.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise ValidationError("No user found with this email.")
        if not user.is_verified:
            raise ValidationError("Email is not verified. Please verify your email first.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for handling password reset after OTP verification.
    Requires email for user identification and new password with confirmation.
    """
    email = serializers.EmailField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise ValidationError("No user found with this email.")
        return value

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return data

class ForgotPasswordResponseSerializer(BaseResponseSerializer):
    """
    Response serializer for forgot password endpoint.
    Extends BaseResponseSerializer to maintain consistent API response structure.
    """
    class DataSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)

    data = DataSerializer(required=False)

class ResetPasswordResponseSerializer(BaseResponseSerializer):
    """
    Response serializer for reset password endpoint.
    Extends BaseResponseSerializer for consistent API response structure.
    """
    pass  # Uses base response structure without additional fields