from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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
