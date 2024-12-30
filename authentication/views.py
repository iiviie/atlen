# views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import *
from .utils import send_otp_email, is_otp_valid
from django.contrib.auth import get_user_model
from .models import OTPVerification
from django.utils import timezone


User = get_user_model()

class RegisterView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationResponseSerializer},
        description='Register a new user or update existing unverified user and send verification OTP.',
        tags=['Authentication']
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            # Check if user exists but is unverified
            existing_user = User.objects.filter(email=request.data.get('email')).first()
            if existing_user and not existing_user.is_verified:
                # Send new OTP
                send_otp_email(existing_user, 'registration')
                return Response({
                    'success': False,
                    'message': 'User exists but is not verified. New OTP has been sent.',
                    'data': {
                        'email': existing_user.email,
                        'is_verified': existing_user.is_verified
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Other validation errors
            return Response({
                'success': False,
                'message': 'Registration failed.',
                'errors': serializer.errors,
                'data': {
                    'is_verified': False
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            # Clear any existing OTP before sending new one
            user.otp = None
            user.otp_created_at = None
            user.save()
            
            # Send new OTP
            send_otp_email(user, 'registration')
            
            return Response({
                'success': True,
                'message': 'Registration successful. Please verify your email with the OTP.',
                'data': {
                    'email': user.email,
                    'is_verified': user.is_verified
                }
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Registration failed.',
                'errors': str(e),
                'data': {
                    'is_verified': False
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginResponseSerializer},
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
                    'message': 'Invalid credentials.',
                    'data': {
                        'is_verified': False
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_verified:
                send_otp_email(user, 'registration')
                return Response({
                    'success': False,
                    'message': 'Email not verified. New OTP has been sent.',
                    'data': {
                        'email': user.email,
                        'is_verified': user.is_verified
                    }
                }, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'message': 'Login successful.',
                'data': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'email': user.email,
                    'is_verified': user.is_verified
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'Invalid data.',
            'errors': serializer.errors,
            'data': {
                'is_verified': False
            }
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
                
                # Get latest unverified OTP for the user and type
                latest_otp = OTPVerification.objects.filter(
                    user=user,
                    verification_type=verification_type,
                    is_verified=False
                ).order_by('-created_at').first()
                
                if not latest_otp:
                    return Response({
                        'success': False,
                        'message': 'No active OTP found.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not latest_otp.is_valid():
                    return Response({
                        'success': False,
                        'message': 'OTP has expired.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if latest_otp.otp != serializer.validated_data['otp']:
                    return Response({
                        'success': False,
                        'message': 'Invalid OTP.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark OTP as verified
                latest_otp.mark_as_verified()
                
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
                
                # Check for verified OTP
                latest_otp = OTPVerification.objects.filter(
                    user=user,
                    verification_type='password_reset',
                    is_verified=True,
                    verified_at__gte=timezone.now() - timezone.timedelta(minutes=30)
                ).first()
                
                if not latest_otp:
                    return Response({
                        'success': False,
                        'message': 'Please verify your OTP before resetting password.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # Invalidate the OTP after password reset
                latest_otp.delete()
                
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
