"""
Tests for the Todo serializers.

This module contains unit tests for Todo serializers.
"""

from django.utils import timezone

from rest_framework.test import APIRequestFactory

import pytest

from apps.todos.models import Todo
from apps.todos.serializers import TodoCreateSerializer, TodoSerializer


@pytest.mark.django_db
class TestTodoSerializer:
    """Test cases for the TodoSerializer."""

    def test_serialize_todo(self, todo):
        """Test serializing a todo instance."""
        serializer = TodoSerializer(todo)
        data = serializer.data

        assert data["id"] == todo.id
        assert data["title"] == todo.title
        assert data["description"] == todo.description
        assert data["completed"] == todo.completed
        assert data["priority"] == todo.priority
        assert data["user"] == todo.user.username

    def test_serialize_todo_with_due_date(self, user):
        """Test serializing a todo with due date."""
        due_date = timezone.now() + timezone.timedelta(days=7)
        todo = Todo.objects.create(
            title="Todo with due date",
            due_date=due_date,
            user=user,
        )
        serializer = TodoSerializer(todo)
        data = serializer.data

        assert data["due_date"] is not None

    def test_read_only_fields(self, todo):
        """Test that read-only fields cannot be set."""
        serializer = TodoSerializer(todo)
        assert "id" in serializer.data
        assert "created_at" in serializer.data
        assert "updated_at" in serializer.data
        assert "user" in serializer.data

    def test_validate_empty_title(self):
        """Test validation rejects empty title."""
        serializer = TodoSerializer(data={"title": "   "})
        assert not serializer.is_valid()
        assert "title" in serializer.errors


@pytest.mark.django_db
class TestTodoCreateSerializer:
    """Test cases for the TodoCreateSerializer."""

    def test_create_todo(self, user):
        """Test creating a todo through serializer."""
        factory = APIRequestFactory()
        request = factory.post("/api/todos/")
        request.user = user

        data = {
            "title": "New Todo",
            "description": "New description",
            "priority": "high",
        }
        serializer = TodoCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        todo = serializer.save()

        assert todo.title == "New Todo"
        assert todo.description == "New description"
        assert todo.priority == "high"
        assert todo.user == user

    def test_create_todo_minimal(self, user):
        """Test creating a todo with minimal data."""
        factory = APIRequestFactory()
        request = factory.post("/api/todos/")
        request.user = user

        data = {"title": "Minimal Todo"}
        serializer = TodoCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        todo = serializer.save()

        assert todo.title == "Minimal Todo"
        assert todo.completed is False
        assert todo.priority == Todo.Priority.MEDIUM

    def test_create_todo_with_all_fields(self, user):
        """Test creating a todo with all fields."""
        factory = APIRequestFactory()
        request = factory.post("/api/todos/")
        request.user = user

        due_date = timezone.now() + timezone.timedelta(days=7)
        data = {
            "title": "Full Todo",
            "description": "Full description",
            "completed": True,
            "priority": "low",
            "due_date": due_date.isoformat(),
        }
        serializer = TodoCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        todo = serializer.save()

        assert todo.title == "Full Todo"
        assert todo.completed is True
        assert todo.priority == "low"

    def test_validate_empty_title(self, user):
        """Test validation rejects empty title."""
        factory = APIRequestFactory()
        request = factory.post("/api/todos/")
        request.user = user

        data = {"title": "   "}
        serializer = TodoCreateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_validate_missing_title(self, user):
        """Test validation rejects missing title."""
        factory = APIRequestFactory()
        request = factory.post("/api/todos/")
        request.user = user

        data = {"description": "No title"}
        serializer = TodoCreateSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_title_is_stripped(self, user):
        """Test that title whitespace is stripped."""
        factory = APIRequestFactory()
        request = factory.post("/api/todos/")
        request.user = user

        data = {"title": "  Padded Title  "}
        serializer = TodoCreateSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        todo = serializer.save()

        assert todo.title == "Padded Title"
