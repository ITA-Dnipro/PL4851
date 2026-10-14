from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from users.cookies import get_refresh_cookie
from users.permissions import TrustedOrigin
from users.serializers.refresh import RefreshSerializer

MISSING_COOKIE_MESSAGE = 'Refresh token cookie is missing'


class RefreshView(TokenRefreshView):
    serializer_class = RefreshSerializer
    permission_classes = [TrustedOrigin]

    def post(self, request, *args, **kwargs):
        refresh = get_refresh_cookie(request)
        if not refresh:
            raise InvalidToken(MISSING_COOKIE_MESSAGE)

        # The token comes from the cookie, not from the request body
        serializer = self.get_serializer(data={'refresh': refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        return Response(serializer.validated_data)
