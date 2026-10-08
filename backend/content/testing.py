from django.contrib.auth import get_user_model


def create_admin_user():
    """Superuser for admin tests.

    Works with any user model: the login field is taken from USERNAME_FIELD
    (username for the default User, email for a custom one).
    """
    user_model = get_user_model()
    return user_model.objects.create(
        **{user_model.USERNAME_FIELD: 'admin@example.com'},
        is_staff=True,
        is_superuser=True,
    )
