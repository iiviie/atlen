from django.contrib.auth import get_user_model
from django.conf import settings
import requests as http_requests
import time
from django.utils import timezone

User = get_user_model()

def verify_google_token(access_token):
    try:
        userinfo_response = http_requests.get(
            'https://www.googleapis.com/oauth2/v3/tokeninfo',
            params={'access_token': access_token}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        if userinfo.get('aud') != settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:
            raise ValueError('Invalid audience')
            
        if not userinfo.get('email_verified'):
            raise ValueError('Email not verified with Google')
            
        if float(userinfo.get('exp', 0)) < time.time():
            raise ValueError('Token has expired')

        return userinfo
        
    except Exception as e:
        raise ValueError(f'Token verification failed: {str(e)}')

def create_user(backend, user, response, *args, **kwargs):
    if not user:
        try:
            access_token = response.get('access_token')
            if not access_token:
                return None
                
            userinfo = verify_google_token(access_token)
            
            email = userinfo.get('email')
            if not email:
                return None
                
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(
                    email=email,
                    first_name=userinfo.get('given_name', ''),
                    last_name=userinfo.get('family_name', ''),
                    is_verified=True,
                    is_registered=True,
                    password=None
                )
                
            user.last_login_provider = 'google'
            user.last_token_use = timezone.now()
            user.save()
                
            return {'user': user}
            
        except ValueError:
            return None
            
    return {'user': user}