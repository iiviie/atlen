from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, OTPVerificationSerializer
from .models import User
from .utils import send_otp_email, is_otp_valid


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user)  # This will now work with the imported function
            return Response({
                'message': 'Registration successful. Please verify your email with the OTP.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                if user.otp == serializer.validated_data['otp'] and is_otp_valid(user):
                    user.is_verified = True
                    user.otp = None
                    user.otp_created_at = None
                    user.save()
                    
                    # Generate JWT tokens after successful verification
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'message': 'Email verified successfully.',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }, status=status.HTTP_200_OK)
                return Response({
                    'message': 'Invalid OTP or OTP expired.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({
                    'message': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                if not user.is_verified:
                    # Resend OTP if user is not verified
                    send_otp_email(user)
                    return Response({
                        'message': 'Email not verified. New OTP has been sent.',
                        'email': user.email,
                        'requires_verification': True
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Generate JWT tokens for verified user
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }, status=status.HTTP_200_OK)
            return Response({
                'message': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

