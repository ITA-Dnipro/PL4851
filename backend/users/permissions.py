from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

UNTRUSTED_ORIGIN_MESSAGE = 'Request origin is not allowed.'


class TrustedOrigin(BasePermission):
    """Blocks cross-site browser requests to the endpoints that use the refresh cookie.

    A cross-site HTML form could otherwise log the victim into another account
    or log them out. Browsers always send Origin with a POST and a page can't
    fake it. Requests without it come from non-browser clients (curl, tests),
    which don't have the victim's cookie, so they are let through.
    """

    def has_permission(self, request, view):
        origin = request.headers.get('Origin')
        if origin is None:
            return True

        own_origin = f'{request.scheme}://{request.get_host()}'
        if origin == own_origin or origin in settings.CORS_ALLOWED_ORIGINS:
            return True

        # Raised here so it stays 403: returning False on a view with
        # authentication classes would turn it into a misleading 401
        raise PermissionDenied(UNTRUSTED_ORIGIN_MESSAGE)
