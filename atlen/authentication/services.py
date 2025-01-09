import random
import threading
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import OTPVerification

class EmailService:
    @staticmethod
    def send_async_email(subject, html_content, recipient_list):
        plain_message = strip_tags(html_content)
        thread = threading.Thread(
            target=send_mail,
            args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list),
            kwargs={'html_message': html_content, 'fail_silently': False}
        )
        thread.start()

class OTPService:
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP."""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    def create_and_send_otp(user, verification_type):
        """Generate OTP, save it, and send via email."""
        otp = OTPService.generate_otp()
        
        # Create new OTP verification record
        OTPVerification.objects.create(
            user=user,
            otp=otp,
            verification_type=verification_type
        )
        
        # Prepare email content
        template_name = (
            'registration_otp_email.html' 
            if verification_type == 'registration' 
            else 'reset_password_otp_email.html'
        )
        
        context = {
            'user': user,
            'otp': otp,
            'valid_minutes': 10
        }
        
        html_content = render_to_string(template_name, context)
        subject = (
            "Verify Your Email" 
            if verification_type == 'registration' 
            else "Reset Your Password"
        )
        
        # Send email asynchronously
        EmailService.send_async_email(subject, html_content, [user.email])

    @staticmethod
    def verify_otp(user, otp_code, verification_type):
        """Verify OTP for given user and type."""
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