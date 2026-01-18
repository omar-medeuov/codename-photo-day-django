"""App configuration for the todos app."""

from django.apps import AppConfig


class TodosConfig(AppConfig):
    """Configuration class for the todos application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.todos"
    verbose_name = "To-Dos"
