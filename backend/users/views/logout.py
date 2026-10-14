from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.cookies import delete_refresh_cookie, get_refresh_cookie


class LogoutView(APIView):
    # The token comes from the cookie, no other authentication is needed
    authentication_classes = []

    def post(self, request):
        refresh = get_refresh_cookie(request)
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                # Expired, forged or already revoked: nothing left to revoke
                pass

        # Always 204 and remove the cookie: JS can't delete an HttpOnly cookie,
        # so this is the only way for the client to get rid of a broken one
        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_refresh_cookie(response)
        return response
