from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove username from required fields

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'