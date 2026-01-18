"""
To-Do models for the application.

This module defines the Todo model with all required fields.
"""

from django.conf import settings
from django.db import models


class Todo(models.Model):
    """
    Todo model representing a task item.

    Attributes:
        title: The title of the to-do item (required, max 200 chars)
        description: Optional detailed description
        completed: Boolean status indicating if the task is complete
        priority: Priority level (Low, Medium, High)
        due_date: Optional due date for the task
        created_at: Timestamp when the to-do was created
        updated_at: Timestamp when the to-do was last updated
        user: Foreign key to the user who owns this to-do
    """

    class Priority(models.TextChoices):
        """Priority choices for to-do items."""

        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todos",
    )

    class Meta:
        verbose_name = "to-do"
        verbose_name_plural = "to-dos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "completed"]),
            models.Index(fields=["user", "priority"]),
            models.Index(fields=["user", "due_date"]),
        ]

    def __str__(self):
        """Return string representation of the to-do."""
        return self.title

    def toggle_complete(self):
        """Toggle the completion status of the to-do."""
        self.completed = not self.completed
        self.save(update_fields=["completed", "updated_at"])
        return self.completed
