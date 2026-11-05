from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from users.serializers.register import RegisterSerializer
from users.services.registration import register_user

VERIFICATION_SENT_MESSAGE = 'Verification email sent.'


class RegisterView(APIView):
    # Open to anyone: no token or session is needed to create an account
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)

        return Response(
            {
                'id': user.pk,
                'email': user.email,
                'detail': VERIFICATION_SENT_MESSAGE,
            },
            status=status.HTTP_201_CREATED,
        )
