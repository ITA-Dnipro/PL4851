from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

MAX_LENGTH_NAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_ROLE = 20


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        STARTUP = 'startup', 'Стартап'
        INVESTOR = 'investor', 'Інвестор'

    username = None
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=MAX_LENGTH_NAME)
    last_name = models.CharField(max_length=MAX_LENGTH_NAME)
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL, unique=True)
    role = models.CharField(max_length=MAX_LENGTH_ROLE, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=['role'], name='user_role_idx'),
        ]

    def can_have_startup_profile(self):
        return self.role == self.Role.STARTUP

    def can_have_investor_profile(self):
        return self.role == self.Role.INVESTOR

    def __str__(self):
        return f'{self.email} ({self.role})'


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )

    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)

    def is_valid(self):
        return (
            not self.revoked
            and self.used_at is None
            and self.expires_at > timezone.now()
        )

    def mark_as_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])

    def revoke(self):
        self.revoked = True
        self.save(update_fields=['revoked'])

    def __str__(self):
        return f'Password reset token for {self.user.email}'


class PasswordResetMetrics(models.Model):
    requests = models.PositiveBigIntegerField(default=0)
    confirms = models.PositiveBigIntegerField(default=0)
    expired_attempts = models.PositiveBigIntegerField(default=0)
    reused_attempts = models.PositiveBigIntegerField(default=0)
