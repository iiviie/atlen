# schema.py
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

class AuthenticationSchema:
    """
    Collection of schema configurations for authentication endpoints.
    These schemas provide detailed API documentation.
    """
    
    # Common response examples
    SUCCESS_RESPONSE = OpenApiExample(
        'Success Response',
        value={
            'success': True,
            'message': 'Operation completed successfully',
            'data': {}
        }
    )
    
    ERROR_RESPONSE = OpenApiExample(
        'Error Response',
        value={
            'success': False,
            'message': 'Operation failed',
            'errors': {'field': ['Error description']}
        }
    )
    
    # Registration examples
    REGISTER_REQUEST = OpenApiExample(
        'Registration Request',
        value={
            'email': 'user@example.com',
            'username': 'username',
            'password': 'securepass123',
            'confirm_password': 'securepass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    
    REGISTER_RESPONSE = OpenApiExample(
        'Registration Response',
        value={
            'success': True,
            'message': 'Registration successful. Please verify your email with the OTP.',
            'data': {'email': 'user@example.com'}
        }
    )
    
    # Login examples
    LOGIN_REQUEST = OpenApiExample(
        'Login Request',
        value={
            'email': 'user@example.com',
            'password': 'securepass123'
        }
    )
    
    LOGIN_RESPONSE = OpenApiExample(
        'Login Response',
        value={
            'success': True,
            'message': 'Login successful.',
            'data': {
                'refresh': 'refresh_token',
                'access': 'access_token'
            }
        }
    )
    
    # OTP verification examples
    OTP_VERIFY_REQUEST = OpenApiExample(
        'OTP Verification Request',
        value={
            'email': 'user@example.com',
            'otp': '123456',
            'verification_type': 'registration'
        }
    )
    
    # Password reset examples
    FORGOT_PASSWORD_REQUEST = OpenApiExample(
        'Forgot Password Request',
        value={
            'email': 'user@example.com'
        }
    )
    
    RESET_PASSWORD_REQUEST = OpenApiExample(
        'Reset Password Request',
        value={
            'email': 'user@example.com',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
    )

# Tags for grouping endpoints in documentation
tags = [
    {
        'name': 'Authentication',
        'description': 'Endpoints for user authentication and account management'
    }
]
