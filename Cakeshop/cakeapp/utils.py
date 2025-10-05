import random
from django.core.mail import send_mail
from .models import EmailOTP2

def send_otp_email(user):
    otp = str(random.randint(100000, 999999))  # 6-digit OTP
    EmailOTP2.objects.create(user=user, otp_code=otp)

    subject = "Your OTP Code"
    message = f"Hello {user.username},\n\nYour OTP code is {otp}. It will expire in 5 minutes."
    send_mail(subject, message, "noreply@example.com", [user.email])