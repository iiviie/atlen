from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class BaseResponseSerializer(serializers.Serializer):
    """
    Base serializer for standardizing API responses.
    All API responses will include success and message fields.
    """
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user registration with password confirmation.
    Validates that passwords match and email is unique.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, data):
        """Ensure passwords match and email is unique."""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({
                'success': False,
                'message': 'Passwords do not match.'
            })
        return data

    def create(self, validated_data):
        """Create and return a new user."""
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    """
    Handles user login data validation.
    Only requires email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class OTPVerificationSerializer(serializers.Serializer):
    """
    Handles OTP verification for both registration and password reset flows.
    verification_type helps distinguish between different OTP purposes.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    verification_type = serializers.ChoiceField(
        choices=['registration', 'password_reset']
    )

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Handles forgot password requests.
    Only requires email field.
    """
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    """
    Handles password reset after OTP verification.
    Requires email for user identification and password confirmation.
    """
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """Ensure new passwords match."""
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError({
                'success': False,
                'message': 'Passwords do not match.'
            })
        return data