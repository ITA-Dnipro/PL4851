from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

SUBJECT = 'Відновлення пароля'


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
    body = render_to_string(
        'users/emails/password_reset.txt',
        {
            'user_name': user.first_name,
            'reset_link': build_reset_link(user, raw_token),
        },
    )
    send_mail(
        subject=SUBJECT,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
