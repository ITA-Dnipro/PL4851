from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


class RememberMeRefreshToken(RefreshToken):
    """Refresh token for "Remember me" logins.

    The lifetime is set on the class rather than with set_exp() after
    for_user(): for_user() saves the expiry to the blacklist table, and a
    shorter one there would let flushexpiredtokens drop a revoked token.
    """

    lifetime = settings.LOGIN_REMEMBER_REFRESH_LIFETIME
