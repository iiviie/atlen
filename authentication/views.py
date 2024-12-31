# authentication/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import (
    UserRegistrationSerializer,
    OTPVerificationSerializer,
    PasswordResetSerializer,
    AuthenticationResponseSerializer
)
from .services import OTPService

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if not user:
            return Response({
                'success': False,
                'message': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:
            OTPService.create_and_send_otp(user, 'registration')
            return Response({
                'success': False,
                'message': 'Email not verified. New OTP sent.',
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


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: AuthenticationResponseSerializer}
    )
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        
        # Check if user exists
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.is_verified:
                return Response({
                    'success': False,
                    'message': 'Account already exists and is verified. Please login instead.',
                    'data': {
                        'email': existing_user.email,
                        'is_verified': existing_user.is_verified
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Send new OTP only for unverified users
                OTPService.create_and_send_otp(existing_user, 'registration')
                return Response({
                    'success': True,
                    'message': 'Account exists but is not verified. New verification code sent.',
                    'data': {
                        'email': existing_user.email,
                        'is_verified': existing_user.is_verified
                    }
                }, status=status.HTTP_201_CREATED)

        # For new user registration
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Registration failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            OTPService.create_and_send_otp(user, 'registration')
            
            return Response({
                'success': True,
                'message': 'Registration successful. Please verify your email.',
                'data': {
                    'email': user.email,
                    'is_verified': user.is_verified
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Registration failed.',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=OTPVerificationSerializer,
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid data.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            is_valid, message = OTPService.verify_otp(
                user, 
                serializer.validated_data['otp'],
                serializer.validated_data['verification_type']
            )

            if not is_valid:
                return Response({
                    'success': False,
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)

            if serializer.validated_data['verification_type'] == 'registration':
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
            
            return Response({
                'success': True,
                'message': message
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                return Response({
                    'success': False,
                    'message': 'Please verify your email first.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            OTPService.create_and_send_otp(user, 'password_reset')
            return Response({
                'success': True,
                'message': 'Password reset OTP has been sent to your email.',
                'data': {'email': user.email}
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No user found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetSerializer,
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid data.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            # Check for verified OTP first
            latest_verified_otp = user.otpverification_set.filter(
                verification_type='password_reset',
                is_verified=True
            ).latest('verified_at')
            
            if not latest_verified_otp:
                return Response({
                    'success': False,
                    'message': 'Please verify your OTP first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Invalidate the used OTP
            latest_verified_otp.delete()
            
            return Response({
                'success': True,
                'message': 'Password reset successful.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)