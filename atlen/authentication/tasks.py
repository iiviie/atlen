# authentication/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

@shared_task
def send_email_async(subject, html_content, recipient_list):
    try:
        plain_message = strip_tags(html_content)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

@shared_task
def send_otp_email(user_email, otp, verification_type):
    try:
        template_name = (
            'registration_otp_email.html' 
            if verification_type == 'registration' 
            else 'reset_password_otp_email.html'
        )
        
        subject = (
            "Verify Your Email" 
            if verification_type == 'registration' 
            else "Reset Your Password"
        )

        context = {
            'email': user_email,
            'otp': otp,
            'valid_minutes': 10
        }
        
        html_content = render_to_string(template_name, context)
        plain_message = strip_tags(html_content)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_content,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")
        return False