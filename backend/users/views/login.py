from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed, Throttled
from rest_framework.response import Response
from rest_framework.throttling import BaseThrottle, ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers.login import LoginSerializer, LoginUserSerializer

LOCKOUT_MESSAGE = 'Too many failed login attempts. Try again later.'


def get_lockouts(request):
    """Failed-attempt counters checked on login: (cache key, max attempts, seconds)."""
    # Same normalization as for stored emails, so the key matches the account
    email = str(request.data.get('email', '')).strip()
    email = get_user_model().objects.normalize_email(email)
    client = BaseThrottle().get_ident(request)

    return [
        # Strict limit per client: someone else's attempts can't lock the owner out
        (
            f'login-failed:{email}:{client}',
            settings.LOGIN_MAX_FAILED_ATTEMPTS,
            settings.LOGIN_LOCKOUT_SECONDS,
        ),
        # Higher limit per email from any client: stops brute force via many IPs
        (
            f'login-failed:{email}',
            settings.LOGIN_MAX_FAILED_ATTEMPTS_PER_EMAIL,
            settings.LOGIN_EMAIL_LOCKOUT_SECONDS,
        ),
    ]


class LoginView(APIView):
    # JWT only: no CSRF check from SessionAuthentication, and 401 stays 401
    authentication_classes = [JWTAuthentication]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        lockouts = get_lockouts(request)
        for key, max_attempts, seconds in lockouts:
            if cache.get(key, 0) >= max_attempts:
                raise Throttled(wait=seconds, detail=LOCKOUT_MESSAGE)

        serializer = LoginSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            for key, _, seconds in lockouts:
                register_failed_attempt(key, seconds)
            raise

        # Reset only this client's counter: the per-email one counts other clients too
        client_key = lockouts[0][0]
        cache.delete(client_key)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        if serializer.validated_data['remember']:
            refresh.set_exp(lifetime=settings.LOGIN_REMEMBER_REFRESH_LIFETIME)

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': LoginUserSerializer(user).data,
            }
        )


def register_failed_attempt(key, seconds):
    # The counter lives for the lockout period from the first failure.
    # add() creates it only if it's missing; incr() needs an existing key.
    if not cache.add(key, 1, timeout=seconds):
        try:
            cache.incr(key)
        except ValueError:
            # The key expired or was reset by a successful login in between
            cache.add(key, 1, timeout=seconds)
