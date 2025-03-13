from django.contrib.auth import get_user_model
from django.conf import settings
import requests as http_requests
import time
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()

def verify_google_token(token, is_id_token=False, client_id=None):
    """
    Verify Google OAuth token
    
    Args:
        token (str): The token to verify
        is_id_token (bool): Whether the token is an ID token (Android) or access token (Web)
        client_id (str): Optional client ID to verify against
    """
    try:
        if is_id_token:
            # For Android ID tokens
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                client_id or settings.GOOGLE_OAUTH2_ANDROID_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            # For Android, we'll verify the audience matches the token's intended audience
            if idinfo['aud'] != idinfo['azp']:
                raise ValueError(f'Token has wrong audience {idinfo["aud"]}, expected {idinfo["azp"]}')
                
            return {
                'email': idinfo['email'],
                'email_verified': idinfo['email_verified'],
                'given_name': idinfo.get('given_name', ''),
                'family_name': idinfo.get('family_name', ''),
                'picture': idinfo.get('picture', ''),
                'aud': idinfo['aud']
            }
        else:
            # Existing access token verification for web
            userinfo_response = http_requests.get(
                'https://www.googleapis.com/oauth2/v3/tokeninfo',
                params={'access_token': token}
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()

            valid_clients = [
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                settings.GOOGLE_OAUTH2_ANDROID_CLIENT_ID
            ]
            
            if userinfo.get('aud') not in valid_clients:
                raise ValueError('Invalid audience')
                
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