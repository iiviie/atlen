# authentication/services.py
import random
from django.template.loader import render_to_string
from django.conf import settings
from .models import OTPVerification
from .tasks import send_email_async, send_otp_email

class EmailService:
    @staticmethod
    def send_async_email(subject, html_content, recipient_list):
        return send_email_async.delay(subject, html_content, recipient_list)

class OTPService:
    @staticmethod
    def generate_otp():
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    def create_and_send_otp(user, verification_type):
        otp = OTPService.generate_otp()
        
        OTPVerification.objects.create(
            user=user,
            otp=otp,
            verification_type=verification_type
        )
        
        # Send OTP email using Celery task
        send_otp_email.delay(user.email, otp, verification_type)

    @staticmethod
    def verify_otp(user, otp_code, verification_type):
        latest_otp = OTPVerification.objects.filter(
            user=user,
            verification_type=verification_type,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not latest_otp:
            return False, "No active OTP found."
            
        if not latest_otp.is_valid():
            return False, "OTP has expired."
            
        if latest_otp.otp != otp_code:
            return False, "Invalid OTP."
            
        latest_otp.mark_as_verified()
        return True, "OTP verified successfully."