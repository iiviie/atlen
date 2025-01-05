from django.contrib.auth import get_user_model

User = get_user_model()

def create_user(backend, user, response, *args, **kwargs):
    if not user:
        email = response.get('email')
        if not email:
            return None
            
        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user:
            # Create new user
            user = User.objects.create_user(
                email=email,
                first_name=response.get('given_name', ''),
                last_name=response.get('family_name', ''),
                is_verified=True,
                is_registered=True,
                password=None  
            )
    return {'user': user}