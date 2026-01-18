"""
Tests for the Todo model.

This module contains unit tests for the Todo model.
"""

from django.utils import timezone

import pytest

from apps.todos.models import Todo


@pytest.mark.django_db
class TestTodoModel:
    """Test cases for the Todo model."""

    def test_create_todo(self, user):
        """Test creating a basic todo."""
        todo = Todo.objects.create(
            title="Test Todo",
            description="Test description",
            user=user,
        )
        assert todo.title == "Test Todo"
        assert todo.description == "Test description"
        assert todo.completed is False
        assert todo.priority == Todo.Priority.MEDIUM
        assert todo.due_date is None
        assert todo.user == user

    def test_todo_str_representation(self, todo):
        """Test the string representation of a todo."""
        assert str(todo) == "Test Todo"

    def test_todo_default_values(self, user):
        """Test default values for optional fields."""
        todo = Todo.objects.create(
            title="Minimal Todo",
            user=user,
        )
        assert todo.completed is False
        assert todo.priority == Todo.Priority.MEDIUM
        assert todo.description == ""
        assert todo.due_date is None

    def test_todo_with_all_fields(self, user):
        """Test creating a todo with all fields populated."""
        due_date = timezone.now() + timezone.timedelta(days=7)
        todo = Todo.objects.create(
            title="Complete Todo",
            description="Full description",
            completed=True,
            priority=Todo.Priority.HIGH,
            due_date=due_date,
            user=user,
        )
        assert todo.completed is True
        assert todo.priority == Todo.Priority.HIGH
        assert todo.due_date == due_date

    def test_toggle_complete(self, todo):
        """Test toggling the completion status."""
        assert todo.completed is False
        new_status = todo.toggle_complete()
        assert new_status is True
        assert todo.completed is True

        new_status = todo.toggle_complete()
        assert new_status is False
        assert todo.completed is False

    def test_todo_priority_choices(self, user):
        """Test all priority choices."""
        for priority, _ in Todo.Priority.choices:
            todo = Todo.objects.create(
                title=f"Todo with {priority} priority",
                priority=priority,
                user=user,
            )
            assert todo.priority == priority

    def test_todo_ordering(self, user):
        """Test that todos are ordered by created_at descending."""
        todo1 = Todo.objects.create(title="First", user=user)
        todo2 = Todo.objects.create(title="Second", user=user)
        todo3 = Todo.objects.create(title="Third", user=user)

        todos = Todo.objects.filter(user=user)
        assert list(todos) == [todo3, todo2, todo1]

    def test_todo_timestamps(self, todo):
        """Test that timestamps are automatically set."""
        assert todo.created_at is not None
        assert todo.updated_at is not None
        assert todo.created_at <= todo.updated_at

    def test_todo_user_relationship(self, user, todo):
        """Test the relationship between todo and user."""
        assert todo.user == user
        assert todo in user.todos.all()

    def test_cascade_delete(self, user, todo_list):
        """Test that todos are deleted when user is deleted."""
        todo_ids = [t.id for t in todo_list]
        user.delete()
        assert not Todo.objects.filter(id__in=todo_ids).exists()
