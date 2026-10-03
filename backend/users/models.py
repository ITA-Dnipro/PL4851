from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH_NAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_ROLE = 20


class User(AbstractUser):
    class Role(models.TextChoices):
        STARTUP = 'startup', 'Стартап'
        INVESTOR = 'investor', 'Інвестор'

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=MAX_LENGTH_NAME)
    last_name = models.CharField(max_length=MAX_LENGTH_NAME)
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL, unique=True)
    role = models.CharField(max_length=MAX_LENGTH_ROLE, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'role']

    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=['role'], name='user_role_idx'),
        ]

    def can_have_startup_profile(self):
        return self.role == self.Role.STARTUP

    def can_have_investor_profile(self):
        return self.role == self.Role.INVESTOR

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.email} ({self.role})'
