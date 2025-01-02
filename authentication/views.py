from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
import requests
from .serializers import (
    AuthenticationResponseSerializer, UserRegistrationSerializer,
    OTPVerificationSerializer, PasswordResetSerializer, GoogleAuthSerializer
)
from .services import OTPService

User = get_user_model()

class BaseAuthView(APIView):
    permission_classes = [AllowAny]

    def create_response(self, success, message, data=None, errors=None, status_code=status.HTTP_200_OK):
        response_data = {
            'success': success,
            'message': message
        }
        if data:
            response_data['data'] = data
        if errors:
            response_data['errors'] = errors
        return Response(response_data, status=status_code)

class CheckEmailView(BaseAuthView):
    @extend_schema(responses={200: AuthenticationResponseSerializer})
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return self.create_response(
                False, 'Email is required.', 
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return self.create_response(
                True, 'Email not registered.',
                data={'is_registered': False, 'is_verified': False}
            )

        return self.create_response(
            True, 'User found.',
            data={
                'is_registered': user.is_registered,
                'is_verified': user.is_verified,
                'email': user.email
            }
        )

class LoginView(BaseAuthView):
    @extend_schema(responses={200: AuthenticationResponseSerializer})
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if not user:
            return self.create_response(
                False, 'Invalid credentials.',
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_verified or not user.is_registered:
            return self.create_response(
                False, 'Account not fully verified or registered.',
                data={
                    'email': user.email,
                    'is_verified': user.is_verified,
                    'is_registered': user.is_registered
                },
                status_code=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return self.create_response(
            True, 'Login successful.',
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email,
                'is_verified': user.is_verified,
                'is_registered': user.is_registered
            }
        )

class RegisterView(BaseAuthView):
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: AuthenticationResponseSerializer}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            OTPService.create_and_send_otp(user, 'registration')
            
            return self.create_response(
                True, 'Registration successful. Please check your email for OTP verification.',
                data={
                    'email': user.email,
                    'is_verified': user.is_verified,
                    'is_registered': user.is_registered
                },
                status_code=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            return self.create_response(
                False, 'Validation failed',
                errors=e.detail if hasattr(e, 'detail') else str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            import traceback
            print(f"Registration error: {str(e)}")
            print(traceback.format_exc())
            
            return self.create_response(
                False, 'Registration failed',
                errors={'detail': str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )

class VerifyOTPView(BaseAuthView):
    @extend_schema(
        request=OTPVerificationSerializer,
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return self.create_response(
                False, 'Invalid data.',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            is_valid, message = OTPService.verify_otp(
                user, 
                serializer.validated_data['otp'],
                serializer.validated_data['verification_type']
            )

            if not is_valid:
                return self.create_response(
                    False, message,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            if serializer.validated_data['verification_type'] == 'registration':
                user.is_verified = True
                user.is_registered = True
                user.save()
                refresh = RefreshToken.for_user(user)
                return self.create_response(
                    True, 'Email verified successfully.',
                    data={
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'email': user.email,
                        'is_verified': user.is_verified,
                        'is_registered': user.is_registered
                    }
                )
            
            return self.create_response(True, message)

        except User.DoesNotExist:
            return self.create_response(
                False, 'User not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )

class ForgotPasswordView(BaseAuthView):
    @extend_schema(responses={200: AuthenticationResponseSerializer})
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                return self.create_response(
                    False, 'Please verify your email first.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            OTPService.create_and_send_otp(user, 'password_reset')
            return self.create_response(
                True, 'Password reset OTP has been sent to your email.',
                data={'email': user.email}
            )
            
        except User.DoesNotExist:
            return self.create_response(
                False, 'No user found with this email.',
                status_code=status.HTTP_404_NOT_FOUND
            )

class ResetPasswordView(BaseAuthView):
    @extend_schema(
        request=PasswordResetSerializer,
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        """Handle password reset."""
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return self.create_response(
                False, 'Invalid data.',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            latest_verified_otp = user.otpverification_set.filter(
                verification_type='password_reset',
                is_verified=True
            ).latest('verified_at')
            
            if not latest_verified_otp:
                return self.create_response(
                    False, 'Please verify your OTP first.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            latest_verified_otp.delete()
            
            return self.create_response(True, 'Password reset successful.')
            
        except User.DoesNotExist:
            return self.create_response(
                False, 'User not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.create_response(
                False, str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
         
            
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=GoogleAuthSerializer,
        responses={200: AuthenticationResponseSerializer}
    )
    def post(self, request):
        token = request.data.get('auth_token')
        if not token:
            return Response({
                'success': False,
                'message': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Google OAuth verification
            userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
            google_response = requests.get(
                userinfo_url,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if not google_response.ok:
                return Response({
                    'success': False,
                    'message': 'Failed to verify token with Google',
                    'errors': google_response.text
                }, status=status.HTTP_400_BAD_REQUEST)
            
            userinfo = google_response.json()
            email = userinfo.get('email')
            
            if not email:
                return Response({
                    'success': False,
                    'message': 'Email not found in Google response'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            user = User.objects.filter(email=email).first()
            
            if not user:
                # Create new user
                username = email.split('@')[0]
                user = User.objects.create(
                    email=email,
                    username=username,
                    first_name=userinfo.get('given_name', ''),
                    last_name=userinfo.get('family_name', ''),
                    is_verified=True  # Google-authenticated users are verified
                )
            elif not user.is_verified:
                # Update existing unverified user
                user.is_verified = True
                user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Google login successful',
                'data': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'email': user.email,
                    'is_verified': user.is_verified,
                    'user_info': userinfo  # For testing purposes
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Authentication failed: {str(e)}',
                'error_details': str(e)  # For debugging
            }, status=status.HTTP_400_BAD_REQUEST)           