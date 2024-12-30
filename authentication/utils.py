# utils.py
import random
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
import threading
from .models import OTPVerification


def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def is_otp_valid(user):
    """
    Check if user's OTP is still valid (not expired).
    OTP expires after 10 minutes.
    """
    if not user.otp or not user.otp_created_at:
        return False
    
    expiry_time = user.otp_created_at + timedelta(minutes=10)
    return timezone.now() <= expiry_time

class EmailThread(threading.Thread):
    """
    Handles asynchronous email sending to prevent API delays.
    """
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.html_content = html_content
        self.recipient_list = recipient_list
        self.plain_message = strip_tags(html_content)
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            subject=self.subject,
            message=self.plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=self.recipient_list,
            html_message=self.html_content,
            fail_silently=False
        )

def send_otp_email(user, verification_type):
    """Generate OTP, save it to OTPVerification model, and send via email."""
    otp = generate_otp()
    
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
    EmailThread(subject, html_content, [user.email]).start()
