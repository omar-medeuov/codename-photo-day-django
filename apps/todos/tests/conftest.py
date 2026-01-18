"""
Pytest fixtures for the todos app tests.

This module contains shared fixtures used across test modules.
"""

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.todos.models import Todo

User = get_user_model()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def other_user(db):
    """Create and return another test user."""
    return User.objects.create_user(
        username="otheruser",
        email="otheruser@example.com",
        password="otherpass123",
    )


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def todo(user):
    """Create and return a test todo."""
    return Todo.objects.create(
        title="Test Todo",
        description="Test description",
        priority=Todo.Priority.MEDIUM,
        user=user,
    )


@pytest.fixture
def todo_list(user):
    """Create and return a list of test todos."""
    todos = []
    for i in range(5):
        todos.append(
            Todo.objects.create(
                title=f"Todo {i}",
                description=f"Description {i}",
                priority=Todo.Priority.choices[i % 3][0],
                completed=i % 2 == 0,
                user=user,
            )
        )
    return todos


@pytest.fixture
def other_user_todo(other_user):
    """Create and return a todo belonging to another user."""
    return Todo.objects.create(
        title="Other User Todo",
        description="Other user's description",
        priority=Todo.Priority.HIGH,
        user=other_user,
    )
