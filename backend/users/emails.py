from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from premailer import transform

from .services import PASSWORD_RESET_TOKEN_LIFETIME

SUBJECT = 'Відновлення пароля'
EXPIRY_MINUTES = int(PASSWORD_RESET_TOKEN_LIFETIME.total_seconds() // 60)


def build_reset_link(user, raw_token):
    query = urlencode(
        {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': raw_token,
        }
    )
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}/reset-password?{query}'


def send_password_reset_email(user, raw_token):
    context = {
        'user_name': user.first_name,
        'reset_link': build_reset_link(user, raw_token),
        'expiry_minutes': EXPIRY_MINUTES,
    }
    message = EmailMultiAlternatives(
        subject=SUBJECT,
        body=render_to_string('users/emails/password_reset.txt', context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=[settings.EMAIL_REPLY_TO] if settings.EMAIL_REPLY_TO else None,
    )
    html = transform(render_to_string('users/emails/password_reset.html', context))
    message.attach_alternative(html, 'text/html')
    message.send()
