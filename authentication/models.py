from django.db import models
from django.utils import timezone
from accounts.models import User

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
    
    class Meta:
        ordering = ['-created_at']
    
    def mark_as_verified(self):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
    
    def is_valid(self):
        """Check if OTP is still valid (not expired)."""
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() <= expiry_time
