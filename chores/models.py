import uuid

from django.conf import settings
from django.db import models


class Household(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=12, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HouseholdMembership(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='household_membership',
    )
    household = models.ForeignKey(
        Household,
        related_name='members',
        on_delete=models.CASCADE,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_household_membership'),
        ]

    def __str__(self):
        return f'{self.user} -> {self.household}'
