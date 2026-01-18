"""
URL configuration for the todos app.

This module defines URL patterns for Todo API endpoints.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import TodoViewSet

app_name = "todos"

router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = [
    path("", include(router.urls)),
]
