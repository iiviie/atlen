# views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    OTPVerificationSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, BaseResponseSerializer
)
from .utils import send_otp_email, is_otp_valid
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: BaseResponseSerializer},
        description='Register a new user and send verification OTP.',
        tags=['Authentication']
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user, 'registration')
            return Response({
                'success': True,
                'message': 'Registration successful. Please verify your email with the OTP.',
                'data': {'email': user.email}
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Registration failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=UserLoginSerializer,
        responses={200: BaseResponseSerializer},
        description='Authenticate user and return tokens.',
        tags=['Authentication']
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            if not user:
                return Response({
                    'success': False,
                    'message': 'Invalid credentials.'
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_verified:
                send_otp_email(user, 'registration')
                return Response({
                    'success': False,
                    'message': 'Email not verified. New OTP has been sent.',
                    'data': {'email': user.email}
                }, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'message': 'Login successful.',
                'data': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'Invalid data.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=OTPVerificationSerializer,
        responses={200: BaseResponseSerializer},
        description='Verify OTP for registration or password reset.',
        tags=['Authentication']
    )
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                verification_type = serializer.validated_data['verification_type']
                
                if not is_otp_valid(user):
                    return Response({
                        'success': False,
                        'message': 'OTP has expired.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if user.otp != serializer.validated_data['otp']:
                    return Response({
                        'success': False,
                        'message': 'Invalid OTP.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Clear OTP after successful verification
                user.otp = None
                user.otp_created_at = None
                
                if verification_type == 'registration':
                    user.is_verified = True
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'success': True,
                        'message': 'Email verified successfully.',
                        'data': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token)
                        }
                    }, status=status.HTTP_200_OK)
                else:  # password_reset
                    user.save()
                    return Response({
                        'success': True,
                        'message': 'OTP verified. You can now reset your password.',
                        'data': {'email': user.email}
                    }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'message': 'Invalid data.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: BaseResponseSerializer},
        description='Send password reset OTP to user email.',
        tags=['Authentication']
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                send_otp_email(user, 'password_reset')
                return Response({
                    'success': True,
                    'message': 'Password reset OTP has been sent to your email.',
                    'data': {'email': user.email}
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'message': 'Invalid data.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: BaseResponseSerializer},
        description='Reset user password after OTP verification.',
        tags=['Authentication']
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Password reset successful. You can now login with your new password.'
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'message': 'Invalid data.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)