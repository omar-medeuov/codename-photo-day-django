"""
Views for the todos app.

This module contains viewsets and views for Todo CRUD operations.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from .filters import TodoFilter
from .models import Todo
from .permissions import IsOwner
from .serializers import (
    TodoCreateSerializer,
    TodoSerializer,
    TodoToggleCompleteSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["To-Dos"],
        summary="List all to-dos",
        description="Retrieve a paginated list of to-dos for the authenticated user. "
        "Supports filtering by completed status, priority, and due date range. "
        "Supports searching by title and description. "
        "Supports ordering by created_at, due_date, and priority.",
    ),
    create=extend_schema(
        tags=["To-Dos"],
        summary="Create a new to-do",
        description="Create a new to-do item for the authenticated user.",
    ),
    retrieve=extend_schema(
        tags=["To-Dos"],
        summary="Retrieve a to-do",
        description="Get details of a specific to-do item.",
    ),
    update=extend_schema(
        tags=["To-Dos"],
        summary="Update a to-do",
        description="Update all fields of a specific to-do item.",
    ),
    partial_update=extend_schema(
        tags=["To-Dos"],
        summary="Partially update a to-do",
        description="Update one or more fields of a specific to-do item.",
    ),
    destroy=extend_schema(
        tags=["To-Dos"],
        summary="Delete a to-do",
        description="Delete a specific to-do item.",
    ),
)
class TodoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Todo CRUD operations.

    Provides the following actions:
    - list: GET /api/todos/
    - create: POST /api/todos/
    - retrieve: GET /api/todos/{id}/
    - update: PUT /api/todos/{id}/
    - partial_update: PATCH /api/todos/{id}/
    - destroy: DELETE /api/todos/{id}/
    - toggle_complete: POST /api/todos/{id}/toggle-complete/
    """

    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = TodoFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return todos belonging to the authenticated user."""
        return Todo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == "create":
            return TodoCreateSerializer
        if self.action == "toggle_complete":
            return TodoToggleCompleteSerializer
        return TodoSerializer

    @extend_schema(
        tags=["To-Dos"],
        summary="Toggle to-do completion status",
        description="Toggle the completed status of a specific to-do item.",
        responses={200: TodoToggleCompleteSerializer},
    )
    @action(detail=True, methods=["post"], url_path="toggle-complete")
    def toggle_complete(self, request, pk=None):
        """
        Toggle the completion status of a to-do.

        POST /api/todos/{id}/toggle-complete/
        """
        todo = self.get_object()
        new_status = todo.toggle_complete()
        return Response(
            {
                "id": todo.id,
                "completed": new_status,
                "message": f"To-do marked as {'completed' if new_status else 'incomplete'}.",
            },
            status=status.HTTP_200_OK,
        )
