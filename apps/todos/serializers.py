"""
Serializers for the todos app.

This module contains serializers for Todo CRUD operations.
"""

from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    """
    Serializer for Todo model.

    Handles serialization and deserialization of Todo instances.
    """

    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Todo
        fields = (
            "id",
            "title",
            "description",
            "completed",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
            "user",
        )
        read_only_fields = ("id", "created_at", "updated_at", "user")

    def validate_title(self, value):
        """Validate that title is not empty or whitespace only."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace.")
        return value.strip()


class TodoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new Todo."""

    class Meta:
        model = Todo
        fields = (
            "id",
            "title",
            "description",
            "completed",
            "priority",
            "due_date",
        )
        read_only_fields = ("id",)

    def validate_title(self, value):
        """Validate that title is not empty or whitespace only."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace.")
        return value.strip()

    def create(self, validated_data):
        """Create a new Todo associated with the authenticated user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class TodoToggleCompleteSerializer(serializers.Serializer):
    """Serializer for toggle complete response."""

    id = serializers.IntegerField(read_only=True)
    completed = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)
