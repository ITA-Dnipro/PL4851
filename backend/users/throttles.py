from rest_framework.throttling import SimpleRateThrottle


class PasswordResetIPThrottle(SimpleRateThrottle):
    scope = 'password_reset_ip'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class PasswordResetEmailThrottle(SimpleRateThrottle):
    scope = 'password_reset_email'

    def get_cache_key(self, request, view):
        data = request.data
        if not hasattr(data, 'get'):
            return None
        email = str(data.get('email', '')).strip().lower()
        if not email:
            return None
        return self.cache_format % {'scope': self.scope, 'ident': email}
