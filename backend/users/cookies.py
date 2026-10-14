from django.conf import settings


def set_refresh_cookie(response, refresh, remember):
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        str(refresh),
        # Without "Remember me" it's a session cookie, gone when the browser closes
        max_age=refresh.lifetime if remember else None,
        path=settings.REFRESH_COOKIE_PATH,
        secure=settings.REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def delete_refresh_cookie(response):
    # The path must match the one the cookie was set with, or it stays
    response.delete_cookie(
        settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def get_refresh_cookie(request):
    return request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
