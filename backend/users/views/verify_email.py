from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers.verify_email import VerifyEmailSerializer
from users.services.email_verification import verify_email

VERIFIED_MESSAGE = 'Email verified.'
INVALID_LINK_MESSAGE = 'The verification link is invalid or has expired.'


class VerifyEmailView(APIView):
    # Open to anyone: the signed link proves the email, no token or session needed
    authentication_classes = []

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = verify_email(**serializer.validated_data)
        if user is None:
            return Response(
                {'detail': INVALID_LINK_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'detail': VERIFIED_MESSAGE})
