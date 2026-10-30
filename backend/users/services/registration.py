from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from investors.models import InvestorProfile
from startups.models import StartupProfile
from users.exceptions import EmailAlreadyRegistered
from users.services.email_verification import send_verification

User = get_user_model()


@transaction.atomic
def register_user(
    *, email, password, first_name, last_name, company_name, role, legal_form
):
    """Creates an inactive user with an empty profile for the chosen role."""
    try:
        # A savepoint keeps the outer transaction usable after the error
        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                legal_form=legal_form,
                is_active=False,
            )
    except IntegrityError:
        # Another request registered the same email after the serializer check
        raise EmailAlreadyRegistered()

    if role == User.Role.STARTUP:
        StartupProfile.objects.create(user=user, startup_name=company_name)
    else:
        InvestorProfile.objects.create(user=user, investor_name=company_name)

    send_verification(user)
    return user
