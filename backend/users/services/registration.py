from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from investors.models import InvestorProfile
from startups.models import StartupProfile
from users.exceptions import EmailAlreadyRegistered
from users.services.email_verification import send_verification

User = get_user_model()


def unverified_accounts(email):
    """Accounts registered with this email that were never verified.

    An inactive user who has logged in before was deactivated by an admin,
    so it is not treated as a pending registration.
    """
    return User.objects.filter(
        email__iexact=email, is_active=False, last_login__isnull=True
    )


def is_email_taken(email):
    """Whether the email belongs to an account a new registration can't replace."""
    return (
        User.objects.filter(email__iexact=email)
        .exclude(pk__in=unverified_accounts(email))
        .exists()
    )


@transaction.atomic
def register_user(
    *, email, password, first_name, last_name, company_name, role, legal_form
):
    """Creates an inactive user with an empty profile for the chosen role.

    A pending unverified registration with the same email is replaced, so an
    expired link or someone else's sign-up doesn't lock the owner out.
    """
    pending = unverified_accounts(email)
    StartupProfile.objects.filter(user__in=pending).delete()
    InvestorProfile.objects.filter(user__in=pending).delete()
    pending.delete()

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
