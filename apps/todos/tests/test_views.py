"""
Tests for the Todo views.

This module contains integration tests for Todo API endpoints.
"""

from django.urls import reverse
from django.utils import timezone

from rest_framework import status

import pytest

from apps.todos.models import Todo


@pytest.mark.django_db
class TestTodoListCreate:
    """Test cases for listing and creating todos."""

    def test_list_todos(self, authenticated_client, todo_list):
        """Test listing todos returns paginated results."""
        url = reverse("todos:todo-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 5

    def test_list_todos_unauthenticated(self, api_client):
        """Test listing todos requires authentication."""
        url = reverse("todos:todo-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_only_own_todos(self, authenticated_client, todo, other_user_todo):
        """Test users only see their own todos."""
        url = reverse("todos:todo-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == todo.id

    def test_create_todo(self, authenticated_client):
        """Test creating a new todo."""
        url = reverse("todos:todo-list")
        data = {
            "title": "New Todo",
            "description": "Test description",
            "priority": "high",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Todo"
        assert Todo.objects.filter(title="New Todo").exists()

    def test_create_todo_minimal(self, authenticated_client):
        """Test creating a todo with minimal data."""
        url = reverse("todos:todo-list")
        data = {"title": "Minimal Todo"}
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Minimal Todo"

    def test_create_todo_invalid(self, authenticated_client):
        """Test creating a todo with invalid data."""
        url = reverse("todos:todo-list")
        data = {"description": "No title"}
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTodoRetrieveUpdateDestroy:
    """Test cases for retrieving, updating, and deleting todos."""

    def test_retrieve_todo(self, authenticated_client, todo):
        """Test retrieving a single todo."""
        url = reverse("todos:todo-detail", kwargs={"pk": todo.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == todo.id
        assert response.data["title"] == todo.title

    def test_retrieve_other_user_todo(self, authenticated_client, other_user_todo):
        """Test users cannot retrieve other users' todos."""
        url = reverse("todos:todo-detail", kwargs={"pk": other_user_todo.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_todo(self, authenticated_client, todo):
        """Test updating a todo with PUT."""
        url = reverse("todos:todo-detail", kwargs={"pk": todo.id})
        data = {
            "title": "Updated Todo",
            "description": "Updated description",
            "completed": True,
            "priority": "high",
        }
        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        todo.refresh_from_db()
        assert todo.title == "Updated Todo"
        assert todo.completed is True

    def test_partial_update_todo(self, authenticated_client, todo):
        """Test partially updating a todo with PATCH."""
        url = reverse("todos:todo-detail", kwargs={"pk": todo.id})
        data = {"completed": True}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        todo.refresh_from_db()
        assert todo.completed is True
        assert todo.title == "Test Todo"  # Unchanged

    def test_update_other_user_todo(self, authenticated_client, other_user_todo):
        """Test users cannot update other users' todos."""
        url = reverse("todos:todo-detail", kwargs={"pk": other_user_todo.id})
        data = {"title": "Hacked Todo"}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_todo(self, authenticated_client, todo):
        """Test deleting a todo."""
        url = reverse("todos:todo-detail", kwargs={"pk": todo.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Todo.objects.filter(id=todo.id).exists()

    def test_delete_other_user_todo(self, authenticated_client, other_user_todo):
        """Test users cannot delete other users' todos."""
        url = reverse("todos:todo-detail", kwargs={"pk": other_user_todo.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Todo.objects.filter(id=other_user_todo.id).exists()


@pytest.mark.django_db
class TestTodoToggleComplete:
    """Test cases for the toggle complete action."""

    def test_toggle_complete_to_true(self, authenticated_client, todo):
        """Test toggling incomplete to complete."""
        assert todo.completed is False
        url = reverse("todos:todo-toggle-complete", kwargs={"pk": todo.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["completed"] is True
        todo.refresh_from_db()
        assert todo.completed is True

    def test_toggle_complete_to_false(self, authenticated_client, user):
        """Test toggling complete to incomplete."""
        todo = Todo.objects.create(
            title="Completed Todo",
            completed=True,
            user=user,
        )
        url = reverse("todos:todo-toggle-complete", kwargs={"pk": todo.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["completed"] is False
        todo.refresh_from_db()
        assert todo.completed is False

    def test_toggle_complete_other_user_todo(
        self, authenticated_client, other_user_todo
    ):
        """Test users cannot toggle other users' todos."""
        url = reverse("todos:todo-toggle-complete", kwargs={"pk": other_user_todo.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTodoFiltering:
    """Test cases for todo filtering."""

    def test_filter_by_completed(self, authenticated_client, todo_list):
        """Test filtering todos by completed status."""
        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"completed": "true"})

        assert response.status_code == status.HTTP_200_OK
        for todo in response.data["results"]:
            assert todo["completed"] is True

    def test_filter_by_priority(self, authenticated_client, todo_list):
        """Test filtering todos by priority."""
        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"priority": "high"})

        assert response.status_code == status.HTTP_200_OK
        for todo in response.data["results"]:
            assert todo["priority"] == "high"

    def test_filter_by_due_date_range(self, authenticated_client, user):
        """Test filtering todos by due date range."""
        now = timezone.now()
        Todo.objects.create(
            title="Past Due",
            due_date=now - timezone.timedelta(days=7),
            user=user,
        )
        future_todo = Todo.objects.create(
            title="Future Due",
            due_date=now + timezone.timedelta(days=7),
            user=user,
        )

        url = reverse("todos:todo-list")
        response = authenticated_client.get(
            url,
            {
                "due_date_from": now.isoformat(),
                "due_date_to": (now + timezone.timedelta(days=14)).isoformat(),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == future_todo.id


@pytest.mark.django_db
class TestTodoSearch:
    """Test cases for todo search."""

    def test_search_by_title(self, authenticated_client, user):
        """Test searching todos by title."""
        Todo.objects.create(title="Important Meeting", user=user)
        Todo.objects.create(title="Buy groceries", user=user)

        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"search": "Meeting"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert "Meeting" in response.data["results"][0]["title"]

    def test_search_by_description(self, authenticated_client, user):
        """Test searching todos by description."""
        Todo.objects.create(
            title="Task 1",
            description="Contains keyword important here",
            user=user,
        )
        Todo.objects.create(
            title="Task 2",
            description="Nothing special",
            user=user,
        )

        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"search": "important"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestTodoOrdering:
    """Test cases for todo ordering."""

    def test_order_by_created_at(self, authenticated_client, todo_list):
        """Test ordering todos by created_at."""
        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"ordering": "created_at"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        for i in range(len(results) - 1):
            assert results[i]["created_at"] <= results[i + 1]["created_at"]

    def test_order_by_priority(self, authenticated_client, todo_list):
        """Test ordering todos by priority."""
        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"ordering": "priority"})

        assert response.status_code == status.HTTP_200_OK
        # Just verify the request succeeds

    def test_order_by_due_date(self, authenticated_client, user):
        """Test ordering todos by due_date."""
        now = timezone.now()
        Todo.objects.create(
            title="Later",
            due_date=now + timezone.timedelta(days=10),
            user=user,
        )
        Todo.objects.create(
            title="Sooner",
            due_date=now + timezone.timedelta(days=1),
            user=user,
        )

        url = reverse("todos:todo-list")
        response = authenticated_client.get(url, {"ordering": "due_date"})

        assert response.status_code == status.HTTP_200_OK
