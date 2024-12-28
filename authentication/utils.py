# utils.py
import random
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import threading

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def is_otp_valid(user):
    """Check if the OTP is still valid (not expired)"""
    if not user.otp_created_at:
        return False
    
    expiry_time = user.otp_created_at + timedelta(minutes=10)
    return timezone.now() <= expiry_time

def send_email_async(subject, html_content, recipient_list):
    """Send email asynchronously"""
    def send_mail_task():
        send_mail(
            subject=subject,
            message=strip_tags(html_content),
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    
    email_thread = threading.Thread(target=send_mail_task)
    email_thread.start()

def send_otp_email(user):
    """Generate OTP, save it to user model, and send it via email"""
    # Generate new OTP
    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    # Prepare email content using template
    context = {
        'user': user,
        'otp': otp
    }
    html_content = render_to_string('otp_email.html', context)
    
    subject = "Email Verification OTP"
    send_email_async(subject, html_content, [user.email])