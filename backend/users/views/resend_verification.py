from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from users.serializers.resend_verification import ResendVerificationSerializer
from users.services.email_verification import resend_verification

RESENT_MESSAGE = 'If the email is waiting for verification, a new link has been sent.'


class ResendVerificationIPThrottle(SimpleRateThrottle):
    scope = 'resend_verification_ip'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class ResendVerificationEmailThrottle(SimpleRateThrottle):
    """Limits letters to one address, whichever client asks for them."""

    scope = 'resend_verification_email'

    def get_cache_key(self, request, view):
        data = request.data if hasattr(request.data, 'get') else {}
        # Upper case, like PostgreSQL compares the email in the iexact lookup,
        # so case variants of one address share the limit
        email = str(data.get('email', '')).strip().upper()
        if not email:
            return None
        return self.cache_format % {'scope': self.scope, 'ident': email}


class ResendVerificationView(APIView):
    # Open to anyone: the user can't log in until the email is verified
    authentication_classes = []
    throttle_classes = [ResendVerificationIPThrottle, ResendVerificationEmailThrottle]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resend_verification(serializer.validated_data['email'])

        # The same answer for any email, so it doesn't tell which ones are registered
        return Response({'detail': RESENT_MESSAGE})
