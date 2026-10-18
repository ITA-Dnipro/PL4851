from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class RefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # SimpleJWT looks the user up with get() and doesn't catch
        # DoesNotExist, so a deleted user's token would end in a 500
        try:
            return super().validate(attrs)
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed(
                self.error_messages['no_active_account'], 'no_active_account'
            )
