from django.db import models
from django.utils import timezone
from accounts.models import User
import secrets

class OTPVerification(models.Model):
    VERIFICATION_TYPES = [
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, null=True, blank=True)  # New field
    reset_token_expires_at = models.DateTimeField(null=True, blank=True)  # New field
    
    class Meta:
        ordering = ['-created_at']
    
    def mark_as_verified(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        if self.verification_type == 'password_reset':
            self.reset_token = secrets.token_urlsafe(32)
            self.reset_token_expires_at = timezone.now() + timezone.timedelta(minutes=15)
        self.save()
    
    def is_valid(self):
        """Check if OTP is still valid (not expired)."""
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() <= expiry_time
        
    def is_reset_token_valid(self):
        """Check if reset token is still valid."""
        if not self.reset_token or not self.reset_token_expires_at:
            return False
        return timezone.now() <= self.reset_token_expires_at