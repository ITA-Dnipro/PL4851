from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed, Throttled
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers.login import LoginSerializer, LoginUserSerializer

LOCKOUT_MESSAGE = 'Too many failed login attempts. Try again later.'


def failed_attempts_key(email):
    return f'login-failed:{email.strip().lower()}'


class LoginView(APIView):
    # JWT only: no CSRF check from SessionAuthentication, and 401 stays 401
    authentication_classes = [JWTAuthentication]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        key = failed_attempts_key(str(request.data.get('email', '')))
        if cache.get(key, 0) >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
            raise Throttled(wait=settings.LOGIN_LOCKOUT_SECONDS, detail=LOCKOUT_MESSAGE)

        serializer = LoginSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            register_failed_attempt(key)
            raise

        cache.delete(key)
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


def register_failed_attempt(key):
    # The counter lives for the lockout period from the first failure
    cache.add(key, 0, timeout=settings.LOGIN_LOCKOUT_SECONDS)
    cache.incr(key)
