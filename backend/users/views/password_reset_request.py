import logging

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

from users.emails import send_password_reset_email
from users.metrics import increment_metric
from users.serializers.password_reset import PasswordResetRequestSerializer
from users.services import create_password_reset_token, revoke_previous_reset_tokens
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
            try:
                raw_token = create_password_reset_token(user, revoke_previous=False)
                send_password_reset_email(user, raw_token)
                revoke_previous_reset_tokens(user, raw_token)
            except Exception:
                logger.exception('Failed to create or send the password reset email')

        return Response({'detail': RESPONSE_DETAIL})
