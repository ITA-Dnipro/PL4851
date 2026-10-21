import logging

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

from users.emails import send_password_reset_email
from users.metrics import increment_metric
from users.serializers.password_reset import PasswordResetRequestSerializer
from users.services import create_password_reset_token
from users.throttles import PasswordResetEmailThrottle, PasswordResetIPThrottle

logger = logging.getLogger(__name__)
User = get_user_model()

RESPONSE_DETAIL = 'If the email exists, you will receive reset instructions.'


class PasswordResetRequestView(APIView):
    authentication_classes = []
    throttle_classes = [PasswordResetIPThrottle, PasswordResetEmailThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        increment_metric('requests')

        user = User.objects.filter(
            email__iexact=serializer.validated_data['email'],
            is_active=True,
        ).first()

        if user is not None:
            raw_token = create_password_reset_token(user)
            try:
                send_password_reset_email(user, raw_token)
            except Exception:
                logger.exception('Failed to send the password reset email')

        return Response({'detail': RESPONSE_DETAIL})
