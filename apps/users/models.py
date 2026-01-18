"""
User models for the To-Do application.

This module defines the custom User model extending Django's AbstractUser.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    This model can be extended with additional fields as needed.
    """

    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        """Return string representation of the user."""
        return self.username
