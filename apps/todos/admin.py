"""Admin configuration for the todos app."""

from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """Admin configuration for the Todo model."""

    list_display = (
        "title",
        "user",
        "completed",
        "priority",
        "due_date",
        "created_at",
    )
    list_filter = ("completed", "priority", "created_at", "user")
    search_fields = ("title", "description", "user__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("title", "description", "user")}),
        ("Status", {"fields": ("completed", "priority", "due_date")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
